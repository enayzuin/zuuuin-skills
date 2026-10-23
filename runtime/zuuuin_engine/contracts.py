"""Private record contracts from Annex A; no discovery, I/O, or public projection.

Reference integrity is closed by validate_registry (or validate_record with a
registry). External facts must be declared with external_fact=True and provenance;
the validator cannot infer the origin of arbitrary private prose.
"""
from collections.abc import Mapping
from datetime import datetime
import math
import re
import uuid

from .state import ControlError, now


SCHEMA_VERSION = "1.0"
COMMON_FIELDS = ("schema_version", "id", "type", "created_at", "updated_at", "revision")
ENUMS = {
    "collection": ("engine", "domain", "shared"),
    "visibility": ("private", "candidate_public", "public"),
    "maturity": ("draft", "experimental", "validated", "deprecated"),
    "validation": ("not_tested", "static_only", "passed", "failed", "inconclusive"),
    "installation": ("not_installed", "installed", "failed", "rolled_back"),
    "availability": ("unknown", "discoverable", "not_discoverable", "dependency_missing", "pending_reload"),
    "publication": ("not_requested", "staged", "audit_blocked", "awaiting_approval", "approved", "publishing", "published", "failed", "withdrawn"),
    "claim_status": ("confirmed", "inferred", "unknown"),
}

# Field names are intentionally stable and describe records, not a real taxonomy.
# A known value must have the stated type. A null needs an explicit field reason;
# identity, counters, enum dimensions and semantic invariants cannot be unknown.
FIELD_TYPES = {
    "source": {"source_type": "text", "scope": "object", "access": "text", "query": "text", "pagination": "object", "complete": "bool", "partial": "bool", "limitations": "texts"},
    "project": {"name": "text", "status": "text", "objective": "text", "needs": "ids", "sources": "ids", "constraints": "texts"},
    "need": {"project_id": "id", "input": "object", "desired_output": "text", "success_criteria": "texts", "constraints": "texts", "priority": "text", "evidence_refs": "evidence"},
    "domain": {"name": "text", "definition": "text", "need_ids": "ids"},
    "module": {"name": "text", "definition": "text", "domain_id": "id", "need_ids": "ids"},
    "object": {"name": "text", "definition": "text", "attributes": "object", "relations": "objects", "operations": "texts", "need_ids": "ids"},
    "capability": {"name": "text", "input_objects": "ids", "output_objects": "ids", "transformation": "text", "criteria": "texts", "need_ids": "ids"},
    "skill": {"name": "text", "slug": "text", "collection": "text", "capabilities": "ids", "triggers": "texts", "non_use": "texts", "tools": "texts", "dependencies": "texts", "permissions": "texts", "authorship": "text", "origin": "text"},
    "skill_revision": {"skill_id": "id", "declared_version": "text", "immutable_origin": "text", "manifest": "object", "license": "text", "validation": "text"},
    "installation": {"skill_revision_id": "id", "destination": "text", "scope": "object", "method": "text", "installed_at": "datetime", "configuration": "object", "installation": "text", "availability": "text"},
    "case": {"task": "text", "context": "object", "inputs": "object", "criteria": "texts", "baseline": "object", "allowed_resources": "texts", "privacy": "object"},
    "evaluation": {"skill_revision_id": "id", "case_ids": "ids", "execution": "object", "environment": "object", "model": "text", "results": "objects", "metrics": "object", "measurement_source": "text"},
    "comparison": {"need_id": "id", "local_revision_id": "id", "candidate_revision_ids": "ids", "eliminators": "texts", "criteria": "texts", "results": "objects", "pros": "texts", "cons": "texts", "confidence": "text"},
    "decision": {"choice": "text", "rejected_alternatives": "texts", "reasons": "texts", "evidence_refs": "evidence", "scope": "object", "authorization_id": "id", "policy_ref": "text"},
    "publication_candidate": {"selected_content": "texts", "origin": "text", "transformations": "texts", "manifest": "object", "rights": "object", "audit": "object", "destination": "text"},
    "publication": {"candidate_id": "id", "declared_version": "text", "package_hash": "text", "authorization_id": "id", "commit": "text", "release": "text", "site": "text", "checks": "objects", "publication": "text"},
    "event": {"session_id": "text", "task_id": "text", "event_type": "text", "occurred_at": "datetime", "refs": "ids", "source_ref": "text"},
    "authorization": {"action": "text", "resources": "texts", "limits": "object", "origin": "text", "valid_from": "datetime", "valid_until": "datetime", "conditions": "texts"},
}
REQUIRED_FIELDS = {kind: COMMON_FIELDS + tuple(fields) for kind, fields in FIELD_TYPES.items()}

