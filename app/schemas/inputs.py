from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.country import Currency, Language, normalize_capital_list


class PaginationInput(BaseModel):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)


class CountryCodeInput(BaseModel):
    code: str = Field(min_length=2, max_length=2)

    @field_validator("code", mode="before")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return str(value).upper().strip()


class CountryIdInput(BaseModel):
    id: str = Field(min_length=1)

    @field_validator("id")
    @classmethod
    def valid_object_id(cls, value: str) -> str:
        from bson import ObjectId

        if not ObjectId.is_valid(value):
            raise ValueError("Invalid country id")
        return value


class LanguageInput(BaseModel):
    language: str = Field(min_length=1)

    @field_validator("language", mode="before")
    @classmethod
    def strip_language(cls, value: str) -> str:
        stripped = str(value).strip()
        if not stripped:
            raise ValueError("Language cannot be empty")
        return stripped


class NearbyInput(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    max_distance: float = Field(gt=0)


class AddCountryInput(BaseModel):
    code: str = Field(min_length=2, max_length=2)
    common_name: str = Field(min_length=1)
    official_name: str = Field(min_length=1)

    native_name: str | None = None
    alpha3_code: str | None = None
    region: str | None = None
    subregion: str | None = None
    population: int | None = Field(default=None, ge=0)
    area: float | None = Field(default=None, ge=0)
    capital: list[str] = Field(default_factory=list)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    currencies: list[Currency] = Field(default_factory=list)
    languages: list[Language] = Field(default_factory=list)

    @field_validator("code", mode="before")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return str(value).upper().strip()

    @field_validator("common_name", "official_name", mode="before")
    @classmethod
    def strip_name(cls, value: str) -> str:
        stripped = str(value).strip()
        if not stripped:
            raise ValueError("Country names cannot be empty")
        return stripped

    @field_validator("native_name", mode="before")
    @classmethod
    def strip_optional_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = str(value).strip()
        return stripped or None

    @field_validator("capital", mode="before")
    @classmethod
    def normalize_capital(cls, value: Any) -> list[str]:
        return normalize_capital_list(value)

    @model_validator(mode="after")
    def coordinates_pair(self) -> "AddCountryInput":
        if (self.latitude is None) ^ (self.longitude is None):
            raise ValueError("Both latitude and longitude must be provided together")
        return self


class UpdateCountryInput(BaseModel):
    common_name: str | None = None
    official_name: str | None = None
    native_name: str | None = None

    @field_validator(
        "common_name",
        "official_name",
        "native_name",
        mode="before",
    )
    @classmethod
    def strip_optional_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = str(value).strip()
        if not stripped:
            raise ValueError("Field cannot be empty when provided")
        return stripped

    @model_validator(mode="after")
    def validate_patch(self) -> "UpdateCountryInput":
        patch_fields = (
            self.common_name,
            self.official_name,
            self.native_name,
        )
        if all(value is None for value in patch_fields):
            raise ValueError("At least one name field must be provided to update")

        return self
