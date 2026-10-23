"""Private local-profile reader and atomic JSON utilities for the engine CLI.

This module validates the data consumed by the CLI. Workflow orchestration and
human approval decisions belong to the caller's private control system.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo


class ControlError(ValueError):
    pass


def now():
    return datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_json(path, value, before_replace=None):
    """A failed write leaves the preceding file intact; fsync before rename."""
    path = Path(path)
    if path.is_symlink() or not path.parent.is_dir() or path.parent.is_symlink():
        raise ControlError("Unsafe JSON destination")
    fd, temporary = tempfile.mkstemp(prefix=".pending-", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(canonical(value) + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
        if before_replace:
            before_replace()
        os.replace(temporary, path)
        parent_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(parent_fd)
        finally:
            os.close(parent_fd)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _absolute_path(value):
    return (isinstance(value, str) and value and Path(value).is_absolute()
            and ".." not in Path(value).parts
            and not any(ord(char) < 32 or ord(char) == 127 for char in value))


def _evidence_refs(value):
    if not isinstance(value, list):
        raise ControlError("Evidence references must be a list")
    for ref in value:
        if (not isinstance(ref, dict) or not _absolute_path(ref.get("path"))
                or not isinstance(ref.get("sha256"), str)
                or not re.fullmatch(r"[0-9a-f]{64}", ref["sha256"])):
            raise ControlError("Invalid evidence reference")


def validate_state(state):
    """Validate a generic local profile without interpreting workflow gates."""
    if (not isinstance(state, dict) or state.get("schema_version") != "1.0"
            or type(state.get("state_revision")) is not int):
        raise ControlError("Invalid local-profile format")
    try:
        uuid.UUID(state["id"])
        uuid.UUID(state["run_id"])
        if (state["id"] != state["run_id"] or state["state_revision"] < 0
                or type(state.get("revision")) is not int
                or state["revision"] != state["state_revision"]):
            raise ValueError("Invalid identity/revision")
        for field in ("created_at", "updated_at", "started_at"):
            if datetime.fromisoformat(state[field]).utcoffset() is None:
                raise ValueError("Timezone required")
    except (KeyError, ValueError, TypeError, AttributeError) as exc:
        raise ControlError("Profile identity, time or revision invalid") from exc
    if (not isinstance(state.get("phase"), str)
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", state["phase"])):
        raise ControlError("An explicit local workflow phase is required")
    if not isinstance(state.get("phase_status"), str) or state["phase_status"] not in {
            "not_started", "in_progress", "ready_for_gate", "awaiting_approval",
            "blocked", "completed", "invalidated"}:
        raise ControlError("Invalid local phase status")
    roots = state.get("roots")
    required_roots = {"work", "private", "source", "test", "release"}
    if (not isinstance(roots, dict) or not required_roots.issubset(roots)
            or not all(_absolute_path(value) for value in roots.values())):
        raise ControlError("Explicit absolute local-profile roots are required")
    events = state.get("events")
    if not isinstance(events, list):
        raise ControlError("Profile events must be a list")
    seen = set()
    for event in events:
        try:
            if not isinstance(event, dict):
                raise ValueError("Event must be an object")
            uuid.UUID(event["id"])
            if event["id"] in seen:
                raise ValueError("Duplicate event")
        except (KeyError, ValueError, TypeError, AttributeError) as exc:
            raise ControlError("Invalid or duplicate event ID") from exc
        seen.add(event["id"])
        if not isinstance(event.get("event_type", event.get("type")), str):
            raise ControlError("An explicit event type is required")
        _evidence_refs(event.get("evidence_refs", []))
    _evidence_refs(state.get("evidence_refs"))
    if "publication_approval" in state and not isinstance(state["publication_approval"], dict):
        raise ControlError("Invalid publication approval record")
    return state


def _private_directory(argument):
    """Resolve verified OS aliases while refusing user-created symlink paths."""
    path = Path(argument).absolute()
    if ".." in path.parts:
        raise ControlError("Private-root traversal refused")
    aliases = {Path("/tmp"): Path("/private/tmp"),
               Path("/var"): Path("/private/var"),
               Path("/etc"): Path("/private/etc")}
    current = Path("/")
    for part in path.parts[1:]:
        child = current / part
        if child.is_symlink():
            target = aliases.get(child)
            if target is None or child.resolve(strict=True) != target:
                raise ControlError("Private-root symlink ancestry refused")
            current = target
        elif child.is_dir():
            current = child
        else:
            raise ControlError("Private root requires existing real directories")
    return current


class ExecutionStore:
    """Read-only CLI access; this class cannot advance or approve a workflow."""
    def __init__(self, private_root):
        self.root = _private_directory(private_root)
        if self.root.is_symlink() or not self.root.is_dir():
            raise ControlError("Private root must be an existing real directory")
        for sub in (self.root / "state", self.root / "state/events"):
            if sub.is_symlink() or not sub.is_dir():
                raise ControlError("State and event directories must be real directories")
        self.path = self.root / "state/execution.json"

    def read(self):
        if self.path.is_symlink() or not self.path.is_file():
            raise ControlError("A regular local-profile file is required")
        state = validate_state(json.loads(self.path.read_text()))
        if Path(state["roots"]["private"]) != self.root:
            raise ControlError("Profile private root differs from the selected root")
        return state

    def verify_checkpoint_evidence(self):
        state = self.read()
        actions = [event for event in state["events"]
                   if event.get("event_type", event.get("type"))
                   in ("action.completed", "action.corrected")]
        refs = actions[-1].get("evidence_refs", []) if actions else state["evidence_refs"]
        for ref in refs:
            path = Path(ref["path"])
            if path.is_symlink() or not path.is_file() or digest(path) != ref["sha256"]:
                raise ControlError("Latest profile evidence changed or is missing")
        return True