# (expected record type, is a list). None means any declared record type.
REFERENCE_FIELDS = {
    "project": {"needs": ("need", True), "sources": ("source", True)},
    "need": {"project_id": ("project", False)},
    "domain": {"need_ids": ("need", True), "module_ids": ("module", True)},
    "module": {"domain_id": ("domain", False), "need_ids": ("need", True)},
    "object": {"need_ids": ("need", True), "module_id": ("module", False), "domain_id": ("domain", False)},
    "capability": {"input_objects": ("object", True), "output_objects": ("object", True), "need_ids": ("need", True)},
    "skill": {"capabilities": ("capability", True), "dependency_skill_ids": ("skill", True)},
    "skill_revision": {"skill_id": ("skill", False)},
    "installation": {"skill_revision_id": ("skill_revision", False)},
    "evaluation": {"skill_revision_id": ("skill_revision", False), "case_ids": ("case", True)},
    "comparison": {"need_id": ("need", False), "local_revision_id": ("skill_revision", False), "candidate_revision_ids": ("skill_revision", True)},
    "decision": {"authorization_id": ("authorization", False), "need_id": ("need", False), "selected_revision_id": ("skill_revision", False), "rejected_revision_ids": ("skill_revision", True)},
    "publication_candidate": {"origin_revision_ids": ("skill_revision", True)},
    "publication": {"candidate_id": ("publication_candidate", False), "authorization_id": ("authorization", False)},
    "event": {"refs": (None, True)},
}
_HEX = re.compile(r"^[0-9a-f]+$")


def _text(value, path):
    if not isinstance(value, str) or not value.strip():
        raise ControlError(f"{path}: expected non-empty text")


def _id(value, path):
    _text(value, path)
    try:
        valid = str(uuid.UUID(value)) == value
    except (ValueError, AttributeError):
        valid = False
    if not valid:
        raise ControlError(f"{path}: expected canonical UUID")


def _timestamp(value, path):
    _text(value, path)
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if result.utcoffset() is None:
            raise ValueError("timezone required")
    except ValueError as exc:
        raise ControlError(f"{path}: expected ISO 8601 timestamp with timezone") from exc
    return result


def _json(value, path="record"):
    if value is None or type(value) in (str, bool, int):
        return
    if type(value) is float and math.isfinite(value):
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str) or not key:
                raise ControlError(f"{path}: object keys must be non-empty strings")
            _json(item, f"{path}.{key}")
        return
    if isinstance(value, list):
        for i, item in enumerate(value):
            _json(item, f"{path}.{i}")
        return
    raise ControlError(f"{path}: expected finite JSON data")


