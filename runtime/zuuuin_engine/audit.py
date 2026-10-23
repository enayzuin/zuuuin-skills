"""Audit exact package bytes and automatically applicable outgoing Git history."""
from pathlib import Path
import hashlib
import re
from .state import ControlError
from .util import response, contained, package_manifest, safe_git, scan_value, GIT_OUTPUT_LIMIT


def _display(value, identifiers):
    return "[redacted filename]" if scan_value(value, identifiers) else value


def _redact(value, identifiers):
    """Sanitize every output slot, including manifest paths and reviewer labels."""
    if isinstance(value, str):
        return "[redacted]" if scan_value(value, identifiers) else value
    if isinstance(value, list):
        return [_redact(item, identifiers) for item in value]
    if isinstance(value, dict):
        return {_redact(key, identifiers): _redact(item, identifiers) for key, item in value.items()}
    return value


def _inspect(content, location, request, findings, limitations):
    identifiers = request.get("private_identifiers", [])
    shown = _display(location, identifiers)
    findings.extend({"path": "[redacted filename]", **item} for item in scan_value(location, identifiers))
    text = content.decode("utf-8", errors="replace")
    findings.extend({"path": shown, **item} for item in scan_value(text, identifiers))
    try:
        content.decode("utf-8")
        binary = b"\x00" in content
    except UnicodeDecodeError:
        binary = True
    reviewed = False
    if binary:
        digest = hashlib.sha256(content).hexdigest()
        review = request.get("binary_reviews", {}).get(digest, {})
        reviewed = review.get("status") == "passed" and bool(review.get("evidence_ref"))
        if not reviewed:
            limitations.append({"path": shown, "digest": digest, "reason": "Binary content not contextually reviewed"})
    return binary, reviewed


def _git(root, arguments):
    result = safe_git(root, arguments)
    if result.returncode:
        raise ControlError("Applicable Git history could not be fully inspected")
    return result.stdout


def _history(package, request, findings, limitations):
    """Inspect reachable commit metadata, exact tree names and raw unique blobs.

    Binary reviews use SHA-256 of raw blobs, not Git object IDs. Gitlinks remain
    pending coverage; no submodule is followed or fetched.
    """
    metadata = _git(package, ["log", "--all", "HEAD", "--format=fuller", "--no-color", "--no-show-signature"])
    findings.extend({"path": "outgoing-history-metadata", **item} for item in scan_value(metadata.decode("utf-8", errors="replace"), request.get("private_identifiers", [])))
    commits = _git(package, ["rev-list", "--all", "HEAD"]).splitlines()
    if not commits or len(commits) > 10_000:
        raise ControlError("Applicable history is empty or exceeds its inspection bound")
    blobs, entries, total = {}, 0, len(metadata)
    for raw_commit in commits:
        commit = raw_commit.decode("ascii")
        if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", commit):
            raise ControlError("Invalid Git object identity")
        tree = _git(package, ["ls-tree", "-rz", "--full-tree", commit])
        total += len(tree)
        if total > GIT_OUTPUT_LIMIT:
            raise ControlError("Applicable history exceeds its total inspection bound")
        for entry in tree.split(b"\x00"):
            if not entry:
                continue
            entries += 1
            if entries > 50_000:
                raise ControlError("Applicable history exceeds its tree entry bound")
            try:
                descriptor, raw_name = entry.split(b"\t", 1)
                mode, kind, raw_oid = descriptor.split(b" ")
                name = raw_name.decode("utf-8")
                oid = raw_oid.decode("ascii")
            except (ValueError, UnicodeError) as exc:
                raise ControlError("Historical tree names or objects could not be inspected") from exc
            shown = _display(name, request.get("private_identifiers", []))
            findings.extend({"path": "outgoing-history/[redacted filename]", **item} for item in scan_value(name, request.get("private_identifiers", [])))
            if kind == b"commit" or mode == b"160000":
                limitations.append({"path": "outgoing-history/" + shown, "reason": "Gitlink content requires a separately audited package"})
                continue
            if kind != b"blob" or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", oid):
                raise ControlError("Unsupported historical tree object")
            blobs.setdefault(oid, set()).add(shown)
    binary_count, pending = 0, 0
    for oid, names in blobs.items():
        try:
            size = int(_git(package, ["cat-file", "-s", oid]).strip())
        except ValueError as exc:
            raise ControlError("Historical blob size is invalid") from exc
        if size < 0 or total + size > GIT_OUTPUT_LIMIT:
            raise ControlError("Applicable history exceeds its blob inspection bound")
        content = _git(package, ["cat-file", "blob", oid])
        if len(content) != size:
            raise ControlError("Historical blob changed during inspection")
        total += size
        binary, reviewed = _inspect(content, "outgoing-history/" + sorted(names)[0], request, findings, limitations)
        binary_count += int(binary)
        pending += int(binary and not reviewed)
    return {"applicable": True, "commits_inspected": len(commits), "blobs_inspected": len(blobs),
            "binary_blobs": binary_count, "binary_blobs_pending": pending,
            "complete": not pending and not any("Gitlink" in item["reason"] for item in limitations)}


