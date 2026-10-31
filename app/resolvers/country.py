import strawberry

from app.graphql.inputs import AddCountryInput as AddCountryInputGQL
from app.graphql.inputs import UpdateCountryInput as UpdateCountryInputGQL
from app.graphql.mappers import country_to_type
from app.graphql.types import (
    CountryConnection,
    CountryType,
    CurrencyGroupType,
    NearbyCountryType,
)
from app.services import country_service
from app.utils.country import (
    parse_add_country_input,
    parse_update_country_input,
)

# Resolver for Queries and Mutation

# Queries
@strawberry.type
class Query:
    @strawberry.field
    async def get_countries(
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
    async def get_country_by_code(self, code: str) -> CountryType | None:
        result = await country_service.get_country_by_code(code)
        if not result:
            return None
        return country_to_type(result)

    @strawberry.field
    async def get_countries_by_language(self, language: str) -> list[CountryType]:
        countries = await country_service.get_countries_by_language(language)
        return [country_to_type(country) for country in countries]

    @strawberry.field
    async def get_nearby_countries(
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
    async def get_countries_grouped_by_currency(self) -> list[CurrencyGroupType]:
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
    async def get_country_by_id(self, id: str) -> CountryType | None:
        country = await country_service.get_country_by_id(id)
        if not country:
            return None
        return country_to_type(country)


# Mutations
@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_country(self, input: AddCountryInputGQL) -> CountryType:
        data = parse_add_country_input(input)
        country = await country_service.add_country(data)
        return country_to_type(country)

    @strawberry.mutation
    async def update_country(self, input: UpdateCountryInputGQL) -> CountryType:
        data = parse_update_country_input(input)
        country = await country_service.update_country(data)
        return country_to_type(country)
