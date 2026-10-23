"""Exact-package publication with trusted policy, scoped authorization and receipts."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import fcntl
import uuid
from urllib.parse import urlsplit
from .state import ControlError, atomic_json, now
from .util import response, contained, package_manifest, safe_git


class GitTransport:
    """No shell, force push, inherited hooks, or automatic repository creation."""
    def _git(self, package, arguments):
        return safe_git(package, arguments, text=True)

    def expected(self, package):
        root = self._git(package, ["rev-parse", "--show-toplevel"])
        if root.returncode or Path(root.stdout.strip()).resolve() != package.resolve():
            raise ControlError("Only a dedicated release Git root can be pushed")
        status = self._git(package, ["status", "--porcelain"])
        if status.returncode or status.stdout.strip():
            raise ControlError("Release tree must be clean and committed")
        head = self._git(package, ["rev-parse", "HEAD"])
        if head.returncode:
            raise ControlError("Release commit unavailable")
        return head.stdout.strip()

    def lookup(self, package, destination, target_ref):
        result = self._git(package, ["ls-remote", "--", destination, target_ref])
        return result.stdout.split()[0] if result.returncode == 0 and result.stdout.strip() else None

    def push(self, package, destination, target_ref, expected_commit):
        if not re.fullmatch(r"[0-9a-f]{40,64}", expected_commit):
            raise ControlError("An immutable approved commit is required")
        return self._git(package, ["-c", "push.followTags=false", "push", "--", destination, expected_commit + ":" + target_ref]).returncode


def _run(request, context=None):
    ctx = context or {}
    package = Path(request.get("package", "")).absolute()
    if not any(contained(package, Path(a)) for a in ctx.get("allowed_read_roots", [])):
        raise ControlError("Publication package outside authorized scope")
    manifest = package_manifest(package)
    if request.get("mode", "publish") not in ("prepare", "publish") or ("simulate" in request and type(request["simulate"]) is not bool):
        raise ControlError("Explicit supported mode and boolean simulation flag required")
    if request.get("mode") == "prepare":
        return response("publish", "prepared_only", package_digest=manifest["digest"], manifest=manifest, external_effects=False)
    destination, audit = request.get("destination"), request.get("audit", {})
    authorization = ctx.get("authorizations", {}).get(request.get("authorization_id"), {})
    if authorization.get("type") == "authorization":
        from .contracts import validate_record
        validate_record(authorization)
        limits=authorization["limits"]
        if request.get("candidate_id") not in authorization["resources"]:
            authorization={}
        else:
            authorization={**authorization,"package_digest":limits.get("package_hash"),"destination":limits.get("destination"),"target_ref":limits.get("target_ref"),"simulation_only":limits.get("simulation_only",False)}
    simulated = request.get("simulate", True) is True
    target_ref = request.get("target_ref", "refs/heads/main")
    if not destination or not re.fullmatch(r"refs/heads/[A-Za-z0-9][A-Za-z0-9._/-]*", target_ref) or ".." in target_ref:
        raise ControlError("Explicit destination and valid target branch are required")
    parsed = urlsplit(destination)
    if parsed.username or parsed.password or any(c.isspace() for c in destination):
        raise ControlError("Credential-bearing or malformed destination refused")
    approved_audit = audit.get("status") == "approved_in_scope" and audit.get("package_digest") == manifest["digest"]
    exact = authorization.get("package_digest") == manifest["digest"] and authorization.get("destination") == destination and authorization.get("target_ref", target_ref) == target_ref and authorization.get("action") == "publish"
    if not approved_audit or not exact:
        return response("publish", "blocked", reason="Current audit, exact package and scoped authorization required", external_effects=False)
    try:
        instant = datetime.now(timezone.utc)
        start = datetime.fromisoformat(authorization["valid_from"])
        end = datetime.fromisoformat(authorization["valid_until"]) if authorization.get("valid_until") else None
        valid = start.utcoffset() is not None and start <= instant and (end is None or (end.utcoffset() is not None and instant <= end))
    except (KeyError, ValueError, TypeError):
        valid = False
    if not valid:
        return response("publish", "blocked", reason="Authorization validity is unknown or expired", external_effects=False)
    if simulated:
        return response("publish", "simulated", package_digest=manifest["digest"], destination=destination, external_effects=False)
    policy, approval = ctx.get("policy", {}), ctx.get("publication_approval", {})
    phase = ctx.get("phase")
    enabled = (policy.get("external_publication_enabled") is True
               and isinstance(phase, str)
               and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", phase)
               and policy.get("publication_phase") == phase)
    approved = approval.get("source") == "user" and approval.get("package_digest") == manifest["digest"] and approval.get("destination") == destination
    if not enabled or not approved or authorization.get("source") != "user" or authorization.get("simulation_only", False):
        return response("publish", "blocked", reason="Trusted publication policy, explicit phase and user approval required", external_effects=False)
    if not ctx.get("receipt_root"):
        raise ControlError("Explicit private receipt root required")
    receipt_root = Path(ctx["receipt_root"])
    if not receipt_root.is_dir() or receipt_root.is_symlink():
        raise ControlError("A private existing receipt directory is required")
    key = hashlib.sha256((manifest["digest"] + destination + target_ref + request["authorization_id"]).encode()).hexdigest()
    receipt = receipt_root / (key + ".json")
    transport = ctx.get("transport") or GitTransport()
    expected = transport.expected(package)
    git_state = manifest.get("git_state")
    if not isinstance(git_state, dict) or expected != git_state.get("head"):
        return response("publish", "blocked", reason="Current commit differs from the approved Git package", external_effects=False)
    if receipt.is_symlink():
        raise ControlError("Receipt symlink refused")
    if receipt.exists():
        previous = json.loads(receipt.read_text())
        observed = transport.lookup(package, destination, target_ref)
        if observed == previous.get("expected_commit"):
            previous.update(status="published_verified", verified_at=now())
            atomic_json(receipt, previous)
            return response("publish", "published_verified", receipt=previous, repeated_push=False)
        return response("publish", "outcome_unknown", reason="Prior attempt exists; reconcile before any repeat", repeated_push=False)
    stamp=now()
    pending = {"schema_version":"1.0","type":"publication_receipt","id":str(uuid.uuid5(uuid.NAMESPACE_URL,key)),"revision":1,"created_at":stamp,"updated_at":stamp,"status":"attempt_started","package_digest":manifest["digest"],"expected_commit":expected,"destination":destination,"target_ref":target_ref,"started_at":stamp}
    if package_manifest(package)["digest"] != manifest["digest"]:
        return response("publish", "blocked", reason="Package changed after approval; new audit and authorization required", external_effects=False)
    atomic_json(receipt, pending)  # Commit intent before the external side effect.
    exit_code = transport.push(package, destination, target_ref, expected)
    observed = transport.lookup(package, destination, target_ref)
    status = "published_verified" if observed == expected else "outcome_unknown"
    pending.update(status=status, push_exit_code=exit_code, verified_at=now(), updated_at=now(), revision=2)
    atomic_json(receipt, pending)
    return response("publish", status, receipt=pending, external_effects=True)


def run(request, context=None):
    ctx=context or {}
    receipt_root=Path(ctx["receipt_root"]) if ctx.get("receipt_root") else None
    if request.get("simulate", True) is True or receipt_root is None or not receipt_root.is_dir():
        return _run(request,ctx)
    if receipt_root.is_symlink():raise ControlError("Receipt root symlink refused")
    fd=os.open(receipt_root/"publication.lock",os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
    try:
        fcntl.flock(fd,fcntl.LOCK_EX)
        return _run(request,ctx)
    finally:
        fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
