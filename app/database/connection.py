import asyncio

from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import ServerSelectionTimeoutError

from app.config import settings

_client: AsyncMongoClient | None = None
_database: AsyncDatabase | None = None

_MONGO_START_HINT = (
    f"Cannot connect to MongoDB at {settings.MONGODB_URI}.\n"
    "Start it from the project root:\n"
    "  docker compose up -d\n"
    "If the container is crash-looping or the name is stuck:\n"
    "  ./scripts/reset-mongo.sh"
)


def get_client() -> AsyncMongoClient:
    global _client
    if _client is None:
        _client = AsyncMongoClient(settings.MONGODB_URI)
    return _client


def get_database() -> AsyncDatabase:
    global _database
    if _database is None:
        _database = get_client()[settings.MONGODB_DATABASE]
    return _database


async def connect_to_database() -> None:
    last_error: Exception | None = None
    client = get_client()
    for attempt in range(1, 6):
        try:
            await client.admin.command("ping")
            print("Connected to MongoDB")
            return
        except ServerSelectionTimeoutError as error:
            last_error = error
            if attempt < 5:
                print(f"MongoDB not ready (attempt {attempt}/5), retrying...")
                await asyncio.sleep(2)

    raise RuntimeError(_MONGO_START_HINT) from last_error


async def close_database_connection() -> None:
    global _client, _database
    if _client is not None:
        await _client.close()
        _client = None
        _database = None
        print("Disconnected from MongoDB")
