from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "StockPilot API"
    # Injected at image build time with the Git commit SHA (see backend/Dockerfile).
    app_version: str = "dev"
    database_url: str = "postgresql+psycopg://stockpilot:stockpilot@localhost:5432/stockpilot"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
