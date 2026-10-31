from datetime import datetime, timezone

from bson import ObjectId

from app.cache.serialization import (
    country_document_from_json,
    country_document_to_json,
    missing_country_json,
)


def test_country_document_json_round_trip():
    original = {
        "_id": ObjectId(),
        "code": "IN",
        "updatedAt": datetime(2024, 6, 1, 12, 0, tzinfo=timezone.utc),
        "name": {"common": "India"},
    }

    restored = country_document_from_json(country_document_to_json(original))

    assert isinstance(restored["_id"], ObjectId)
    assert restored["code"] == "IN"
    assert restored["updatedAt"] == original["updatedAt"]


def test_missing_country_json_decodes_to_none():
    assert country_document_from_json(missing_country_json()) is None
