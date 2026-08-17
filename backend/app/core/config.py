import logging

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str
    anthropic_api_key: str
    youtube_api_key: str
    tavily_api_key: str = ""  # optional — WebArticlesFetcher skips gracefully when absent
    refresh_key: str

    refresh_interval_hours: int = 48
    max_items_per_domain: int = 10

    # Comma-separated allowed CORS origins (e.g. "https://frontier-brief.vercel.app")
    cors_origins: str = ""

    environment: str = "production"

    @field_validator("refresh_key")
    @classmethod
    def refresh_key_must_be_strong(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("REFRESH_KEY must be at least 32 characters")
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()  # type: ignore[call-arg]

if settings.environment == "production" and not settings.cors_origins_list:
    logger.warning(
        "CORS_ORIGINS is not configured — all cross-origin requests will be blocked. "
        "Set CORS_ORIGINS to your Vercel frontend URL in Railway environment variables."
    )
