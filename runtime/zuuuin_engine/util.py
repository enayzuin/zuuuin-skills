"""Small deterministic helpers shared by the eight engine operations."""
from pathlib import Path
import configparser
import hashlib
import json
import os
import re
import selectors
import subprocess
import time
import uuid
from .state import ControlError, canonical, now


def stable_id(kind, key):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "zuuuin:" + kind + ":" + key))


def response(operation, status, **data):
    stamp = now()
    result = {"schema_version":"1.0", "type":"operation_result", "id":str(uuid.uuid4()), "created_at":stamp, "updated_at":stamp, "revision":1, "operation":operation, "status":status, "source":"agent_or_supplied_observation", **data}
    reasons = {}
    def visit(value, path):
        if value is None:
            reasons[path] = "Not observed or not supplied; no measurement inferred. See evidence and coverage."
        elif isinstance(value, dict):
            for key, item in value.items(): visit(item, path + "." + key if path else key)
        elif isinstance(value, list):
            for i, item in enumerate(value): visit(item, path + "." + str(i))
    visit(result, "")
    if reasons: result["unknown_reasons"] = reasons
    return result


def contained(path, root):
    path, root = Path(path).resolve(strict=False), Path(root).resolve(strict=False)
    return path == root or root in path.parents


PATTERNS = {
    "private_home_path": re.compile(r"/Users/[A-Za-z0-9_.-]+(?:/[^\s\"']*)?"),
    "synthetic_private_marker": re.compile(r"ZUUUIN_PRIVATE_CANARY_[A-Za-z0-9]{4,}"),
    "credential_pattern": re.compile(r"(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16})"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}


def scan_value(value, private_identifiers=()):
    """Return finding kinds and line numbers, never matched sensitive values."""
    findings = []
    def scan(item, slot="value"):
        if isinstance(item, str):
            for kind, pattern in PATTERNS.items():
                for match in pattern.finditer(item):
                    findings.append({"kind":kind,"location":slot+":line:"+str(item.count("\n",0,match.start())+1)})
            for needle in private_identifiers:
                if isinstance(needle,str) and needle and needle in item:
                    findings.append({"kind":"private_identifier","location":slot})
        elif isinstance(item, dict):
            for i,(key,child) in enumerate(item.items()):
                scan(key,slot+f".key[{i}]");scan(child,slot+f".field[{i}]")
        elif isinstance(item,list):
            for i,child in enumerate(item):scan(child,slot+f"[{i}]")
    scan(value)
    return findings


GIT_OUTPUT_LIMIT = 20_000_000
GIT_TIMEOUT_SECONDS = 15


def _walk_error(error):
    raise ControlError("Package or Git metadata could not be fully enumerated") from error


def _git_preflight(root):
    """Accept a deliberately small Git/config subset without asking Git to parse it."""
    root = Path(root).absolute()
    gitdir = root / ".git"
    if root.is_symlink() or not root.is_dir() or gitdir.is_symlink() or not gitdir.is_dir():
        raise ControlError("Git requires a real package root and in-place .git directory; gitdir files/worktrees are not audited")
    for base, dirs, names in os.walk(gitdir, followlinks=False, onerror=_walk_error):
        for name in dirs + names:
            if (Path(base) / name).is_symlink():
                raise ControlError("Symlinked Git metadata is not audited")
    for name in ("commondir", "shallow", "config.worktree", "config.lock", "info/grafts", "objects/info/alternates", "objects/info/http-alternates", "refs/replace"):
        if (gitdir / name).exists():
            raise ControlError("External, partial, replaced or changing Git metadata is not audited")
    config = gitdir / "config"
    try:
        raw = config.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ControlError("Git configuration could not be inspected") from exc
    if len(raw) > 65_536 or "\\" in raw or "\x00" in raw:
        raise ControlError("Escaped, continued or oversized Git configuration is not audited")
    # Git's full grammar differs from INI. Reject forms outside this shared subset,
    # rather than assuming ConfigParser's treatment is the one Git will use.
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", ";")):
            continue
        if stripped.startswith("["):
            if not re.fullmatch(r'\[(?:core|user|remote "[A-Za-z0-9._/-]+"|branch "[A-Za-z0-9._/-]+")\]', stripped, re.I):
                raise ControlError("Unsupported Git section (including includes, filters and callbacks)")
        elif not re.fullmatch(r"[A-Za-z][A-Za-z0-9-]*\s*=.*", stripped):
            raise ControlError("Unsupported Git configuration syntax")
    parser = configparser.ConfigParser(interpolation=None, strict=True, delimiters=("=",), empty_lines_in_values=False)
    try:
        parser.read_string(raw)
    except configparser.Error as exc:
        raise ControlError("Ambiguous Git configuration is not audited") from exc
    if parser.defaults() or len({s.lower() for s in parser.sections()}) != len(parser.sections()):
        raise ControlError("Git defaults or duplicate sections are not audited")
    core_flags = {"filemode", "logallrefupdates", "ignorecase", "precomposeunicode"}
    for section in parser.sections():
        primary = section.split(" ", 1)[0].lower()
        for key, value in parser.items(section):
            if primary == "core":
                if key == "repositoryformatversion" and value == "0":
                    continue
                if key == "bare" and value.lower() == "false":
                    continue
                if key in core_flags and value.lower() in ("true", "false"):
                    continue
                raise ControlError("Unsupported Git core setting; executable callbacks are refused")
            if primary == "user" and key in ("name", "email"):
                continue
            if primary == "remote" and key in ("url", "pushurl") and value.startswith(("https://", "ssh://")):
                continue
            if primary == "remote" and key == "fetch" and re.fullmatch(r"\+?refs/[A-Za-z0-9_*/.:-]+", value):
                continue
            if primary == "branch" and key in ("remote", "merge") and re.fullmatch(r"[A-Za-z0-9_/.:-]+", value):
                continue
            raise ControlError("Unsupported Git setting; includes, filters, transports and callbacks are refused")
    return root


def safe_git(root, arguments, *, text=False):
    """Return CompletedProcess with bounded output; reject unsafe repo/config first.

    Nonzero exit codes remain the caller's responsibility. No inherited Git config,
    credentials, includes, callback drivers or external object directories are used.
    Only explicit https/ssh destinations are accepted for transport commands.
    """
    root = _git_preflight(root)
    if not isinstance(arguments, (list, tuple)) or not arguments or not all(isinstance(a, str) for a in arguments):
        raise ControlError("Git arguments must be an explicit string list")
    args = list(arguments)
    if args[:2] == ["-c", "push.followTags=false"]:
        args = args[2:]
    forbidden = ("-c", "-C", "--config-env", "--git-dir", "--work-tree", "--exec-path", "--super-prefix", "--namespace", "--bare", "--show-signature")
    if not args or any(a == f or a.startswith(f + "=") for a in args for f in forbidden) or any(a.startswith(("-c", "-C")) for a in args):
        raise ControlError("Git arguments cannot replace the inspected configuration/context")
    if args[0] not in ("rev-parse", "status", "log", "rev-list", "ls-tree", "cat-file", "ls-remote", "push"):
        raise ControlError("Git command is outside the supported inspection/publication interface")
    if args[0] in ("ls-remote", "push"):
        transport_args = args[2:] if args[1:2] == ["--"] else args[1:]
        if not transport_args or not transport_args[0].startswith(("https://", "ssh://")):
            raise ControlError("Git transport requires an explicit https or ssh destination")
    env = {"PATH": os.defpath, "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_CONFIG_SYSTEM": "/dev/null", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_COUNT": "0",
           "GIT_TERMINAL_PROMPT": "0", "GIT_OPTIONAL_LOCKS": "0", "GIT_NO_REPLACE_OBJECTS": "1",
           "GIT_NO_LAZY_FETCH": "1", "GIT_ATTR_NOSYSTEM": "1", "GIT_PAGER": "cat", "PAGER": "cat"}
    command = ["git", "-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor=false",
               "-c", "core.attributesFile=/dev/null", "-c", "core.untrackedCache=false",
               "-c", "push.followTags=false", "-c", "protocol.allow=never",
               "-c", "protocol.https.allow=always", "-c", "protocol.ssh.allow=always", "-C", str(root), *args]
    output, errors, total = bytearray(), bytearray(), 0
    deadline = time.monotonic() + GIT_TIMEOUT_SECONDS
    try:
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env) as process:
            try:
                with selectors.DefaultSelector() as selector:
                    for stream, target in ((process.stdout, output), (process.stderr, errors)):
                        os.set_blocking(stream.fileno(), False)
                        selector.register(stream, selectors.EVENT_READ, target)
                    while selector.get_map():
                        remaining = deadline - time.monotonic()
                        if remaining <= 0:
                            raise ControlError("Git inspection exceeded its execution timeout")
                        for key, _ in selector.select(min(remaining, 0.1)):
                            chunk = os.read(key.fd, 65_536)
                            if not chunk:
                                selector.unregister(key.fileobj)
                                continue
                            total += len(chunk)
                            if total > GIT_OUTPUT_LIMIT:
                                raise ControlError("Git inspection exceeded its output bound")
                            key.data.extend(chunk)
                code = process.wait(timeout=max(0.01, deadline - time.monotonic()))
            except Exception:
                process.kill()
                process.wait()
                raise
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ControlError("Git inspection could not complete") from exc
    stdout, stderr = bytes(output), bytes(errors)
    if text:
        stdout, stderr = stdout.decode("utf-8", errors="replace"), stderr.decode("utf-8", errors="replace")
    return subprocess.CompletedProcess(command, code, stdout, stderr)


