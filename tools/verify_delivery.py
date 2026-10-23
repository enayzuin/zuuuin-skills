"""Verify this local candidate. Optional examples require the offline wheel installed.

No publication, account access, community discovery or skill installation.
Synthetic helper execution is distinct from client activation or productivity.
"""
import argparse
import ast
import hashlib
from html.parser import HTMLParser
import importlib.metadata
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OPERATIONS = ["project-map", "router", "catalog", "compare", "evaluate", "author", "audit", "publish"]

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def require(condition, message):
    if not condition: raise ValueError(message)
def pairs(items):
    value = {}
    for key, item in items:
        require(key not in value, "Duplicate JSON key"); value[key] = item
    return value
def read_json(path):
    def invalid(value): raise ValueError("Nonfinite JSON value: " + value)
    def finite(value):
        result = float(value); require(math.isfinite(result), "Nonfinite numeric result"); return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs, parse_constant=invalid, parse_float=finite)
def package_files():
    result = []
    for directory, dirs, files in os.walk(ROOT, followlinks=False):
        if Path(directory) == ROOT:
            dirs[:] = [name for name in dirs if name != ".git"]
            files = [name for name in files if name != ".git"]
        for name in dirs + files: require(not (Path(directory) / name).is_symlink(), "Package symlink refused")
        result.extend(Path(directory) / name for name in files)
    return sorted(result)
def run(args, cwd=ROOT):
    env = {"PATH": os.defpath, "LANG": "C.UTF-8"}
    if os.environ.get("TMPDIR"): env["TMPDIR"] = os.environ["TMPDIR"]
    proc = subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True, timeout=120)
    require(proc.returncode == 0, "Command failed: " + str(args[:5]) + " " + proc.stderr[-1800:])
    return proc.stdout
def matches(expected, actual):
    if isinstance(expected, dict): return isinstance(actual, dict) and all(k in actual and matches(v, actual[k]) for k, v in expected.items())
    if isinstance(expected, list): return isinstance(actual, list) and len(expected) == len(actual) and all(matches(e, a) for e, a in zip(expected, actual))
    return type(expected) is type(actual) and expected == actual

class Page(HTMLParser):
    def __init__(self): super().__init__(); self.links = []; self.ids = set()
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "href" in attrs: self.links.append(attrs["href"])
        if "id" in attrs: self.ids.add(attrs["id"])

def static_checks():
    files = package_files(); before = {p: sha(p) for p in files}; json_count = python_count = links = 0
    for path in files:
        if path.suffix == ".json": read_json(path); json_count += 1
        if path.suffix == ".py": ast.parse(path.read_text(encoding="utf-8")); python_count += 1
        if path.suffix == ".md" or path.name == "llms.txt":
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                url = urlsplit(target)
                if url.scheme or url.netloc: continue
                destination = (path.parent / unquote(url.path)).resolve() if url.path else path
                require(destination.is_relative_to(ROOT) and destination.is_file(), "Broken local Markdown link: " + target)
                links += 1
    catalog = read_json(ROOT / "catalog/skills.json"); skills = catalog["skills"]
    require(len(skills) == 8 and all(s["collection"] == "engine" for s in skills), "Unexpected selection")
    for revision in catalog["skill_revisions"]:
        for source in revision["source_files"]: require(sha(ROOT / source["path"]) == source["sha256"], "Skill revision source mismatch")
    for skill in skills:
        body = (ROOT / skill["path"] / "SKILL.md").read_text(encoding="utf-8")
        require(body.startswith("---\n") and re.search(r"^name: " + re.escape(skill["slug"]) + r"$", body, re.M) and re.search(r"^description: .+", body, re.M), "Selected frontmatter mismatch")
    wheel = ROOT / catalog["runtime"]["path"]; require(sha(wheel) == catalog["runtime"]["sha256"], "Wheel digest mismatch")
    with zipfile.ZipFile(wheel) as archive:
        modules = [name for name in archive.namelist() if name.startswith("zuuuin_engine/") and name.endswith(".py")]
        require(len(modules) == 14, "Unexpected wheel module set")
        for name in modules: require(archive.read(name) == (ROOT / "runtime" / name).read_bytes(), "Wheel/source mismatch")
    discovery = json.loads(run([sys.executable, "-I", "-B", "tools/build_discovery.py", "--check"]))
    known = json.loads(run([sys.executable, "-I", "-B", "tools/build_well_known.py", "--check"]))
    with tempfile.TemporaryDirectory(prefix="zuuuin-static-check-") as tmp:
        site = Path(tmp).resolve() / "preview"
        build = json.loads(run([sys.executable, "-I", "-B", "tools/build_site.py", "--output", str(site)]))
        pages = {}
        for path in site.rglob("*.html"):
            page = Page(); page.feed(path.read_text(encoding="utf-8")); pages[path.resolve()] = page
        html_links = 0
        for path, page in pages.items():
            for target in page.links:
                url = urlsplit(target)
                if url.scheme or url.netloc: continue
                destination = (path.parent / unquote(url.path)).resolve() if url.path else path
                require(destination.is_relative_to(site) and destination.is_file(), "Broken local HTML link")
                if url.fragment and destination in pages: require(unquote(url.fragment) in pages[destination].ids, "Broken HTML anchor")
                html_links += 1
        require(not (site / "sitemap.xml").exists() and (site / "robots.txt").read_text() == "User-agent: *\nDisallow: /\n", "Preview access/origin state changed")
    require({p: sha(p) for p in package_files()} == before, "Checks modified package")
    return {"json_files": json_count, "python_files": python_count, "markdown_local_links": links, "html_pages": build["html_pages"], "html_local_links": html_links, "skills": 8, "wheel_modules": len(modules), "discovery_groups": discovery["groups"], "well_known_resources": known["resources"], "source_bytes_preserved": True}

