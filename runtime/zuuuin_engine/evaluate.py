"""Evaluate observed outputs and activation, preserving unmeasured dimensions."""
from .state import ControlError
from .util import response
import math


def at_path(value, path):
    for part in path.split("."):
        if not isinstance(value, dict) or part not in value:
            return False, None
        value = value[part]
    return True, value


def run(request, context=None):
    if not request.get("revision_id") or not request.get("cases"):
        raise ControlError("A fixed revision and nonempty cases are required")
    results, activation_positive, activation_negative = [], [], []
    for case in request["cases"]:
        if not case.get("case_id"):
            raise ControlError("Each case needs identity")
        checks = []
        executed = case.get("executed") is True
        if executed and case.get("evidence_ref") and case.get("expected"):
            for path, expected in case["expected"].items():
                found, actual = at_path(case.get("observed_output"), path)
                checks.append({"criterion": path, "passed": found and actual == expected})
            outcome = "pass" if all(c["passed"] for c in checks) else "fail"
        else:
            outcome = "inconclusive" if executed else "not_run"
        expected_activation, observed_activation = case.get("expected_activation"), case.get("observed_activation")
        if executed and case.get("evidence_ref") and type(expected_activation) is bool and type(observed_activation) is bool:
            (activation_positive if expected_activation else activation_negative).append(observed_activation)
        results.append({"case_id": case["case_id"], "executed": executed, "outcome": outcome, "checks": checks, "evidence_ref": case.get("evidence_ref")})
    measured = request.get("measurements", {})
    metrics = {}
    for dimension in ("tokens", "duration_seconds", "cost_money"):
        item = measured.get(dimension, {})
        value = item.get("value")
        valid = item.get("source_kind") == "runtime" and item.get("evidence_ref") and type(value) in (int, float) and math.isfinite(value) and value >= 0
        metrics[dimension] = value if valid else None
    metrics["missed_activation_denominator"] = len(activation_positive)
    metrics["false_activation_denominator"] = len(activation_negative)
    metrics["missed_activation_rate"] = sum(not x for x in activation_positive) / len(activation_positive) if activation_positive else None
    metrics["false_activation_rate"] = sum(activation_negative) / len(activation_negative) if activation_negative else None
    return response("evaluate", "passed" if all(r["outcome"] == "pass" for r in results) else "inconclusive_or_failed", revision_id=request["revision_id"], results=results, metrics=metrics, changes_applied=False, proposals=[{"case_id": r["case_id"], "reason": "Observed criterion failure; define a hypothesis before editing"} for r in results if r["outcome"] == "fail"])
