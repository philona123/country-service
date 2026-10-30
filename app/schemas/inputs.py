from pydantic import BaseModel, Field, field_validator


class PaginationInput(BaseModel):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)


class CountryCodeInput(BaseModel):
    code: str = Field(min_length=2, max_length=2)

    @field_validator("code", mode="before")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        if value is None:
            raise ValueError("Country code is required")
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


class UpdateCountryNameInput(BaseModel):
    code: str = Field(min_length=2, max_length=2)
    common_name: str = Field(min_length=1)
    official_name: str = Field(min_length=1)

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
