from datetime import datetime, timezone

from pymongo import UpdateOne

from app.config import settings
from app.database.connection import get_database
from app.ingestion.client import CountryAPIClient
from app.ingestion.transformer import transform_country


async def ingest_countries() -> None:
    countries_collection = get_database()["countries"]
    client = CountryAPIClient(settings.COUNTRY_API_URL)
    raw_countries = await client.fetch_countries()
    operations = []
    valid_count = 0
    failed_count = 0

    for raw_country in raw_countries:
        try:
            country = transform_country(raw_country)
            operations.append(
                UpdateOne(
                    {"code": country["code"]},
                    {
                        "$set": country,
                        "$setOnInsert": {
                            "createdAt": datetime.now(timezone.utc)
                        },
                    },
                    upsert=True,
                )
            )
            valid_count += 1

        except Exception as error:
            failed_count += 1
            print(f"Country ingestion failed: {error}")

    if operations:
        result = await countries_collection.bulk_write(
            operations,
            ordered=False,
        )
        print(
            {
                "fetched": len(raw_countries),
                "valid": valid_count,
                "failed": failed_count,
                "inserted": result.upserted_count,
                "modified": result.modified_count,
            }
        )