def _typed(value, spec, path):
    if value is None:
        return  # _unknowns checks every null, including nested custom data.
    if spec in ("text", "id", "datetime"):
        {"text": _text, "id": _id, "datetime": _timestamp}[spec](value, path)
    elif spec == "bool":
        if type(value) is not bool:
            raise ControlError(f"{path}: expected boolean")
    elif spec == "object":
        if not isinstance(value, dict):
            raise ControlError(f"{path}: expected object")
    elif spec in ("texts", "ids", "objects", "evidence"):
        if not isinstance(value, list):
            raise ControlError(f"{path}: expected list")
        for i, item in enumerate(value):
            if item is None:
                raise ControlError(f"{path}.{i}: null list entry is not a record value")
            if spec == "texts":
                _text(item, f"{path}.{i}")
            elif spec == "ids":
                _id(item, f"{path}.{i}")
            elif spec == "objects":
                if not isinstance(item, dict):
                    raise ControlError(f"{path}.{i}: expected object")
            elif isinstance(item, str):
                _text(item, f"{path}.{i}")
            elif isinstance(item, dict):
                ref = item.get("source_ref", item.get("path"))
                _text(ref, f"{path}.{i}.source_ref/path")
                if "sha256" in item and (not isinstance(item["sha256"], str) or len(item["sha256"]) != 64 or not _HEX.fullmatch(item["sha256"])):
                    raise ControlError(f"{path}.{i}.sha256: invalid digest")
            else:
                raise ControlError(f"{path}.{i}: expected evidence reference")
        if spec in ("texts", "ids") and len(value) != len(set(value)):
            raise ControlError(f"{path}: duplicate entries")


def _unknowns(record):
    paths = []
    def walk(value, path):
        if value is None:
            paths.append(path)
        elif isinstance(value, dict):
            for key, item in value.items():
                if not path and key in ("unknown_reason", "unknown_reasons"):
                    continue
                walk(item, f"{path}.{key}" if path else key)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                walk(item, f"{path}.{i}")
    walk(record, "")
    reasons = {}
    for key in ("unknown_reason", "unknown_reasons"):
        if key not in record:
            continue
        value = record[key]
        if key == "unknown_reason" and isinstance(value, str):
            _text(value, key)
            if len(paths) != 1:
                raise ControlError("unknown_reason text requires exactly one null field; use a field map")
            reasons[paths[0]] = value
        elif isinstance(value, dict):
            for field, reason in value.items():
                _text(field, key)
                _text(reason, f"{key}.{field}")
                if field in reasons and reasons[field] != reason:
                    raise ControlError(f"{field}: conflicting unknown reasons")
                reasons[field] = reason
        else:
            raise ControlError(f"{key}: expected field-to-reason map")
    if set(paths) != set(reasons):
        raise ControlError("Every null must have its own reason and every reason must identify a null field")


def _provenance(record):
    if "external_fact" in record and type(record["external_fact"]) is not bool:
        raise ControlError("external_fact: expected boolean")
    provenance = record.get("provenance")
    if (record.get("external_fact") is True or "claim_status" in record) and not provenance:
        raise ControlError("External facts require provenance")
    if provenance is None:
        return
    entries = provenance if isinstance(provenance, list) else [provenance]
    if not entries:
        raise ControlError("provenance: expected at least one observation")
    for item in entries:
        if not isinstance(item, dict) or not {"source_ref", "observed_at", "claim_status"} <= item.keys():
            raise ControlError("provenance requires source_ref, observed_at and claim_status")
        _text(item["source_ref"], "provenance.source_ref")
        _timestamp(item["observed_at"], "provenance.observed_at")
        if item["claim_status"] not in ENUMS["claim_status"]:
            raise ControlError("provenance.claim_status: invalid factual state")


def _manifest(manifest):
    if manifest is None:
        return
    if manifest.get("algorithm") != "sha256" or not isinstance(manifest.get("files"), list):
        raise ControlError("manifest requires algorithm=sha256 and files list")
    paths = []
    for item in manifest["files"]:
        if not isinstance(item, dict) or not {"path", "size", "digest"} <= item.keys():
            raise ControlError("manifest file requires path, size and digest")
        path = item["path"]
        _text(path, "manifest.path")
        if path.startswith("/") or "\\" in path or any(p in ("", ".", "..") for p in path.split("/")):
            raise ControlError("manifest path must be normalized and relative")
        if type(item["size"]) is not int or item["size"] < 0:
            raise ControlError("manifest size must be a non-negative integer")
        if not isinstance(item["digest"], str) or len(item["digest"]) != 64 or not _HEX.fullmatch(item["digest"]):
            raise ControlError("manifest file digest must be a SHA-256 hex value")
        paths.append(path)
    if paths != sorted(set(paths)):
        raise ControlError("manifest paths must be unique and sorted")
    if "digest" in manifest:
        value = manifest["digest"]
        if not isinstance(value, str) or len(value) != 64 or not _HEX.fullmatch(value):
            raise ControlError("manifest digest must be a SHA-256 hex value")


