"""Contextual comparison: eligibility, evidence, trade-offs, then proposal."""
from .state import ControlError
from .util import response

WEIGHTS = {"efficacy": .35, "fit": .25, "integration": .15, "efficiency": .15, "maintenance": .10}


def summarize(alternative, criteria):
    scores, evidence = {}, []
    flags = {field: alternative.get(field) for field in ("eligible", "mandatory_passed")}
    eligibility_reasons = []
    if flags["eligible"] is not True:
        eligibility_reasons.append({"field": "eligible", "observed": flags["eligible"],
                                    "reason": "The supplied alternative declares itself ineligible." if flags["eligible"] is False else "Eligibility is not confirmed by the supplied input."})
    if flags["mandatory_passed"] is not True:
        eligibility_reasons.append({"field": "mandatory_passed", "observed": flags["mandatory_passed"],
                                    "reason": "The supplied mandatory check did not pass; this flag does not identify a specific failed condition." if flags["mandatory_passed"] is False else "The supplied input does not confirm that mandatory checks passed."})
    for criterion in criteria:
        observation = alternative.get("measurements", {}).get(criterion, {})
        value = observation.get("value")
        measured = observation.get("source_kind") == "execution" and bool(observation.get("evidence_refs"))
        if measured and value is not None and (type(value) not in (int, float) or not 0 <= value <= 4):
            raise ControlError("Measured ordinal score must be between zero and four")
        scores[criterion] = value if measured else None
        evidence.extend(observation.get("evidence_refs", []))
    complete = all(v is not None for v in scores.values()) and alternative.get("comparable") is True
    index = round(25 * sum(WEIGHTS[k] * scores[k] for k in WEIGHTS), 4) if complete and set(criteria) == set(WEIGHTS) else None
    return {"revision_id": alternative.get("revision_id"), "eligible": flags["eligible"] is True and flags["mandatory_passed"] is True, "eligibility_flags": flags, "eligibility_reasons": eligibility_reasons, "scores": scores, "index": index, "comparable": complete, "evidence_refs": evidence, "unknown_reason": "Index unavailable unless all five criteria have comparable execution evidence" if index is None else "none"}


def run(request, context=None):
    if not request.get("need_id") or not request.get("context_key"):
        raise ControlError("Need and project/task context are mandatory")
    criteria = request.get("criteria", list(WEIGHTS))
    if not criteria or not set(criteria) <= set(WEIGHTS) or len(set(criteria)) != len(criteria):
        raise ControlError("Choose explicit, distinct supported criteria")
    local = summarize(request.get("local", {}), criteria)
    comparisons = []
    for candidate in request.get("candidates", []):
        summary = summarize(candidate, criteria)
        gains, losses = [], []
        if not summary["eligible"]:
            decision = "not_eligible"
        elif not local["comparable"] or not summary["comparable"]:
            decision = "test_more"
        else:
            gains = [c for c in criteria if summary["scores"][c] > local["scores"][c]]
            losses = [c for c in criteria if summary["scores"][c] < local["scores"][c]]
            decision = "keep_local" if not gains else ("human_decision_required" if losses or request.get("protected_local") else "replace_in_context_proposal")
        comparisons.append({"candidate": summary, "gains": gains, "losses": losses, "proposal": decision, "adoption_authorized": False})
    return response("compare", "compared" if comparisons else "inconclusive", need_id=request["need_id"], context_key=request["context_key"], local=local, comparisons=comparisons, global_replacement=False, mutation_performed=False)
