from datetime import datetime, timezone

from app.repositories import country_repository
from app.schemas.inputs import (
    AddCountryInput,
    CountryCodeInput,
    CountryIdInput,
    LanguageInput,
    NearbyInput,
    PaginationInput,
    UpdateCountryNameInput,
)
from app.schemas.validation import parse_input


async def get_countries(page: int, page_size: int):
    params = parse_input(PaginationInput, page=page, page_size=page_size)
    items, total_count = await country_repository.get_countries(
        params.page,
        params.page_size,
    )
    total_pages = (total_count + params.page_size - 1) // params.page_size
    return {
        "items": items,
        "total_count": total_count,
        "page": params.page,
        "page_size": params.page_size,
        "total_pages": total_pages,
    }


async def get_country_by_code(code: str):
    params = parse_input(CountryCodeInput, code=code)
    return await country_repository.get_country_by_code(params.code)


async def get_country_by_id(id: str):
    params = parse_input(CountryIdInput, id=id)
    return await country_repository.get_country_by_id(params.id)


async def get_countries_by_language(language: str):
    params = parse_input(LanguageInput, language=language)
    return await country_repository.get_countries_by_language(params.language)


async def get_nearby_countries(
    latitude: float,
    longitude: float,
    max_distance: float,
):
    params = parse_input(
        NearbyInput,
        latitude=latitude,
        longitude=longitude,
        max_distance=max_distance,
    )
    return await country_repository.get_nearby_countries(
        params.latitude,
        params.longitude,
        params.max_distance,
    )


async def get_countries_grouped_by_currency():
    return await country_repository.get_countries_grouped_by_currency()


async def add_country(code: str, common_name: str, official_name: str):
    data = parse_input(
        AddCountryInput,
        code=code,
        common_name=common_name,
        official_name=official_name,
    )

    existing = await country_repository.get_country_by_code(data.code)

    if existing:
        raise ValueError(f"Country {data.code} already exists")

    country = {
        "code": data.code,
        "name": {
            "common": data.common_name,
            "official": data.official_name,
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
        "updatedAt": datetime.now(timezone.utc),
    }

    return await country_repository.add_country(country)


async def update_country_name(
    code: str,
    common_name: str,
    official_name: str,
):
    data = parse_input(
        UpdateCountryNameInput,
        code=code,
        common_name=common_name,
        official_name=official_name,
    )

    country = await country_repository.get_country_by_code(data.code)

    if not country:
        raise ValueError(f"Country {data.code} not found")

    return await country_repository.update_country_name(
        data.code,
        data.common_name,
        data.official_name,
    )
