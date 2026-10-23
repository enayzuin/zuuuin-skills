"""Read-only physical catalog of explicitly authorized roots."""
import json
import os
from pathlib import Path
from .state import ControlError
from .util import response, stable_id, contained, package_manifest, skill_metadata


def run(request, context=None):
    roots = request.get("roots")
    allowed = (context or {}).get("allowed_read_roots", [])
    if not isinstance(roots, list) or not roots or not allowed:
        raise ControlError("Explicit roots and authorized read boundaries are required")
    entries, links, errors, revisions = [], [], [], {}
    for raw in roots:
        root = Path(raw).absolute()
        if root.is_symlink() or not any(contained(root, Path(a)) for a in allowed):
            raise ControlError("Root is a symlink or outside the authorized read scope")
        if not root.is_dir():
            errors.append({"root": str(root), "reason": "Unavailable directory; not verified empty"})
            continue
        def unreadable(error):
            errors.append({"root": str(root), "reason": type(error).__name__})
        for base, dirs, files in os.walk(root, followlinks=False, onerror=unreadable):
            for name in list(dirs) + files:
                path = Path(base) / name
                if path.is_symlink():
                    links.append({"path": str(path), "target": str(path.resolve(strict=False)), "followed": False})
                    if name in dirs:
                        dirs.remove(name)
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
            if "SKILL.md" not in files or (Path(base)/"SKILL.md").is_symlink():
                continue
            package = Path(base)
            try:
                metadata = skill_metadata(package)
                manifest = package_manifest(package)
                extra_path = package / "zuuuin.manifest.json"
                extra = json.loads(extra_path.read_text()) if extra_path.is_file() else {}
                missing = [t for t in extra.get("tools", []) if t not in request.get("available_tools", [])]
                identity = stable_id("skill-revision", manifest["digest"])
                entry = {"id": identity, "name": metadata["name"], "description": metadata["description"], "path": str(package), "manifest": manifest, "origin": extra.get("origin"), "license": extra.get("license"), "authorship": "unknown_unless_proven", "availability": "dependency_missing" if missing else "unknown", "missing_tools": missing, "validation": "static_only", "model_links": request.get("model_links", {}).get(metadata["name"], [])}
                entries.append(entry)
                revisions.setdefault(metadata["name"], set()).add(manifest["digest"])
            except (OSError, ValueError, ControlError) as exc:
                errors.append({"path": str(package), "reason": type(exc).__name__, "detail": "Package unreadable, invalid or contains a symlink; inspect privately"})
    conflicts = [{"name": k, "distinct_revisions": len(v)} for k, v in revisions.items() if len(v) > 1]
    return response("catalog", "cataloged" if not errors else "partial", entries=entries, symlinks=links, conflicts=conflicts, errors=errors, coverage={"complete": not errors, "root_count": len(roots)}, mutations=[])
