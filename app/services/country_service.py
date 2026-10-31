import logging

from app.cache import country_cache
from app.cache.country_cache import CACHE_MISS
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

logger = logging.getLogger(__name__)


# Service methods for the Queries and Mutations
async def get_countries(page: int, page_size: int):
    logger.info(f"get_countries:Start - page: {page}, page_size: {page_size}")
    params = parse_input(PaginationInput, page=page, page_size=page_size)
    items, total_count = await country_repository.get_countries(
        params.page,
        params.page_size,
    )
    total_pages = (total_count + params.page_size - 1) // params.page_size
    logger.info(f"get_countries:End - total_count: {total_count}, total_pages: {total_pages}")
    return {
        "items": items,
        "total_count": total_count,
        "page": params.page,
        "page_size": params.page_size,
        "total_pages": total_pages,
    }


async def get_country_by_code(code: str):
    logger.info(f"get_country_by_code:Start - code: {code}")
    params = parse_input(CountryCodeInput, code=code)
    cached = await country_cache.get_by_code(params.code)
    if cached is not CACHE_MISS:
        logger.info("get_country_by_code:End - cache hit code=%s", params.code)
        return cached

    country = await country_repository.get_country_by_code(params.code)
    await country_cache.put(country, code=params.code)
    logger.info(f"get_country_by_code:End - country: {country is not None}")
    return country


async def get_country_by_id(id: str):
    logger.info(f"get_country_by_id:Start - id: {id}")
    params = parse_input(CountryIdInput, id=id)
    cached = await country_cache.get_by_id(params.id)
    if cached is not CACHE_MISS:
        logger.info("get_country_by_id:End - cache hit id=%s", params.id)
        return cached

    country = await country_repository.get_country_by_id(params.id)
    await country_cache.put(country, country_id=params.id)
    logger.info(f"get_country_by_id:End - country: {country is not None}")
    return country


async def get_countries_by_language(language: str):
    logger.info(f"get_countries_by_language:Start - language: {language}")
    params = parse_input(LanguageInput, language=language)
    countries = await country_repository.get_countries_by_language(params.language)
    logger.info(f"get_countries_by_language:End - countries: {len(countries)}")
    return countries


async def get_nearby_countries(
    latitude: float,
    longitude: float,
    max_distance: float,
):
    logger.info(f"get_nearby_countries:Start - latitude: {latitude}, longitude: {longitude}, max_distance: {max_distance}")
    params = parse_input(
        NearbyInput,
        latitude=latitude,
        longitude=longitude,
        max_distance=max_distance,
    )
    nearby_countries = await country_repository.get_nearby_countries(
        params.latitude,
        params.longitude,
        params.max_distance,
    )
    logger.info(f"get_nearby_countries:End - nearby_countries: {len(nearby_countries)}")
    return nearby_countries


async def get_countries_grouped_by_currency():
    return await country_repository.get_countries_grouped_by_currency()


async def add_country(data: AddCountryInput):
    logger.info(f"add_country:Start")
    existing = await country_repository.get_country_by_code(data.code)
    if existing:
        raise ValueError(f"Country {data.code} already exists")
    country = await country_repository.add_country(build_country_document(data))
    await country_cache.put(country)
    logger.info("add_country:End - id=%s code=%s", country.get("_id"), country.get("code"))
    return country


async def update_country(data: UpdateCountryInput):
    logger.info(f"update_country:Start - code: {data.code}")
    country = await country_repository.get_country_by_code(data.code)
    if not country:
        raise ValueError(f"Country {data.code} not found")
    patch = build_country_update_patch(data)
    country = await country_repository.update_country(data.code, patch)
    if country:
        await country_cache.put(country)
    logger.info(
        "update_country:End - id=%s code=%s",
        country.get("_id") if country else None,
        data.code,
    )
    return country
