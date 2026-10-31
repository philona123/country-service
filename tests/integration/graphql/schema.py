import pytest

from app.graphql.schema import schema

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_get_country_by_code_query(mongo_countries, sample_country):
    await mongo_countries.insert_one(sample_country)

    result = await schema.execute(
        """
        query ($code: String!) {
            getCountryByCode(code: $code) {
                code
                name { common }
            }
        }
        """,
        variable_values={"code": "IN"},
    )

    assert result.errors is None
    data = result.data["getCountryByCode"]
    assert data["code"] == "IN"
    assert data["name"]["common"] == "India"
