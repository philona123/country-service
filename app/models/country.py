from typing import Optional
from pydantic import BaseModel, Field


def normalize_capital_list(value) -> list[str]:
    if not value:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    return []


def normalize_currency_list(value) -> list[dict]:
    """Mongo $unwind leaves a single currency object instead of a list."""
    if not value:
        return []
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


class CountryName(BaseModel):
    common: str
    official: str
    native: Optional[str] = None

class Currency(BaseModel):
    code: str
    name: str
    symbol: Optional[str] = None

class Language(BaseModel):
    code: Optional[str] = None
    name: str
    nativeName: Optional[str] = None

class Coordinates(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

class GeoLocation(BaseModel):
    type: str = "Point"
    coordinates: list[float]

class Country(BaseModel):
    code: str = Field(min_length=2, max_length=2)

    name: CountryName

    alpha3Code: Optional[str] = None
    numericCode: Optional[str] = None

    capital: list[str] = Field(default_factory=list)

    region: Optional[str] = None
    subregion: Optional[str] = None

    population: int = Field(ge=0)
    area: Optional[float] = Field(default=None, ge=0)

    coordinates: Optional[Coordinates] = None

    currencies: list[Currency] = Field(default_factory=list)
    languages: list[Language] = Field(default_factory=list)

    timezones: list[str] = Field(default_factory=list)
    borders: list[str] = Field(default_factory=list)
    callingCodes: list[str] = Field(default_factory=list)
    topLevelDomains: list[str] = Field(default_factory=list)