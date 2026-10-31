from datetime import datetime, timezone

from app.graphql.inputs import AddCountryInput as AddCountryInputGQL
from app.graphql.inputs import CurrencyInput
from app.graphql.inputs import LanguageInput
from app.graphql.inputs import UpdateCountryInput as UpdateCountryInputGQL
from app.schemas.inputs import AddCountryInput, UpdateCountryInput
from app.schemas.validation import parse_input


def _geo_from_lat_lon(
    latitude: float | None,
    longitude: float | None,
) -> tuple[dict | None, dict | None]:
    if latitude is None or longitude is None:
        return None, None

    coordinates = {"latitude": latitude, "longitude": longitude}
    location = {
        "type": "Point",
        "coordinates": [longitude, latitude],
    }
    return coordinates, location


def _currencies_to_dicts(
    currencies: list[CurrencyInput] | None,
) -> list[dict]:
    if not currencies:
        return []
    return [
        {"code": c.code, "name": c.name, "symbol": c.symbol}
        for c in currencies
    ]


def _languages_to_dicts(
    languages: list[LanguageInput] | None,
) -> list[dict]:
    if not languages:
        return []
    result = []
    for language in languages:
        entry: dict = {"name": language.name}
        if language.native_name:
            entry["nativeName"] = language.native_name
        result.append(entry)
    return result


def parse_add_country_input(input: AddCountryInputGQL) -> AddCountryInput:
    return parse_input(
        AddCountryInput,
        code=input.code,
        common_name=input.common_name,
        official_name=input.official_name,
        native_name=input.native_name,
        alpha3_code=input.alpha3_code,
        region=input.region,
        subregion=input.subregion,
        population=input.population,
        area=input.area,
        capital=input.capital or [],
        latitude=input.latitude,
        longitude=input.longitude,
        currencies=_currencies_to_dicts(input.currencies),
        languages=_languages_to_dicts(input.languages),
    )


def parse_update_country_input(
    input: UpdateCountryInputGQL,
) -> UpdateCountryInput:
    return parse_input(
        UpdateCountryInput,
        common_name=input.common_name,
        official_name=input.official_name,
        native_name=input.native_name,
    )


def build_country_document(data: AddCountryInput) -> dict:
    coordinates, location = _geo_from_lat_lon(data.latitude, data.longitude)
    now = datetime.now(timezone.utc)

    return {
        "code": data.code,
        "name": {
            "common": data.common_name,
            "official": data.official_name,
            "native": data.native_name,
        },
        "alpha3Code": data.alpha3_code,
        "capital": data.capital,
        "region": data.region,
        "subregion": data.subregion,
        "population": data.population if data.population is not None else 0,
        "area": data.area,
        "coordinates": coordinates,
        "location": location,
        "currencies": [currency.model_dump() for currency in data.currencies],
        "languages": [language.model_dump() for language in data.languages],
        "isActive": True,
        "sourceType": "MANUAL",
        "createdAt": now,
        "updatedAt": now,
    }


def build_country_update_patch(data: UpdateCountryInput) -> dict:
    patch: dict = {"updatedAt": datetime.now(timezone.utc)}
    touches_name = False

    if data.common_name is not None:
        patch["name.common"] = data.common_name
        touches_name = True
    if data.official_name is not None:
        patch["name.official"] = data.official_name
        touches_name = True
    if data.native_name is not None:
        patch["name.native"] = data.native_name
        touches_name = True
    if touches_name:
        patch["nameSource"] = "MANUAL"

    return patch
