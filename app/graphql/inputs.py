import strawberry


@strawberry.input
class CurrencyInput:
    code: str
    name: str
    symbol: str | None = None


@strawberry.input
class LanguageInput:
    name: str
    native_name: str | None = None


@strawberry.input
class AddCountryInput:
    code: str
    common_name: str
    official_name: str
    native_name: str | None = None
    alpha3_code: str | None = None
    region: str | None = None
    subregion: str | None = None
    population: int | None = None
    area: float | None = None
    capital: list[str] | None = None
    latitude: float | None = None
    longitude: float | None = None
    currencies: list[CurrencyInput] | None = None
    languages: list[LanguageInput] | None = None


@strawberry.input
class UpdateCountryInput:
    common_name: str | None = None
    official_name: str | None = None
    native_name: str | None = None
