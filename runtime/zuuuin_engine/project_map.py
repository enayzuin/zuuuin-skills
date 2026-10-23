"""Map authorized structured observations; never infer needs from project names."""
from .state import ControlError
from .util import response, stable_id


def run(request, context=None):
    sources = request.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ControlError("Provide at least one authorized source snapshot")
    projects, needs, conflicts, gaps, coverage = {}, {}, [], [], []
    project_observations = {}
    for source in sources:
        ref = source.get("source_ref")
        if not ref or source.get("authorized") is not True:
            raise ControlError("Each source needs an explicit authorized scope and reference")
        complete = source.get("complete") is True and not source.get("has_more", False) and source.get("status", "success") == "success"
        coverage.append({"source_ref": ref, "complete": complete, "status": source.get("status", "success")})
        for observation in source.get("projects", []):
            key = observation.get("canonical_key")
            if not isinstance(key, str) or not key:
                gaps.append({"source_ref": ref, "reason": "Project canonical identity is unresolved"})
                continue
            identity = stable_id("project", key)
            candidate = {"id": identity, "canonical_key": key, "name": observation.get("name"), "objective": observation.get("objective"), "status": observation.get("status", "unknown"), "source_refs": [ref], "needs": []}
            if not candidate["name"] or not candidate["objective"]:
                gaps.append({"source_ref":ref,"project_id":identity,"reason":"Project name or objective not observed; do not infer from title"})
            if identity not in projects:
                projects[identity] = candidate
                project_observations[identity] = {field: [] for field in ("name", "objective", "status")}
            else:
                if ref not in projects[identity]["source_refs"]:
                    projects[identity]["source_refs"].append(ref)
            for field, observations in project_observations[identity].items():
                observations.append({"source_ref": ref, "value": candidate[field]})
            for n in observation.get("needs", []):
                if not n.get("desired_output") or not n.get("success_criteria"):
                    gaps.append({"source_ref": ref, "project_id": identity, "reason": "Need lacks observable outcome or acceptance criteria"})
                    continue
                nid = stable_id("need", key + ":" + str(n.get("canonical_key", n["desired_output"])))
                value = {"id": nid, "project_id": identity, "source_refs": [ref], "claim_status": n.get("claim_status", "confirmed"), **{k: n.get(k) for k in ("input", "desired_output", "success_criteria", "constraints", "priority", "frequency")}}
                if nid in needs and needs[nid]["desired_output"] != value["desired_output"]:
                    conflicts.append({"need_id": nid, "field": "desired_output", "resolution": "source_reconciliation_required"})
                elif nid not in needs:
                    needs[nid] = value
                if nid not in projects[identity]["needs"]:
                    projects[identity]["needs"].append(nid)
    # Reconcile after collecting every observation, so a later repetition cannot
    # silently resolve a disagreement or make the first source canonical.
    for identity, fields in project_observations.items():
        for field, observations in fields.items():
            if any(item["value"] != observations[0]["value"] for item in observations[1:]):
                projects[identity][field] = "unknown" if field == "status" else None
                conflicts.append({"project_id": identity, "field": field, "sources": list(projects[identity]["source_refs"]), "observations": observations, "resolution": "human_or_source_reconciliation_required"})
    complete = all(s["complete"] for s in coverage)
    return response("project-map", "mapped" if complete and not conflicts and not gaps else "inconclusive", projects=list(projects.values()), needs=list(needs.values()), coverage={"complete": complete, "sources": coverage, "observed_projects": len(projects)}, conflicts=conflicts, gaps=gaps)