def git_snapshot(root):
    def git(args):
        result = safe_git(root, args)
        if result.returncode:
            raise ControlError("Outgoing Git state could not be fully read")
        return result.stdout
    head = git(["rev-parse", "HEAD"]).decode().strip()
    history = git(["log", "--all", "HEAD", "-p", "--binary", "--no-ext-diff", "--no-textconv", "--format=fuller"])
    return {"head": head, "history_sha256": hashlib.sha256(history).hexdigest(),
            "status_sha256": hashlib.sha256(git(["status", "--porcelain=v1"])).hexdigest()}


def package_manifest(root):
    root = Path(root).absolute()
    if root.is_symlink() or not root.is_dir():raise ControlError("Package must be a real directory")
    files = []
    for base, dirs, names in os.walk(root, followlinks=False, onerror=_walk_error):
        for name in dirs + names:
            if (Path(base)/name).is_symlink():raise ControlError("Package symlink refused; do not follow external targets")
        if Path(base) != root and ".git" in dirs + names:
            raise ControlError("Nested Git metadata requires a separately audited package")
        dirs[:] = sorted(d for d in dirs if d != ".git")
        for name in sorted(names):
            p = Path(base)/name
            if name == ".git":
                raise ControlError("Gitdir files/worktrees are not audited")
            try:
                if not p.is_file():raise ControlError("Non-regular package resource refused")
                content = p.read_bytes()
                files.append({"path":p.relative_to(root).as_posix(),"size":len(content),"digest":hashlib.sha256(content).hexdigest(),"executable":bool(p.stat().st_mode & 0o111)})
            except OSError as exc:
                raise ControlError("Package resource could not be fully read") from exc
    value = {"algorithm":"sha256","files":sorted(files,key=lambda x:x["path"]),"git_state":git_snapshot(root) if (root/".git").exists() else "not_a_git_root"}
    return {**value,"digest":hashlib.sha256(canonical(value)).hexdigest()}


