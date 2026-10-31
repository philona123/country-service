import pytest

from app.services import country_service

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_get_country_by_code_through_service_and_repository(
    mongo_countries,
    sample_country,
):
    await mongo_countries.insert_one(sample_country)

    country = await country_service.get_country_by_code("IN")

    assert country is not None
    assert country["code"] == "IN"
