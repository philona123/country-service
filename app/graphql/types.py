import strawberry
from typing import Optional

@strawberry.type
class CountryNameType:
    common: str
    official: str
    native: Optional[str]

@strawberry.type
class CurrencyType:
    code: str
    name: str
    symbol: Optional[str]

@strawberry.type
class LanguageType:
    code: Optional[str]
    name: str
    nativeName: Optional[str]

@strawberry.type
class CoordinatesType:
    latitude: float
    longitude: float

@strawberry.type
class CountryType:
    id: str
    code: str
    name: CountryNameType
    alpha3Code: Optional[str]
    capital: list[str]
    region: Optional[str]
    subregion: Optional[str]
    population: int
    area: Optional[float]
    coordinates: Optional[CoordinatesType]
    currencies: list[CurrencyType]
    languages: list[LanguageType]

@strawberry.type
class CountryConnection:
    items: list[CountryType]
    total_count: int
    page: int
    page_size: int
    total_pages: int


@strawberry.type
class NearbyCountryType:
    country: CountryType
    distance_km: float


@strawberry.type
class CurrencyGroupType:
    currency_code: str
    currency_name: Optional[str]
    symbol: Optional[str]
    country_count: int
    countries: list[CountryType]

