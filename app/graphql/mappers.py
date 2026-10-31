from app.models.country import (
    normalize_capital_list,
    normalize_currency_list,
    normalize_language_list,
)
from app.graphql.types import (
    CountryType,
    CountryNameType,
    CurrencyType,
    LanguageType,
    CoordinatesType,
)


def country_to_type(document: dict) -> CountryType:
    name = document.get("name") or {}

    coordinates_data = document.get("coordinates")

    coordinates = None

    if coordinates_data:
        coordinates = CoordinatesType(
            latitude=coordinates_data["latitude"],
            longitude=coordinates_data["longitude"]
        )

    currencies = [
        CurrencyType(
            code=item["code"],
            name=item["name"],
            symbol=item.get("symbol")
        )
        for item in normalize_currency_list(document.get("currencies"))
    ]

    languages = [
        LanguageType(
            name=item["name"],
            nativeName=item.get("nativeName"),
        )
        for item in normalize_language_list(document.get("languages"))
    ]

    return CountryType(
        id=str(document["_id"]),
        code=document["code"],
        name=CountryNameType(
            common=name.get("common", ""),
            official=name.get("official", ""),
            native=name.get("native")
        ),
        alpha3Code=document.get("alpha3Code"),
        capital=normalize_capital_list(document.get("capital")),
        region=document.get("region"),
        subregion=document.get("subregion"),
        population=document.get("population") or 0,
        area=document.get("area"),
        coordinates=coordinates,
        currencies=currencies,
        languages=languages
    )