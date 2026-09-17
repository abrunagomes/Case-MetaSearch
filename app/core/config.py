##usa pydantic-settings para carregar configs a partir de variáveis de ambiente
##garante instancia unica pelo get_settings

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ##carrega as configs de ambiente

    # Aplicação
    app_name: str = "Data Catalog Service"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True

    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "data_catalog"
    mongodb_collection: str = "metadata"

    # Paginação
    default_page_size: int = 20
    max_page_size: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