def _nonempty(record, *fields):
    for field in fields:
        if not record.get(field):
            raise ControlError(f"{field}: value is necessary for this record invariant")


def _invariants(record):
    kind = record["type"]
    if kind == "source":
        if type(record["complete"]) is not bool or type(record["partial"]) is not bool:
            raise ControlError("Coverage requires explicit complete and partial booleans")
        pagination = record["pagination"]
        if pagination is not None:
            if type(pagination.get("has_more")) is not bool:
                raise ControlError("pagination requires has_more boolean")
            if record["complete"] and pagination["has_more"]:
                raise ControlError("Unfinished pagination cannot be complete")
        if record["complete"] and (record["partial"] or pagination is None):
            raise ControlError("Partial or unknown coverage cannot be complete")
    if kind == "need":
        _nonempty(record, "desired_output", "success_criteria")
    if kind in ("domain", "module", "object", "capability"):
        _nonempty(record, "name", "definition" if kind != "capability" else "transformation", "need_ids")
    if kind == "capability":
        _nonempty(record, "criteria")
    if kind == "skill":
        _nonempty(record, "name", "slug", "capabilities", "triggers", "non_use")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", record["slug"]):
            raise ControlError("slug must use lowercase letters, digits and single hyphens")
    if kind in ("skill_revision", "publication_candidate"):
        _manifest(record["manifest"])
    if kind == "case":
        _nonempty(record, "criteria")
    if kind == "evaluation":
        _nonempty(record, "case_ids", "execution")
        executed = record["execution"].get("executed")
        if type(executed) is not bool:
            raise ControlError("execution.executed must be a boolean")
        for result in record["results"] or []:
            _id(result.get("case_id"), "results.case_id")
            if result["case_id"] not in record["case_ids"]:
                raise ControlError("Result case is outside this evaluation")
            if result.get("outcome") not in ("pass", "fail", "not_run", "inconclusive"):
                raise ControlError("Result outcome must be pass, fail, not_run or inconclusive")
            if not executed and result["outcome"] in ("pass", "fail"):
                raise ControlError("Unexecuted evaluation cannot claim an execution result")
        outcomes = [item["outcome"] for item in record["results"] or []]
        if record.get("validation") == "passed" and (not executed or len(outcomes) != len(record["case_ids"]) or any(v != "pass" for v in outcomes)):
            raise ControlError("Passed validation requires executed, passing results for every case")
        if len({item["case_id"] for item in record["results"] or []}) != len(record["results"] or []):
            raise ControlError("Evaluation contains duplicate case results")
    if kind == "comparison":
        _nonempty(record, "criteria", "candidate_revision_ids")
        if record["local_revision_id"] in record["candidate_revision_ids"]:
            raise ControlError("Local and candidate alternatives must differ")
    if kind == "decision":
        _nonempty(record, "scope", "reasons")
        if not record["authorization_id"] and not record["policy_ref"]:
            raise ControlError("Decision needs a scoped authorization or policy reference")
    if kind == "event" and not (record["session_id"] or record["task_id"]):
        raise ControlError("Operational event needs a session or task reference")
    if kind == "publication" and record["publication"] in ("approved", "publishing", "published"):
        _nonempty(record, "candidate_id", "authorization_id", "package_hash")
    if kind == "authorization":
        _nonempty(record, "resources", "limits", "origin")
        if record["valid_from"] is None:
            raise ControlError("Authorization needs a known validity start")
        if record["valid_until"] and _timestamp(record["valid_until"], "valid_until") < _timestamp(record["valid_from"], "valid_from"):
            raise ControlError("Authorization ends before it starts")
    if record.get("maturity") == "validated":
        scope = record.get("validation_scope")
        if record.get("validation") != "passed" or not isinstance(scope, dict):
            raise ControlError("Validated maturity needs passed validation and validation_scope")
        for field, spec in {"case_ids": "ids", "client": "text", "skill_revision_id": "id", "context": "text"}.items():
            if field not in scope or scope[field] is None:
                raise ControlError(f"validation_scope.{field}: required")
            _typed(scope[field], spec, f"validation_scope.{field}")
        if not scope["case_ids"]:
            raise ControlError("Validated maturity requires scoped test cases")


