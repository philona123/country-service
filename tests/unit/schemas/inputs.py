import pytest

from app.schemas.inputs import (
    AddCountryInput,
    CountryCodeInput,
    CountryIdInput,
    PaginationInput,
    UpdateCountryInput,
)
from app.schemas.validation import parse_input


def test_pagination_input_valid():
    result = parse_input(PaginationInput, page=1, page_size=10)
    assert result.page == 1
    assert result.page_size == 10


@pytest.mark.parametrize("page,page_size", [(0, 10), (1, 0), (1, 101)])
def test_pagination_input_invalid(page, page_size):
    with pytest.raises(ValueError):
        parse_input(PaginationInput, page=page, page_size=page_size)


def test_country_code_normalizes_to_uppercase():
    result = parse_input(CountryCodeInput, code="in")
    assert result.code == "IN"


def test_country_code_requires_value():
    with pytest.raises(ValueError):
        parse_input(CountryCodeInput, code=None)


def test_country_id_valid_object_id(country_id):
    result = parse_input(CountryIdInput, id=country_id)
    assert result.id == country_id


def test_country_id_invalid():
    with pytest.raises(ValueError, match="Invalid country id"):
        parse_input(CountryIdInput, id="not-an-object-id")


def test_add_country_input_requires_coordinate_pair():
    with pytest.raises(ValueError, match="latitude and longitude"):
        parse_input(
            AddCountryInput,
            code="XX",
            common_name="A",
            official_name="B",
            latitude=1.0,
        )


def test_add_country_input_normalizes_code_and_strips_names():
    result = parse_input(
        AddCountryInput,
        code="xx",
        common_name="  Example  ",
        official_name="Official",
    )
    assert result.code == "XX"
    assert result.common_name == "Example"


def test_add_country_input_rejects_empty_name():
    with pytest.raises(ValueError):
        parse_input(
            AddCountryInput,
            code="XX",
            common_name="   ",
            official_name="Official",
        )


def test_update_country_requires_at_least_one_patch_field():
    with pytest.raises(ValueError, match="At least one name field"):
        parse_input(UpdateCountryInput)


def test_update_country_partial_patch():
    result = parse_input(
        UpdateCountryInput,
        common_name="Updated",
        official_name="Updated Official",
    )
    assert result.common_name == "Updated"
    assert result.official_name == "Updated Official"


def test_update_country_rejects_empty_optional_name():
    with pytest.raises(ValueError, match="cannot be empty"):
        parse_input(
            UpdateCountryInput,
            common_name="   ",
        )
