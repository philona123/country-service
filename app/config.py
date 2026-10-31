from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
    LOG_LEVEL: str = "INFO"
    APP_NAME: str = "Country Service"
    ENVIRONMENT: str = "development"
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "country_db"
    MONGODB_TEST_DATABASE: str = "country_db_test"
    COUNTRY_API_URL: str = "https://www.apicountries.com"
    INGESTION_INTERVAL_HOURS: int = 24
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 300
    CACHE_NEGATIVE_TTL_SECONDS: int = 60


settings = Settings()