def run(request, context=None):
    package = Path(request.get("package", "")).absolute()
    allowed = (context or {}).get("allowed_read_roots", [])
    if not any(contained(package, Path(a)) for a in allowed):
        raise ControlError("Package is outside the authorized audit scope")
    git_marker = package / ".git"
    applicable_git = git_marker.exists() or git_marker.is_symlink()
    repository = request.get("git_repository")
    if repository:
        supplied = Path(repository).absolute()
        if supplied.is_symlink() or supplied.resolve() != package.resolve() or not applicable_git:
            raise ControlError("History repository must be the audited package Git root")
    manifest = package_manifest(package)
    findings, limitations = [], []
    for item in manifest["files"]:
        try:
            content = (package / item["path"]).read_bytes()
        except OSError as exc:
            raise ControlError("Package content could not be fully inspected") from exc
        if hashlib.sha256(content).hexdigest() != item["digest"]:
            raise ControlError("Package changed during inspection")
        _inspect(content, item["path"], request, findings, limitations)
    for raw in request.get("history_snapshots", []):
        path = Path(raw).absolute()
        if path.is_symlink() or not any(contained(path, Path(a)) for a in allowed):
            raise ControlError("History snapshot outside authorized scope")
        try:
            _inspect(path.read_bytes(), "outgoing-history-snapshot", request, findings, limitations)
        except OSError as exc:
            raise ControlError("History snapshot could not be fully inspected") from exc
    coverage = _history(package, request, findings, limitations) if applicable_git else {"applicable": False, "complete": True}
    if package_manifest(package)["digest"] != manifest["digest"]:
        raise ControlError("Package or Git history changed during inspection")
    review = request.get("contextual_review", {})
    reviewed = review.get("status") == "passed" and review.get("package_digest") == manifest["digest"] and bool(review.get("evidence_ref")) and bool(review.get("reviewer_id")) and review.get("reviewer_id") != request.get("author_id")
    if not reviewed:
        limitations.append({"path": "package", "reason": "Independent contextual review bound to current digest required"})
    if request.get("rights_confirmed") is not True:
        limitations.append({"path": "package", "reason": "Authorship/redistribution eligibility unconfirmed"})
    status = "blocked" if findings else ("review_required" if limitations else "approved_in_scope")
    report_manifest = manifest if not findings else {"algorithm": "sha256", "digest": manifest["digest"], "file_count": len(manifest["files"]), "files": "redacted after a sensitive finding"}
    return _redact(response("audit", status, package_digest=manifest["digest"], manifest=report_manifest,
                            findings=findings, limitations=limitations, history_coverage=coverage,
                            reviewed_by=review.get("reviewer_id"), exposure_performed=False), request.get("private_identifiers", []))
