from datetime import datetime

from app.graphql.inputs import AddCountryInput as AddCountryInputGQL
from app.graphql.inputs import CurrencyInput, LanguageInput
from app.schemas.inputs import AddCountryInput, UpdateCountryInput
from app.schemas.validation import parse_input
from app.utils.country import (
    build_country_document,
    build_country_update_patch,
    parse_add_country_input,
)


def test_build_country_document_minimal_defaults():
    data = parse_input(
        AddCountryInput,
        code="XX",
        common_name="Example",
        official_name="Republic of Example",
    )
    document = build_country_document(data)

    assert document["code"] == "XX"
    assert document["population"] == 0
    assert document["coordinates"] is None
    assert document["location"] is None
    assert document["isActive"] is True
    assert document["sourceType"] == "MANUAL"
    assert isinstance(document["createdAt"], datetime)
    assert document["createdAt"].tzinfo is not None


def test_build_country_document_with_geo():
    data = parse_input(
        AddCountryInput,
        code="XX",
        common_name="Example",
        official_name="Republic of Example",
        latitude=12.0,
        longitude=77.0,
    )
    document = build_country_document(data)

    assert document["coordinates"] == {"latitude": 12.0, "longitude": 77.0}
    assert document["location"] == {
        "type": "Point",
        "coordinates": [77.0, 12.0],
    }


def test_build_country_update_patch_sets_name_source_when_name_changes():
    data = parse_input(UpdateCountryInput, code="IN", common_name="New Name")
    patch = build_country_update_patch(data)

    assert patch["name.common"] == "New Name"
    assert patch["nameSource"] == "MANUAL"
    assert "updatedAt" in patch
    assert isinstance(patch["updatedAt"], datetime)


def test_build_country_update_patch_skips_name_source_for_non_name_fields():
    data = parse_input(UpdateCountryInput, code="IN", population=99)
    patch = build_country_update_patch(data)

    assert patch["population"] == 99
    assert "nameSource" not in patch


def test_parse_add_country_input_from_graphql():
    gql_input = AddCountryInputGQL(
        code="xy",
        common_name="Test",
        official_name="Test Republic",
        currencies=[CurrencyInput(code="TST", name="Test", symbol="T")],
        languages=[LanguageInput(name="Testian", native_name="Testish")],
    )
    result = parse_add_country_input(gql_input)

    assert result.code == "XY"
    assert len(result.currencies) == 1
    assert result.currencies[0].code == "TST"
    assert len(result.languages) == 1
    assert result.languages[0].nativeName == "Testish"
