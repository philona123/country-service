from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services import ingestion_service


def _valid_raw_country(code: str = "IN", name: str = "India") -> dict:
    return {
        "alpha2Code": code,
        "name": name,
        "officialName": f"Republic of {name}",
        "latlng": [20.0, 77.0],
    }


@pytest.mark.asyncio
async def test_ingest_countries_bulk_writes_and_invalidates_cache():
    raw_countries = [_valid_raw_country()]

    mock_client = MagicMock()
    mock_client.fetch_countries = AsyncMock(return_value=raw_countries)

    bulk_result = MagicMock()
    bulk_result.upserted_count = 1
    bulk_result.modified_count = 0

    with patch(
        "app.services.ingestion_service.CountryAPIClient",
        return_value=mock_client,
    ):
        with patch(
            "app.services.ingestion_service.country_repository.bulk_upsert_countries",
            new_callable=AsyncMock,
            return_value=bulk_result,
        ) as bulk_upsert:
            with patch(
                "app.services.ingestion_service.invalidate_all_country_entities",
                new_callable=AsyncMock,
            ) as invalidate:
                await ingestion_service.ingest_countries()

    mock_client.fetch_countries.assert_awaited_once()
    bulk_upsert.assert_awaited_once()
    assert len(bulk_upsert.await_args.args[0]) == 1
    invalidate.assert_awaited_once()


@pytest.mark.asyncio
async def test_ingest_countries_skips_invalid_and_still_writes_valid():
    raw_countries = [
        _valid_raw_country("IN", "India"),
        {"name": "Missing alpha2 code"},
    ]

    mock_client = MagicMock()
    mock_client.fetch_countries = AsyncMock(return_value=raw_countries)

    bulk_result = MagicMock()
    bulk_result.upserted_count = 1
    bulk_result.modified_count = 0

    with patch(
        "app.services.ingestion_service.CountryAPIClient",
        return_value=mock_client,
    ):
        with patch(
            "app.services.ingestion_service.country_repository.bulk_upsert_countries",
            new_callable=AsyncMock,
            return_value=bulk_result,
        ) as bulk_upsert:
            with patch(
                "app.services.ingestion_service.invalidate_all_country_entities",
                new_callable=AsyncMock,
            ) as invalidate:
                await ingestion_service.ingest_countries()

    assert len(bulk_upsert.await_args.args[0]) == 1
    invalidate.assert_awaited_once()


@pytest.mark.asyncio
async def test_ingest_countries_does_not_write_when_all_invalid():
    raw_countries = [{"name": "No code"}]

    mock_client = MagicMock()
    mock_client.fetch_countries = AsyncMock(return_value=raw_countries)

    with patch(
        "app.services.ingestion_service.CountryAPIClient",
        return_value=mock_client,
    ):
        with patch(
            "app.services.ingestion_service.country_repository.bulk_upsert_countries",
            new_callable=AsyncMock,
            return_value=None,
        ) as bulk_upsert:
            with patch(
                "app.services.ingestion_service.invalidate_all_country_entities",
                new_callable=AsyncMock,
            ) as invalidate:
                await ingestion_service.ingest_countries()

    bulk_upsert.assert_awaited_once_with([])
    invalidate.assert_not_awaited()
