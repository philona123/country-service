from app.cache.country_cache import invalidate_all_country_entities
from app.config import settings
from app.ingestion.client import CountryAPIClient
from app.ingestion.transformer import transform_country
from app.repositories import country_repository


async def ingest_countries() -> None:
    client = CountryAPIClient(settings.COUNTRY_API_URL)
    raw_countries = await client.fetch_countries()
    operations = []
    valid_count = 0
    failed_count = 0
    for raw_country in raw_countries:
        try:
            country = transform_country(raw_country)
            operations.append(country_repository.country_upsert_operation(country))
            valid_count += 1

        except Exception as error:
            failed_count += 1
            print(f"Country ingestion failed: {error}")

    result = await country_repository.bulk_upsert_countries(operations)
    if result is not None:
        print(
            {
                "fetched": len(raw_countries),
                "valid": valid_count,
                "failed": failed_count,
                "inserted": result.upserted_count,
                "modified": result.modified_count,
            }
        )
        await invalidate_all_country_entities()
