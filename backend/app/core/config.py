from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str
    anthropic_api_key: str
    youtube_api_key: str
    refresh_key: str

    refresh_interval_hours: int = 48
    max_items_per_domain: int = 10

    # Comma-separated allowed CORS origins (e.g. "https://frontier-brief.vercel.app")
    cors_origins: str = "https://frontier-brief.vercel.app"

    environment: str = "production"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()  # type: ignore[call-arg]
