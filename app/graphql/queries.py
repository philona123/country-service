import strawberry

from app.services import country_service
from app.graphql.types import (
    CountryType,
    CountryConnection,
    NearbyCountryType,
    CurrencyGroupType
)
from app.graphql.mappers import country_to_type


@strawberry.type
class Query:

    # 1. Get all countries with pagination
    @strawberry.field
    async def countries(
        self,
        page: int = 1,
        page_size: int = 10
    ) -> CountryConnection:

        result = await country_service.get_countries(
            page,
            page_size
        )

        return CountryConnection(
            items=[
                country_to_type(country)
                for country in result["items"]
            ],
            total_count=result["total_count"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"]
        )

    # 2. Get a country by its code
    @strawberry.field
    async def country(self, code: str) -> CountryType | None:

        result = await country_service.get_country_by_code(code)

        if not result:
            return None

        return country_to_type(result)

    # 3. Find countries by language
    @strawberry.field
    async def countries_by_language(
        self,
        language: str
    ) -> list[CountryType]:

        countries = await country_service.get_countries_by_language(
            language
        )

        return [
            country_to_type(country)
            for country in countries
        ]

    # 4. Find nearby countries
    @strawberry.field
    async def countries_nearby(
        self,
        latitude: float,
        longitude: float,
        max_distance: float = 500
    ) -> list[NearbyCountryType]:

        countries = await country_service.get_nearby_countries(
            latitude,
            longitude,
            max_distance
        )

        return [
            NearbyCountryType(
                country=country_to_type(country),
                distance_km=country["distanceMeters"] / 1000
            )
            for country in countries
        ]

    # 5. Group countries by currency
    @strawberry.field
    async def countries_by_currency(
        self
    ) -> list[CurrencyGroupType]:

        groups = await country_service.get_countries_grouped_by_currency()

        return [
            CurrencyGroupType(
                currency_code=group["_id"],
                currency_name=group.get("name"),
                symbol=group.get("symbol"),
                country_count=group["countryCount"],
                countries=[
                    country_to_type(country)
                    for country in group["countries"]
                ]
            )
            for group in groups
            if group.get("_id")
        ]