from bson import ObjectId

from app.database.connection import get_database


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

async def get_country_by_id(id: str):
    collection = get_collection()
    return await collection.find_one({
        "_id": ObjectId(id),
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

# Efficient database query that groups countries by currency.
async def get_countries_grouped_by_currency():
    collection = get_collection()

    # Project only fields needed for GraphQL before unwind/group to cut memory and wire size.
    country_summary_projection = {
        "_id": 1,
        "code": 1,
        "name": 1,
        "alpha3Code": 1,
        "capital": 1,
        "region": 1,
        "subregion": 1,
        "population": 1,
        "area": 1,
        "coordinates": 1,
        "languages": 1,
        "currencies": 1,
    }

    pipeline = [
        {
            "$match": {
                "isActive": {"$ne": False},
                "currencies.0": {"$exists": True},
            }
        },
        {"$project": country_summary_projection},
        {"$unwind": "$currencies"},
        {
            "$group": {
                "_id": "$currencies.code",
                "name": {"$first": "$currencies.name"},
                "symbol": {"$first": "$currencies.symbol"},
                "countryCount": {"$sum": 1},
                "countries": {
                    "$push": {
                        "_id": "$_id",
                        "code": "$code",
                        "name": "$name",
                        "alpha3Code": "$alpha3Code",
                        "capital": "$capital",
                        "region": "$region",
                        "subregion": "$subregion",
                        "population": "$population",
                        "area": "$area",
                        "coordinates": "$coordinates",
                        "languages": "$languages",
                        "currencies": "$currencies",
                    }
                },
            }
        },
        {"$sort": {"_id": 1}},
    ]

    cursor = await collection.aggregate(pipeline)
    return await cursor.to_list(length=None)


async def add_country(country: dict):
    collection = get_collection()

    result = await collection.insert_one(country)

    country["_id"] = result.inserted_id

    return country


async def update_country(code: str, patch: dict):
    collection = get_collection()

    await collection.update_one(
        {"code": code.upper(), "isActive": {"$ne": False}},
        {"$set": patch},
    )

    return await collection.find_one({
        "code": code.upper(),
        "isActive": {"$ne": False},
    })
