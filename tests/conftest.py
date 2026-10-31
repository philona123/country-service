from datetime import datetime, timezone

import pytest
from bson import ObjectId


@pytest.fixture
def country_id() -> str:
    return "507f1f77bcf86cd799439011"


@pytest.fixture
def sample_country(country_id: str) -> dict:
    return {
        "_id": ObjectId(country_id),
        "code": "IN",
        "name": {
            "common": "India",
            "official": "Republic of India",
            "native": "भारत",
        },
        "alpha3Code": "IND",
        "capital": ["New Delhi"],
        "region": "Asia",
        "subregion": "Southern Asia",
        "population": 100,
        "area": 3287263.0,
        "coordinates": {"latitude": 20.0, "longitude": 77.0},
        "currencies": [{"code": "INR", "name": "Rupee", "symbol": "₹"}],
        "languages": [{"code": "hin", "name": "Hindi", "nativeName": "हिन्दी"}],
        "isActive": True,
        "sourceType": "MANUAL",
        "createdAt": datetime(2024, 1, 1, tzinfo=timezone.utc),
        "updatedAt": datetime(2024, 1, 2, tzinfo=timezone.utc),
    }
