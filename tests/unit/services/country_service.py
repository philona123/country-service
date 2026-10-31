from unittest.mock import AsyncMock, patch

import pytest
from bson import ObjectId

from app.cache.country_cache import CACHE_MISS
from app.schemas.inputs import AddCountryInput, UpdateCountryInput
from app.schemas.validation import parse_input
from app.services import country_service


@pytest.mark.asyncio
async def test_get_country_by_code_returns_cache_without_db(sample_country):
    with patch(
        "app.services.country_service.country_cache.get_by_code",
        new_callable=AsyncMock,
        return_value=sample_country,
    ) as cache_get:
        with patch(
            "app.services.country_service.country_repository.get_country_by_code",
            new_callable=AsyncMock,
        ) as repo_get:
            result = await country_service.get_country_by_code("IN")

    assert result is sample_country
    cache_get.assert_awaited_once_with("IN")
    repo_get.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_country_by_code_loads_and_caches_on_miss(sample_country):
    with patch(
        "app.services.country_service.country_cache.get_by_code",
        new_callable=AsyncMock,
        return_value=CACHE_MISS,
    ):
        with patch(
            "app.services.country_service.country_repository.get_country_by_code",
            new_callable=AsyncMock,
            return_value=sample_country,
        ) as repo_get:
            with patch(
                "app.services.country_service.country_cache.put",
                new_callable=AsyncMock,
            ) as cache_put:
                result = await country_service.get_country_by_code("in")

    assert result is sample_country
    repo_get.assert_awaited_once_with("IN")
    cache_put.assert_awaited_once_with(sample_country, code="IN")


@pytest.mark.asyncio
async def test_get_country_by_id_cache_hit(sample_country, country_id):
    with patch(
        "app.services.country_service.country_cache.get_by_id",
        new_callable=AsyncMock,
        return_value=sample_country,
    ):
        with patch(
            "app.services.country_service.country_repository.get_country_by_id",
            new_callable=AsyncMock,
        ) as repo_get:
            result = await country_service.get_country_by_id(country_id)

    assert result is sample_country
    repo_get.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_countries_computes_total_pages():
    with patch(
        "app.services.country_service.country_repository.get_countries",
        new_callable=AsyncMock,
        return_value=([{"code": "IN"}], 25),
    ):
        result = await country_service.get_countries(page=2, page_size=10)

    assert result["total_count"] == 25
    assert result["total_pages"] == 3
    assert result["page"] == 2


@pytest.mark.asyncio
async def test_add_country_raises_when_code_exists(sample_country):
    data = parse_input(
        AddCountryInput,
        code="IN",
        common_name="India",
        official_name="Republic of India",
    )
    with patch(
        "app.services.country_service.country_repository.get_country_by_code",
        new_callable=AsyncMock,
        return_value=sample_country,
    ):
        with patch(
            "app.services.country_service.country_repository.add_country",
            new_callable=AsyncMock,
        ) as repo_add:
            with pytest.raises(ValueError, match="already exists"):
                await country_service.add_country(data)

    repo_add.assert_not_awaited()


@pytest.mark.asyncio
async def test_add_country_persists_and_caches(sample_country):
    data = parse_input(
        AddCountryInput,
        code="XX",
        common_name="Example",
        official_name="Republic of Example",
    )
    created = {**sample_country, "code": "XX", "_id": ObjectId()}

    with patch(
        "app.services.country_service.country_repository.get_country_by_code",
        new_callable=AsyncMock,
        return_value=None,
    ):
        with patch(
            "app.services.country_service.country_repository.add_country",
            new_callable=AsyncMock,
            return_value=created,
        ) as repo_add:
            with patch(
                "app.services.country_service.country_cache.put",
                new_callable=AsyncMock,
            ) as cache_put:
                result = await country_service.add_country(data)

    assert result is created
    repo_add.assert_awaited_once()
    cache_put.assert_awaited_once_with(created)


@pytest.mark.asyncio
async def test_update_country_raises_when_not_found():
    data = parse_input(UpdateCountryInput, code="XX", population=1)

    with patch(
        "app.services.country_service.country_repository.get_country_by_code",
        new_callable=AsyncMock,
        return_value=None,
    ):
        with pytest.raises(ValueError, match="not found"):
            await country_service.update_country(data)


@pytest.mark.asyncio
async def test_update_country_persists_and_refreshes_cache(sample_country):
    data = parse_input(UpdateCountryInput, code="IN", population=999)
    updated = {**sample_country, "population": 999}

    with patch(
        "app.services.country_service.country_repository.get_country_by_code",
        new_callable=AsyncMock,
        return_value=sample_country,
    ):
        with patch(
            "app.services.country_service.country_repository.update_country",
            new_callable=AsyncMock,
            return_value=updated,
        ) as repo_update:
            with patch(
                "app.services.country_service.country_cache.put",
                new_callable=AsyncMock,
            ) as cache_put:
                result = await country_service.update_country(data)

    assert result["population"] == 999
    repo_update.assert_awaited_once()
    assert repo_update.await_args.args[0] == "IN"
    cache_put.assert_awaited_once_with(updated)
