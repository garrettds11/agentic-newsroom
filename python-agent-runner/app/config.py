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
    rss_source_registry_path: str = "config/sources/rss_sources.yml"
    rss_source_ids: str = "zdi_published_2026"
    rss_default_max_items: int = 25
    rss_default_excerpt_chars: int = 800
    rss_cache_ttl_seconds: int = 900
    newsroom_default_max_sources: int = 25
    newsroom_system_max_sources: int = 250
    storage_provider: str = "memory"
    newsroom_api_key: str = ""
    require_auth: bool = False

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
