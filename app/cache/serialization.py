import json
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId

MISSING_MARKER = "__missing__"


def _serialize_value(value: Any) -> Any:
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _serialize_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    return value


def country_document_to_json(document: dict) -> str:
    return json.dumps(_serialize_value(document))


def _deserialize_value(key: str, value: Any) -> Any:
    if key == "_id" and isinstance(value, str) and ObjectId.is_valid(value):
        return ObjectId(value)
    if key in ("createdAt", "updatedAt") and isinstance(value, str):
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed
    if isinstance(value, dict):
        return {nested_key: _deserialize_value(nested_key, nested) for nested_key, nested in value.items()}
    if isinstance(value, list):
        return value
    return value


def country_document_from_json(payload: str) -> dict | None:
    data = json.loads(payload)
    if data.get(MISSING_MARKER):
        return None

    return {
        key: _deserialize_value(key, value)
        for key, value in data.items()
    }


def missing_country_json() -> str:
    return json.dumps({MISSING_MARKER: True})
