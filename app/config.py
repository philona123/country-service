from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    APP_NAME: str = "Country Service"
    ENVIRONMENT: str = "development"
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "country_db"
    COUNTRY_API_URL: str = "https://countries.dev"
    INGESTION_INTERVAL_HOURS: int = 24


settings = Settings()
