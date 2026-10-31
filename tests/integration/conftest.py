import asyncio

import pytest
from pymongo import AsyncMongoClient
from pymongo.errors import ServerSelectionTimeoutError

from app.config import settings
from app.database import connection as db_connection
from app.database.indexes import create_indexes


@pytest.fixture(scope="session")
def mongo_reachable() -> None:
    async def ping() -> None:
        client = AsyncMongoClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=3000,
        )
        try:
            await client.admin.command("ping")
        finally:
            await client.close()

    try:
        asyncio.run(ping())
    except (ServerSelectionTimeoutError, OSError) as error:
        pytest.skip(f"MongoDB not available for integration tests: {error}")


@pytest.fixture
async def mongo_countries(mongo_reachable, monkeypatch):
    monkeypatch.setattr(settings, "MONGODB_DATABASE", settings.MONGODB_TEST_DATABASE)
    monkeypatch.setattr(settings, "CACHE_ENABLED", False)

    db_connection._client = None
    db_connection._database = None

    await db_connection.connect_to_database()
    await create_indexes()

    collection = db_connection.get_database()["countries"]
    await collection.delete_many({})

    yield collection

    await collection.delete_many({})
    await db_connection.close_database_connection()
    db_connection._client = None
    db_connection._database = None
