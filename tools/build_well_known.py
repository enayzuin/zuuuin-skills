"""Generate the selected legacy discovery tree from public catalog/source bytes.

Contract references: Mintlify docs/ai/skillmd and skills CLI 1.7.4
src/providers/wellknown.ts. This is not a universal discovery standard.
No network, runtime installation, private configuration or engine execution.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PREFIX = ".well-known/skills/"
RESOURCES = ("SKILL.md", "references/runtime.md")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def local(value):
    path = PurePosixPath(value)
    require(not path.is_absolute() and ".." not in path.parts, "Unsafe relative path")
    current = ROOT
    for part in path.parts:
        current = current / part
        require(not current.is_symlink(), "Symlink refused")
    return current


def validate_index(index):
    """Validate this selected legacy shape, without inventing a schema URL."""
    require(isinstance(index, dict) and set(index) == {"skills"}, "Legacy index fields changed")
    require(isinstance(index["skills"], list) and len(index["skills"]) == 8, "Exactly eight entries required")
    names = set()
    for entry in index["skills"]:
        require(isinstance(entry, dict) and set(entry) == {"name", "description", "files"}, "Invalid entry fields")
        name = entry["name"]
        require(isinstance(name, str) and 1 <= len(name) <= 64 and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name), "Invalid entry name")
        require(name not in names, "Duplicate entry name")
        names.add(name)
        require(isinstance(entry["description"], str) and bool(entry["description"]), "Description required")
        require(entry["files"] == list(RESOURCES), "Selected resources must be complete and exact")
        for resource in entry["files"]:
            require(not resource.startswith(("/", "\\")) and ".." not in resource and "\x00" not in resource, "Unsafe resource path")


def render():
    catalog = json.loads(local("catalog/skills.json").read_text(encoding="utf-8"))
    skills = sorted(catalog["skills"], key=lambda skill: skill["slug"])
    revisions = {item["id"]: item for item in catalog["skill_revisions"]}
    require(len(skills) == 8 and catalog["runtime"]["version"] == "0.1.1", "Candidate selection/version changed")
    require(catalog.get("owner") == "enayzuin" and catalog.get("license") == "MIT"
            and catalog.get("distribution_version") == "0.1.1"
            and catalog.get("repository_url") == "https://github.com/enayzuin/zuuuin-skills"
            and catalog.get("site_url") == "https://enayzuin.github.io/zuuuin-skills/",
            "Selected distribution metadata changed")
    require("rights_pending" not in catalog and "public_exposure_cleared" not in catalog,
            "Instance authorizations belong outside distribution metadata")
    index, outputs = {"skills": []}, {}
    for skill in skills:
        name = skill["slug"]
        require(skill["collection"] == "engine" and skill["name"] == name and skill["path"] == "skills/" + name, "Selection binding changed")
        revision = revisions[skill["current_revision_id"]]
        require(all(item.get("owner") == "enayzuin" and item.get("license") == "MIT"
                    and "rights_pending" not in item and "public_exposure_cleared" not in item
                    for item in (skill, revision)), "Selected resource metadata changed")
        require(revision["skill_id"] == skill["id"], "Revision binding changed")
        files = {item["path"]: item["sha256"] for item in revision["source_files"]}
        expected = {skill["path"] + "/" + resource for resource in RESOURCES}
        require(len(revision["source_files"]) == 2 and set(files) == expected, "Source resource list changed")
        index["skills"].append({"name": name, "description": skill["description"], "files": list(RESOURCES)})
        for resource in RESOURCES:
            source = skill["path"] + "/" + resource
            content = local(source).read_bytes()
            require(hashlib.sha256(content).hexdigest() == files[source], "Public source hash changed")
            outputs[PREFIX + name + "/" + resource] = content
    validate_index(index)
    outputs[PREFIX + "index.json"] = (json.dumps(index, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    require(len(outputs) == 17, "Expected sixteen resources and one index")
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Read-only exact comparison, including resource bytes")
    args = parser.parse_args()
    try:
        outputs = render()
        for name, value in outputs.items():
            file = local(name)
            if file.exists():
                require(file.is_file() and file.read_bytes() == value, "Generated resource differs: " + name)
            else:
                require(not args.check, "Generated resource missing: " + name)
        if not args.check:
            for name, value in outputs.items():
                file = local(name)
                file.parent.mkdir(parents=True, exist_ok=True)
                if not file.exists():
                    with file.open("xb") as stream:
                        stream.write(value)
        print(json.dumps({"status": "checked" if args.check else "generated",
                          "contract": "legacy name/description/files", "skills": 8,
                          "resources": 16, "output_files": 17, "runtime_version": "0.1.1",
                          "public_origin": "https://enayzuin.github.io/zuuuin-skills/", "outputs": {name: hashlib.sha256(value).hexdigest()
                                                                for name, value in outputs.items()}}, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"status": "refused", "error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