def examples():
    catalog = read_json(ROOT / "catalog/skills.json")
    require(importlib.metadata.version("zuuuin-engine") == catalog["runtime"]["version"], "Install the selected local wheel in a clean venv first")
    before = {p: sha(p) for p in package_files()}; records = []
    with tempfile.TemporaryDirectory(prefix="zuuuin-synthetic-check-") as tmp:
        profile = Path(tmp) / "profile"
        run([sys.executable, "-I", "-B", "tools/init_profile.py", "--root", str(profile)])
        fixture = profile / "source/engine-fixture"; shutil.copytree(ROOT / "skills", fixture)
        demo = profile / "source/demo-package"; demo.mkdir(); (demo / "README.md").write_text("Pacote sintético para revisão local.\n", encoding="utf-8")
        state_hash = sha(profile / "private/state/execution.json")
        for operation in OPERATIONS:
            request = profile / "private/requests" / (operation + ".request.json")
            shutil.copyfile(ROOT / "examples" / request.name, request)
            output = profile / "private/outputs" / (operation + ".result.json")
            cwd = fixture if operation == "catalog" else demo if operation in {"audit", "publish"} else ROOT
            run([sys.executable, "-I", "-B", "-m", "zuuuin_engine", operation, "--request", str(request), "--output", str(output), "--private-root", str(profile / "private")], cwd)
            observed = read_json(output); expected = read_json(ROOT / "examples" / (operation + ".expected.json"))
            require(matches(expected, observed), "Synthetic expected fragment mismatch: " + operation)
            records.append({"operation": operation, "matched": True, "request_sha256": sha(request), "output_sha256": sha(output), "observed_output": observed})
        require(sha(profile / "private/state/execution.json") == state_hash, "Synthetic run altered execution approvals/state")
    require({p: sha(p) for p in package_files()} == before, "Examples modified package")
    return {"passed": len(records), "total": len(OPERATIONS), "runs": records, "synthetic_only": True, "client_activation_tested": False, "productivity_claim": False}

def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--examples", action="store_true"); args = parser.parse_args()
    try:
        result = {"status": "passed", "static": static_checks(), "examples": examples() if args.examples else None}
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)); return 0
    except (OSError, ValueError, KeyError, subprocess.SubprocessError, importlib.metadata.PackageNotFoundError) as error:
        print(str(error), file=sys.stderr); return 2
if __name__ == "__main__": raise SystemExit(main())
