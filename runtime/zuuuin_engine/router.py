"""Minimal task routing over supplied maps and approved scoped revisions."""
from .state import ControlError
from .util import response, stable_id


def run(request, context=None):
    ctx = context or {}
    if request.get("related") is False:
        return response("router", "out_of_scope", selected=[], discovery_performed=False, created_skill=False)
    if not request.get("task") or not request.get("context_key"):
        raise ControlError("Task and context identity are required")
    if not all(isinstance(request.get(k),str) and request[k] for k in ("session_id","task_id","event_id")):
        raise ControlError("Session, task and event identities are required")
    if ctx.get("context_key") and request["context_key"] != ctx["context_key"]:
        raise ControlError("Project profile context mismatch")
    if request.get("depth", 0) > 1:
        return response("router", "deduplicated", selected=[], discovery_performed=False, created_skill=False)
    identity = stable_id("routing-event", request["context_key"] + ":" + request["session_id"] + ":" + request["task_id"] + ":" + request["event_id"])
    seen = ctx.setdefault("seen_events", set())
    if identity in seen:
        return response("router", "deduplicated", selected=[], discovery_performed=False, created_skill=False)
    if not request.get("need_id") or not request.get("capability_ids"):
        return response("router", "needs_mapping", selected=[], discovery_performed=False, created_skill=False)
    seen.add(identity)
    capabilities = set(request["capability_ids"])
    selected, missing = [], []
    for entry in request.get("catalog", []):
        if not capabilities.intersection(entry.get("capability_ids", [])):
            continue
        if entry.get("approved") is True and entry.get("availability") == "discoverable" and request["context_key"] in entry.get("scope_contexts", []):
            if set(entry.get("required_tools", [])) <= set(ctx.get("available_tools", [])):
                selected.append(entry["revision_id"])
                capabilities -= set(entry["capability_ids"])
            else:
                missing.append(entry["revision_id"])
    if not capabilities:
        return response("router", "selected_approved", selected=selected, discovery_performed=False, created_skill=False)
    if ctx.get("provider_mode", "synthetic") != "synthetic":
        raise ControlError("Community provider is not connected during bootstrap")
    provider = ctx.get("discovery_provider")
    if provider is None:
        discovered = {"status": "unknown", "candidates": []}
    else:
        discovered = provider({"capability_ids": sorted(capabilities), "max_queries": 2, "max_candidates": 3})
    health = discovered.get("status", "unknown")
    status = {"success_with_results": "comparison_required", "success_no_results": "no_candidate_in_scope"}.get(health, "discovery_inconclusive")
    return response("router", status, selected=selected, missing_dependencies=missing, discovery_performed=provider is not None, discovery_health=health, candidates=discovered.get("candidates", [])[:3], created_skill=False, installation_performed=False)
