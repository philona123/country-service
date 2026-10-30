import strawberry

from app.services import country_service
from app.graphql.types import CountryType
from app.graphql.mappers import country_to_type


@strawberry.type
class Mutation:

    @strawberry.mutation
    async def add_country(
        self,
        code: str,
        common_name: str,
        official_name: str
    ) -> CountryType:

        country = await country_service.add_country(
            code,
            common_name,
            official_name
        )

        return country_to_type(country)

    @strawberry.mutation
    async def update_country_name(
        self,
        code: str,
        common_name: str,
        official_name: str
    ) -> CountryType:

        country = await country_service.update_country_name(
            code,
            common_name,
            official_name
        )

        return country_to_type(country)