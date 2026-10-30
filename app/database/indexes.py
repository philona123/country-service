from app.database.connection import get_database


async def create_indexes() -> None:
    collection = get_database()["countries"]

    await collection.create_index("code", unique=True)
    await collection.create_index("name.common")
    await collection.create_index("languages.name")
    await collection.create_index("currencies.code")
    await collection.create_index([("location", "2dsphere")])