def _index(records):
    if isinstance(records, Mapping):
        items = list(records.values())
    elif isinstance(records, (list, tuple)):
        items = list(records)
    else:
        raise ControlError("Registry must be a list, tuple or ID-to-record mapping")
    index = {}
    for record in items:
        validate_record(record)
        if record["id"] in index:
            raise ControlError("Registry IDs must be unique")
        index[record["id"]] = record
    if isinstance(records, Mapping) and set(records) != set(index):
        raise ControlError("Registry mapping keys must match record IDs")
    return index


def _reference(value, expected, index, path):
    _id(value, path)
    target = index.get(value)
    if target is None or (expected is not None and target["type"] != expected):
        raise ControlError(f"{path}: missing or wrong-type referenced record")
    return target


def _relations(record, index):
    kind = record["type"]
    for field, (expected, multiple) in REFERENCE_FIELDS.get(kind, {}).items():
        value = record.get(field)
        if value is not None:
            for ref in value if multiple else [value]:
                _reference(ref, expected, index, field)
    for relation in record.get("relations") or []:
        _text(relation.get("relation"), "relations.relation")
        _reference(relation.get("target_id"), None, index, "relations.target_id")
    observations = record.get("provenance") or []
    if isinstance(observations, dict):
        observations = [observations]
    external_refs = [item["source_ref"] for item in observations]
    if kind == "event":
        external_refs.append(record["source_ref"])
    for item in record.get("evidence_refs") or []:
        external_refs.append(item if isinstance(item, str) else item.get("source_ref", item.get("path")))
    for ref in external_refs:
        try:
            uuid.UUID(ref)
        except (ValueError, TypeError, AttributeError):
            continue  # External locators are retained, never dereferenced here.
        _reference(ref, "source", index, "source_ref/evidence_refs")
    if kind == "project":
        for need_id in record["needs"] or []:
            if index[need_id]["project_id"] != record["id"]:
                raise ControlError("Project lists a need belonging to another/unknown project")
    if kind == "domain":
        for module_id in record.get("module_ids") or []:
            if index[module_id]["domain_id"] != record["id"]:
                raise ControlError("Domain lists a module belonging to another domain")
    if kind == "evaluation":
        for result in record["results"] or []:
            if "criteria" in result and result["criteria"] != index[result["case_id"]]["criteria"]:
                raise ControlError("Evaluation result changed the registered case criteria")
    if kind == "comparison":
        alternatives = set(record["candidate_revision_ids"])
        if record["local_revision_id"]:
            alternatives.add(record["local_revision_id"])
        for result in record["results"] or []:
            if result.get("skill_revision_id") not in alternatives:
                raise ControlError("Comparison result is outside its declared alternatives")
            if "criteria" in result and result["criteria"] != record["criteria"]:
                raise ControlError("Comparison alternatives must use the same criteria")
    if record.get("maturity") == "validated":
        scope = record["validation_scope"]
        reviewed = _reference(scope["skill_revision_id"], "skill_revision", index, "validation_scope.skill_revision_id")
        for case_id in scope["case_ids"]:
            _reference(case_id, "case", index, "validation_scope.case_ids")
        if kind == "skill" and reviewed["skill_id"] != record["id"]:
            raise ControlError("Validation scope belongs to another skill")
        if kind == "skill_revision" and reviewed["id"] != record["id"]:
            raise ControlError("Validation scope belongs to another revision")
    if kind == "publication" and record["publication"] in ("approved", "publishing", "published"):
        candidate = index[record["candidate_id"]]
        authorization = index[record["authorization_id"]]
        if not candidate["manifest"] or candidate["manifest"].get("digest") != record["package_hash"]:
            raise ControlError("Publication package differs from its candidate manifest")
        if authorization["limits"].get("package_hash") != record["package_hash"]:
            raise ControlError("Publication authorization must bind the exact package hash")
        if candidate["id"] not in authorization["resources"]:
            raise ControlError("Publication candidate is outside authorization resources")
        if not candidate["audit"] or candidate["audit"].get("status") != "passed":
            raise ControlError("Publication candidate has not passed its audit")
        if record["publication"] == "published" and (not record["checks"] or any(c.get("status") != "passed" for c in record["checks"])):
            raise ControlError("Published state requires passing receipt checks")


