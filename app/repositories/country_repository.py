from bson import ObjectId

from app.database.connection import get_database
from datetime import datetime, timezone


def get_collection():
    return get_database()["countries"]


async def get_countries(page: int, page_size: int):
    collection = get_collection()

    skip = (page - 1) * page_size

    items = await collection.find(
        {"isActive": {"$ne": False}}
    ).sort(
        "name.common", 1
    ).skip(
        skip
    ).limit(
        page_size
    ).to_list(length=page_size)

    total_count = await collection.count_documents(
        {"isActive": {"$ne": False}}
    )

    return items, total_count


async def get_country_by_code(code: str):
    collection = get_collection()

    return await collection.find_one({
        "code": code.upper(),
        "isActive": {"$ne": False}
    })


async def get_countries_by_language(language: str):
    collection = get_collection()

    return await collection.find({
        "languages.name": {
            "$regex": f"^{language}$",
            "$options": "i"
        },
        "isActive": {"$ne": False}
    }).to_list(length=None)


async def get_nearby_countries(
    latitude: float,
    longitude: float,
    max_distance: float
):
    collection = get_collection()

    pipeline = [
        {
            "$geoNear": {
                "near": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                },
                "distanceField": "distanceMeters",
                "maxDistance": max_distance * 1000,
                "spherical": True,
                "query": {"isActive": {"$ne": False}}
            }
        }
    ]

    cursor = await collection.aggregate(pipeline)
    return await cursor.to_list(length=None)


async def get_countries_grouped_by_currency():
    collection = get_collection()

    pipeline = [
        {
            "$match": {
                "isActive": {"$ne": False},
                "currencies.0": {"$exists": True}
            }
        },
        {
            "$unwind": "$currencies"
        },
        {
            "$group": {
                "_id": "$currencies.code",
                "name": {
                    "$first": "$currencies.name"
                },
                "symbol": {
                    "$first": "$currencies.symbol"
                },
                "countries": {
                    "$push": "$$ROOT"
                },
                "countryCount": {
                    "$sum": 1
                }
            }
        },
        {
            "$sort": {
                "_id": 1
            }
        }
    ]

    cursor = await collection.aggregate(pipeline)
    return await cursor.to_list(length=None)


async def add_country(country: dict):
    collection = get_collection()

    result = await collection.insert_one(country)

    country["_id"] = result.inserted_id

    return country


async def update_country_name(
    code: str,
    common_name: str,
    official_name: str
):
    collection = get_collection()

    await collection.update_one(
        {"code": code.upper()},
        {
            "$set": {
                "name.common": common_name,
                "name.official": official_name,
                "updatedAt": datetime.now(timezone.utc),
                "nameSource": "MANUAL"
            }
        }
    )

    return await collection.find_one({
        "code": code.upper()
    })