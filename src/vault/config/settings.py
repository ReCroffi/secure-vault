from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    test_database_url: str | None = None
    kdf_algorithm: str
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
