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
    return [
        {
            "code": language.code,
            "name": language.name,
            "nativeName": language.native_name,
        }
        for language in languages
    ]


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
    payload: dict = {
        "code": input.code,
        "common_name": input.common_name,
        "official_name": input.official_name,
        "native_name": input.native_name,
        "alpha3_code": input.alpha3_code,
        "region": input.region,
        "subregion": input.subregion,
        "population": input.population,
        "area": input.area,
        "capital": input.capital,
        "latitude": input.latitude,
        "longitude": input.longitude,
    }

    if input.currencies is not None:
        payload["currencies"] = _currencies_to_dicts(input.currencies)

    if input.languages is not None:
        payload["languages"] = _languages_to_dicts(input.languages)

    return parse_input(UpdateCountryInput, **payload)


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
    if data.alpha3_code is not None:
        patch["alpha3Code"] = data.alpha3_code
    if data.region is not None:
        patch["region"] = data.region
    if data.subregion is not None:
        patch["subregion"] = data.subregion
    if data.population is not None:
        patch["population"] = data.population
    if data.area is not None:
        patch["area"] = data.area
    if data.capital is not None:
        patch["capital"] = data.capital
    if data.currencies is not None:
        patch["currencies"] = [c.model_dump() for c in data.currencies]
    if data.languages is not None:
        patch["languages"] = [language.model_dump() for language in data.languages]

    if data.latitude is not None and data.longitude is not None:
        coordinates, location = _geo_from_lat_lon(data.latitude, data.longitude)
        patch["coordinates"] = coordinates
        patch["location"] = location

    if touches_name:
        patch["nameSource"] = "MANUAL"

    return patch