def validate_record(record, registry=None):
    """Return the same record or raise ControlError; never mutate input.

    Unknowns use dotted paths in unknown_reasons (or an unknown_reason mapping).
    A singular unknown_reason string is accepted only for exactly one null.
    Without a registry, cross-record references are checked syntactically only.
    """
    if not isinstance(record, dict):
        raise ControlError("Record must be a JSON object")
    _json(record)
    kind = record.get("type")
    if not isinstance(kind, str) or kind not in FIELD_TYPES:
        raise ControlError("Unknown record type")
    missing = set(REQUIRED_FIELDS[kind]) - record.keys()
    if missing:
        raise ControlError("Missing fields: " + ", ".join(sorted(missing)))
    if record["schema_version"] != SCHEMA_VERSION:
        raise ControlError("Unsupported record schema_version")
    _id(record["id"], "id")
    if type(record["revision"]) is not int or record["revision"] < 1:
        raise ControlError("revision must be a positive integer")
    if _timestamp(record["updated_at"], "updated_at") < _timestamp(record["created_at"], "created_at"):
        raise ControlError("updated_at precedes created_at")
    for field, spec in FIELD_TYPES[kind].items():
        _typed(record[field], spec, field)
    for field, (_, multiple) in REFERENCE_FIELDS.get(kind, {}).items():
        if field in record:
            _typed(record[field], "ids" if multiple else "id", field)
    if "relations" in record:
        _typed(record["relations"], "objects", "relations")
        for relation in record["relations"] or []:
            _text(relation.get("relation"), "relations.relation")
            _id(relation.get("target_id"), "relations.target_id")
    for field, values in ENUMS.items():
        if field in record and record[field] not in values:
            raise ControlError(f"{field}: invalid enum value")
    _unknowns(record)
    _provenance(record)
    _invariants(record)
    if registry is not None:
        index = _index(registry)
        if record["id"] in index and index[record["id"]] != record:
            raise ControlError("Record conflicts with its registry ID")
        index[record["id"]] = record
        _relations(record, index)
    return record


def validate_registry(records):
    """Validate unique IDs, typed references and Annex A relations; return input."""
    index = _index(records)
    for record in index.values():
        _relations(record, index)
    return records


def new_record(kind, **fields):
    """Create a complete, locally valid revision-1 record with a new stable UUID."""
    if not isinstance(kind, str) or kind not in FIELD_TYPES:
        raise ControlError("Unknown record type")
    if set(fields) & set(COMMON_FIELDS):
        raise ControlError("new_record generates identity and revision metadata")
    timestamp = now()
    record = {"schema_version": SCHEMA_VERSION, "id": str(uuid.uuid4()), "type": kind,
              "created_at": timestamp, "updated_at": timestamp, "revision": 1, **fields}
    return validate_record(record)
