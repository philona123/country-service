from app.repositories import country_repository
from app.schemas.inputs import (
    AddCountryInput,
    CountryCodeInput,
    CountryIdInput,
    LanguageInput,
    NearbyInput,
    PaginationInput,
    UpdateCountryInput,
)
from app.schemas.validation import parse_input
from app.utils.country import build_country_document, build_country_update_patch


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


async def add_country(data: AddCountryInput):
    existing = await country_repository.get_country_by_code(data.code)
    if existing:
        raise ValueError(f"Country {data.code} already exists")
    return await country_repository.add_country(build_country_document(data))


async def update_country(data: UpdateCountryInput):
    country = await country_repository.get_country_by_code(data.code)
    if not country:
        raise ValueError(f"Country {data.code} not found")
    patch = build_country_update_patch(data)
    return await country_repository.update_country(data.code, patch)
