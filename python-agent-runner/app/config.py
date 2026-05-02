from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the local agent runner."""

    environment: str = "dev"
    dry_run: bool = True
    aws_region: str = "us-east-1"
    search_provider: str = "placeholder"
    searxng_base_url: str = "http://searxng:8080"
    rss_feed_urls: str = ""
    storage_provider: str = "memory"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def external_calls_enabled(self) -> bool:
        return not self.dry_run


@lru_cache
def get_settings() -> Settings:
    return Settings()
