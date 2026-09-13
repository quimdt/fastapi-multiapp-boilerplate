from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "FastAPI Boilerplate"
    api_version: str = "v1"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 43200
    database_url: str = (
        "postgresql+psycopg2://postgres:postgres@localhost:5432/boilerplate"
    )
    frontend_host: str = "http://localhost:3000"

    admin_email: str = "admin@boilerplate.com"
    admin_password: str = "admin"
    admin_name: str = "Admin"
    admin_surname: str = "User"


settings = Settings()
