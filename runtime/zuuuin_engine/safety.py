"""Explicit public projection; never export a private record by subtraction."""
import copy
import re
import uuid
from .state import ControlError

PUBLIC_FIELDS = frozenset(("name", "slug", "description", "collection", "version", "maturity", "license", "examples", "requires", "capability_descriptions"))
PRIVATE_KEYS = frozenset(("project_id", "project_ids", "source_ref", "source_refs", "provenance", "private_root", "destination", "profile", "evidence_refs", "source_chat_id", "source_chat_url"))


def public_projection(record, allowed_fields, public_id, private_identifiers=()):
    """Return only explicitly selected public fields, or reject the whole projection.

    Contextual confidentiality still requires a separate publication audit.
    """
    if not allowed_fields:
        return {}
    if record.get("type") not in ("skill", "capability", "domain", "module", "object"):
        raise ControlError("Project records and private operational data cannot be projected")
    if not isinstance(allowed_fields, list) or not set(allowed_fields) <= PUBLIC_FIELDS:
        raise ControlError("Private or unknown field requested for export")
    try:
        valid_id = str(uuid.UUID(public_id)) == public_id
    except (ValueError, TypeError, AttributeError):
        valid_id = False
    if not valid_id or public_id == record.get("id"):
        raise ControlError("A separate public UUID is required")
    denied = set(private_identifiers) | {str(record.get("id", ""))}
    def inspect(value):
        if isinstance(value, dict):
            if set(value) & PRIVATE_KEYS:
                raise ControlError("Private nested field refused")
            for item in value.values():
                inspect(item)
        elif isinstance(value, (tuple, list)):
            for item in value:
                inspect(item)
        elif isinstance(value, str):
            if re.search(r"/Users/|ZUUUIN_PRIVATE_CANARY_|-----BEGIN .*PRIVATE KEY-----", value) or any(x and x in value for x in denied):
                raise ControlError("Potentially private value refused")
    result = {"id": public_id}
    for field in allowed_fields:
        if field not in record:
            raise ControlError("Selected public field is absent")
        inspect(record[field])
        result[field] = copy.deepcopy(record[field])
    return result
