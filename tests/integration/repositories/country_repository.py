import pytest
from bson import ObjectId

from app.repositories import country_repository

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_get_country_by_code_reads_from_mongo(mongo_countries, sample_country):
    await mongo_countries.insert_one(sample_country)

    country = await country_repository.get_country_by_code("IN")

    assert country is not None
    assert country["code"] == "IN"
    assert country["name"]["common"] == "India"


@pytest.mark.asyncio
async def test_get_country_by_id_reads_from_mongo(mongo_countries, sample_country, country_id):
    await mongo_countries.insert_one(sample_country)

    country = await country_repository.get_country_by_id(country_id)

    assert country is not None
    assert country["_id"] == ObjectId(country_id)


@pytest.mark.asyncio
async def test_get_countries_pagination_and_sort(mongo_countries, sample_country):
    brazil = {
        **sample_country,
        "_id": ObjectId(),
        "code": "BR",
        "name": {
            "common": "Brazil",
            "official": "Federative Republic of Brazil",
        },
    }
    await mongo_countries.insert_many([brazil, sample_country])

    items, total_count = await country_repository.get_countries(page=1, page_size=10)

    assert total_count == 2
    assert [item["code"] for item in items] == ["BR", "IN"]


@pytest.mark.asyncio
async def test_get_countries_by_language_case_insensitive(mongo_countries, sample_country):
    await mongo_countries.insert_one(sample_country)

    matches = await country_repository.get_countries_by_language("hindi")

    assert len(matches) == 1
    assert matches[0]["code"] == "IN"


@pytest.mark.asyncio
async def test_bulk_upsert_countries_writes_to_mongo(mongo_countries):
    document = {
        "code": "TS",
        "name": {"common": "Teststan", "official": "Republic of Teststan"},
        "population": 1,
        "currencies": [],
        "languages": [{"name": "Testian"}],
        "isActive": True,
    }
    operations = [country_repository.country_upsert_operation(document)]

    result = await country_repository.bulk_upsert_countries(operations)

    assert result is not None
    assert result.upserted_count == 1

    stored = await mongo_countries.find_one({"code": "TS"})
    assert stored is not None
    assert stored["name"]["common"] == "Teststan"


@pytest.mark.asyncio
async def test_get_nearby_countries_uses_geo_index(mongo_countries, sample_country):
    delhi = {
        **sample_country,
        "location": {"type": "Point", "coordinates": [77.2090, 28.6139]},
    }
    mumbai = {
        **sample_country,
        "_id": ObjectId(),
        "code": "MH",
        "name": {"common": "Mumbai Region", "official": "Mumbai Region"},
        "location": {"type": "Point", "coordinates": [72.8777, 19.0760]},
    }
    await mongo_countries.insert_many([delhi, mumbai])

    nearby = await country_repository.get_nearby_countries(
        latitude=28.6139,
        longitude=77.2090,
        max_distance=1500,
    )

    assert len(nearby) >= 1
    assert nearby[0]["code"] == "IN"
    assert nearby[0]["distanceMeters"] == pytest.approx(0, abs=100)
