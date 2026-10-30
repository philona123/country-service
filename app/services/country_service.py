from app.repositories import country_repository


async def get_countries(page: int, page_size: int):
    if page < 1:
        raise ValueError("Page must be greater than 0")

    if page_size < 1 or page_size > 100:
        raise ValueError("Page size must be between 1 and 100")

    items, total_count = await country_repository.get_countries(
        page,
        page_size
    )

    total_pages = (
        (total_count + page_size - 1) // page_size
    )

    return {
        "items": items,
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


async def get_country_by_code(code: str):
    if not code or len(code) != 2:
        raise ValueError("Country code must contain 2 characters")

    return await country_repository.get_country_by_code(code)

async def get_country_by_id(id: str):
    if not id:
        raise ValueError("Country ID cannot be empty")

    return await country_repository.get_country_by_id(id)

async def get_countries_by_language(language: str):
    if not language.strip():
        raise ValueError("Language cannot be empty")

    return await country_repository.get_countries_by_language(
        language.strip()
    )


async def get_nearby_countries(
    latitude: float,
    longitude: float,
    max_distance: float
):
    if not -90 <= latitude <= 90:
        raise ValueError("Invalid latitude")

    if not -180 <= longitude <= 180:
        raise ValueError("Invalid longitude")

    if max_distance <= 0:
        raise ValueError("Maximum distance must be greater than 0")

    return await country_repository.get_nearby_countries(
        latitude,
        longitude,
        max_distance
    )


async def get_countries_grouped_by_currency():
    return await country_repository.get_countries_grouped_by_currency()


async def add_country(code: str, common_name: str, official_name: str):
    from datetime import datetime, timezone

    code = code.upper().strip()

    if len(code) != 2:
        raise ValueError("Country code must contain 2 characters")

    if not common_name.strip() or not official_name.strip():
        raise ValueError("Country names cannot be empty")

    existing = await country_repository.get_country_by_code(code)

    if existing:
        raise ValueError(f"Country {code} already exists")

    country = {
        "code": code,
        "name": {
            "common": common_name.strip(),
            "official": official_name.strip()
        },
        "alpha3Code": None,
        "capital": [],
        "region": None,
        "subregion": None,
        "population": 0,
        "area": None,
        "coordinates": None,
        "location": None,
        "currencies": [],
        "languages": [],
        "isActive": True,
        "sourceType": "MANUAL",
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc)
    }

    return await country_repository.add_country(country)


async def update_country_name(
    code: str,
    common_name: str,
    official_name: str
):
    if not common_name.strip() or not official_name.strip():
        raise ValueError("Country names cannot be empty")

    country = await country_repository.get_country_by_code(code)

    if not country:
        raise ValueError(f"Country {code} not found")

    return await country_repository.update_country_name(
        code,
        common_name.strip(),
        official_name.strip()
    )