def skill_metadata(root):
    root=Path(root);text=(root/"SKILL.md").read_text()
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:raise ControlError("YAML frontmatter required")
    front=text[4:].split("\n---\n",1)[0]; fields={}; current=None
    for line in front.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):continue
        if line[:1].isspace():
            if current in ("name","description","compatibility"):
                fields[current]+=" "+line.strip()
            continue
        if ":" not in line:raise ControlError("Unsupported YAML form; use a compatible parser")
        key,value=line.split(":",1);key=key.strip();value=value.strip()
        if key in fields or key not in ("name","description","license","compatibility","metadata","allowed-tools"):
            raise ControlError("Duplicate or unsupported frontmatter field")
        if value in ("|",">","|-",">-"):value=""
        elif value.startswith('"'):
            try:value=json.loads(value)
            except ValueError as exc:raise ControlError("Invalid quoted frontmatter") from exc
        elif value.startswith("'") and value.endswith("'"):value=value[1:-1].replace("''", "'")
        fields[key]=value;current=key
    name,description=fields.get("name"),fields.get("description")
    if not isinstance(name,str) or len(name)>64 or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",name) or root.name!=name:
        raise ControlError("Invalid skill name or directory mismatch")
    if not isinstance(description,str) or not 1<=len(description)<=1024:raise ControlError("Invalid skill description")
    if "compatibility" in fields and not 1<=len(fields["compatibility"])<=500:raise ControlError("Invalid compatibility")
    if "{{" in text:raise ControlError("Unfinished template in functional skill")
    return {"name":name,"description":description,"validation_scope":"Generated scalar frontmatter and supported block text; not a universal YAML parser"}
