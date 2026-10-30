import strawberry

from app.graphql.mappers import country_to_type
from app.graphql.types import (
    CountryConnection,
    CountryType,
    CurrencyGroupType,
    NearbyCountryType,
)
from app.services import country_service


@strawberry.type
class Query:
    @strawberry.field
    async def countries(
        self,
        page: int = 1,
        page_size: int = 10,
    ) -> CountryConnection:
        result = await country_service.get_countries(page, page_size)
        return CountryConnection(
            items=[country_to_type(country) for country in result["items"]],
            total_count=result["total_count"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"],
        )

    @strawberry.field
    async def country(self, code: str) -> CountryType | None:
        result = await country_service.get_country_by_code(code)
        if not result:
            return None
        return country_to_type(result)

    @strawberry.field
    async def countries_by_language(self, language: str) -> list[CountryType]:
        countries = await country_service.get_countries_by_language(language)
        return [country_to_type(country) for country in countries]

    @strawberry.field
    async def countries_nearby(
        self,
        latitude: float,
        longitude: float,
        max_distance: float = 500,
    ) -> list[NearbyCountryType]:
        countries = await country_service.get_nearby_countries(
            latitude,
            longitude,
            max_distance,
        )
        return [
            NearbyCountryType(
                country=country_to_type(country),
                distance_km=country["distanceMeters"] / 1000,
            )
            for country in countries
        ]

    @strawberry.field
    async def countries_by_currency(self) -> list[CurrencyGroupType]:
        groups = await country_service.get_countries_grouped_by_currency()
        return [
            CurrencyGroupType(
                currency_code=group["_id"],
                currency_name=group.get("name"),
                symbol=group.get("symbol"),
                country_count=group["countryCount"],
                countries=[
                    country_to_type(country) for country in group["countries"]
                ],
            )
            for group in groups
            if group.get("_id")
        ]

    @strawberry.field
    async def country_by_id(self, id: str) -> CountryType | None:
        country = await country_service.get_country_by_id(id)
        if not country:
            return None
        return country_to_type(country)


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def add_country(
        self,
        code: str,
        common_name: str,
        official_name: str,
    ) -> CountryType:
        country = await country_service.add_country(
            code,
            common_name,
            official_name,
        )
        return country_to_type(country)

    @strawberry.mutation
    async def update_country_name(
        self,
        code: str,
        common_name: str,
        official_name: str,
    ) -> CountryType:
        country = await country_service.update_country_name(
            code,
            common_name,
            official_name,
        )
        return country_to_type(country)
