from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
import hashlib
import time
import xml.etree.ElementTree as ET

import requests
import yaml

from app.schemas import SourceRecord


class SearchAdapter(ABC):
    @abstractmethod
    def search(self, topic: str) -> list[SourceRecord]:
        """Return normalized source records for a topic."""


class PlaceholderSearchAdapter(SearchAdapter):
    def search(self, topic: str) -> list[SourceRecord]:
        return [
            SourceRecord(
                title=f"Placeholder source for {topic}",
                url="https://example.com/agentic-newsroom-placeholder-source",
                excerpt=(
                    "Placeholder source text for local dry-run execution. "
                    "Replace this adapter before relying on live research."
                ),
                provider="placeholder",
                metadata={"dry_run": True},
            )
        ]


class SearXNGSearchAdapter(SearchAdapter):
    def __init__(self, base_url: str = "http://searxng:8080", timeout_seconds: int = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def search(self, topic: str) -> list[SourceRecord]:
        try:
            response = requests.get(
                f"{self.base_url}/search",
                params={"q": topic, "format": "json"},
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise RuntimeError(f"SearXNG search failed safely: {exc}") from exc
        except ValueError as exc:
            raise RuntimeError("SearXNG search failed safely: response was not valid JSON") from exc

        results = payload.get("results")
        if not isinstance(results, list):
            raise RuntimeError("SearXNG search failed safely: JSON response did not include a results list")

        sources: list[SourceRecord] = []
        for index, result in enumerate(results):
            if not isinstance(result, dict):
                continue

            url = result.get("url")
            title = result.get("title") or f"SearXNG result {index + 1}"
            excerpt = result.get("content") or result.get("snippet") or title
            if not url:
                continue

            sources.append(
                SourceRecord(
                    title=title,
                    url=url,
                    excerpt=excerpt,
                    provider="searxng",
                    metadata={
                        "engine": result.get("engine"),
                        "score": result.get("score"),
                    },
                )
            )

        if not sources:
            raise RuntimeError("SearXNG search failed safely: no usable results with URLs were returned")

        return sources


@dataclass
class RssSourceConfig:
    id: str
    name: str
    type: str
    enabled: bool
    url: str
    fallback_urls: list[str] = field(default_factory=list)
    category: str | None = None
    tags: list[str] = field(default_factory=list)
    max_items: int | None = None
    max_age_days: int | None = None
    excerpt_chars: int | None = None
    cache_ttl_seconds: int | None = None
    default_query_terms: list[str] = field(default_factory=list)
    filter_terms: list[str] = field(default_factory=list)
    notes: str | None = None


@dataclass
class CachedFeed:
    content: str
    cached_at: float
    etag: str | None = None
    last_modified: str | None = None


class RssSearchAdapter(SearchAdapter):
    _response_cache: dict[str, CachedFeed] = {}

    def __init__(
        self,
        feed_urls: list[str] | None = None,
        registry_path: str | None = None,
        source_ids: list[str] | None = None,
        default_max_items: int = 25,
        default_excerpt_chars: int = 800,
        cache_ttl_seconds: int = 900,
        timeout_seconds: int = 10,
    ) -> None:
        self.feed_urls = [url.strip() for url in (feed_urls or []) if url.strip()]
        self.registry_path = registry_path
        self.source_ids = [source_id.strip() for source_id in (source_ids or []) if source_id.strip()]
        self.default_max_items = default_max_items
        self.default_excerpt_chars = default_excerpt_chars
        self.cache_ttl_seconds = cache_ttl_seconds
        self.timeout_seconds = timeout_seconds

    def search(self, topic: str) -> list[SourceRecord]:
        sources = self._configured_sources()
        if not sources:
            raise RuntimeError(
                "RSS search failed safely: configure RSS_SOURCE_IDS with a registry or provide RSS_FEED_URLS"
            )

        records: list[SourceRecord] = []
        errors: list[str] = []

        for source in sources:
            if not source.enabled:
                continue
            try:
                records.extend(self._fetch_and_parse_source(source, topic))
            except RuntimeError as exc:
                errors.append(str(exc))

        records = self._deduplicate(records)
        records.sort(key=lambda record: record.metadata.get("published_at") or "", reverse=True)

        if not records:
            detail = "; ".join(errors) if errors else "no usable feed items with links were returned"
            raise RuntimeError(f"RSS search failed safely: {detail}")

        return records

    def _configured_sources(self) -> list[RssSourceConfig]:
        if self.registry_path and self.source_ids:
            return select_rss_sources(load_rss_source_registry(self.registry_path), self.source_ids)

        return [
            RssSourceConfig(
                id=f"feed_{index + 1}",
                name=url,
                type="rss",
                enabled=True,
                url=url,
                max_items=self.default_max_items,
                excerpt_chars=self.default_excerpt_chars,
                cache_ttl_seconds=self.cache_ttl_seconds,
                notes="Configured through RSS_FEED_URLS quick local experiment mode.",
            )
            for index, url in enumerate(self.feed_urls)
        ]

    def _fetch_and_parse_source(self, source: RssSourceConfig, topic: str) -> list[SourceRecord]:
        errors: list[str] = []
        for url in [source.url, *source.fallback_urls]:
            try:
                content, cache_metadata = self._fetch_feed(
                    url,
                    cache_ttl_seconds=source.cache_ttl_seconds or self.cache_ttl_seconds,
                )
                records = self._parse_feed(content, url, topic, source, cache_metadata)
                return records[: source.max_items or self.default_max_items]
            except RuntimeError as exc:
                errors.append(str(exc))

        raise RuntimeError(f"{source.id} unavailable after primary and fallback attempts: {'; '.join(errors)}")

    def _fetch_feed(self, feed_url: str, cache_ttl_seconds: int) -> tuple[str, dict[str, str | bool | None]]:
        cached = self._response_cache.get(feed_url)
        now = time.time()
        if cached and now - cached.cached_at <= cache_ttl_seconds:
            return cached.content, {
                "cache_hit": True,
                "etag": cached.etag,
                "last_modified": cached.last_modified,
            }

        try:
            response = requests.get(feed_url, timeout=self.timeout_seconds)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"feed fetch failed for {feed_url}: {exc}") from exc

        cached_feed = CachedFeed(
            content=response.text,
            cached_at=now,
            etag=response.headers.get("ETag"),
            last_modified=response.headers.get("Last-Modified"),
        )
        self._response_cache[feed_url] = cached_feed
        return response.text, {
            "cache_hit": False,
            "etag": cached_feed.etag,
            "last_modified": cached_feed.last_modified,
        }

    def _parse_feed(
        self,
        feed_content: str,
        feed_url: str,
        topic: str,
        source: RssSourceConfig,
        cache_metadata: dict[str, str | bool | None] | None = None,
    ) -> list[SourceRecord]:
        try:
            root = ET.fromstring(feed_content)
        except ET.ParseError as exc:
            raise RuntimeError(f"feed XML could not be parsed for {feed_url}") from exc

        items = root.findall(".//item")
        atom_mode = False
        if not items:
            items = root.findall(".//{http://www.w3.org/2005/Atom}entry")
            atom_mode = True

        records: list[tuple[datetime | None, SourceRecord]] = []
        for item in items:
            title = self._text(item, "title") or "Untitled RSS item"
            link = self._text(item, "link") or self._atom_link(item)
            guid = self._text(item, "guid") or link or title
            description = (
                self._text(item, "description")
                or self._text(item, "summary")
                or self._text(item, "content")
                or self._text(item, "{http://www.w3.org/2005/Atom}summary")
                or title
            )
            published_at = self._published_at(item, atom_mode)

            if not link or not self._matches_terms(topic, title, description, source):
                continue
            if source.max_age_days and published_at:
                if published_at < datetime.now(timezone.utc) - timedelta(days=source.max_age_days):
                    continue

            excerpt = self._truncate(description, source.excerpt_chars or self.default_excerpt_chars)
            record = SourceRecord(
                title=title,
                url=link,
                excerpt=excerpt,
                provider="rss",
                metadata={
                    "source_id": source.id,
                    "source_name": source.name,
                    "source_type": source.type,
                    "source_category": source.category,
                    "source_tags": source.tags,
                    "feed_url": feed_url,
                    "primary_url": source.url,
                    "fallback_urls": source.fallback_urls,
                    "guid": guid,
                    "published_at": published_at.isoformat() if published_at else None,
                    "cache": cache_metadata or {},
                    "conditional_request": {
                        "etag": (cache_metadata or {}).get("etag"),
                        "last_modified": (cache_metadata or {}).get("last_modified"),
                    },
                },
            )
            records.append((published_at, record))

        records.sort(key=lambda pair: pair[0] or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        return [record for _, record in records]

    def _matches_terms(self, topic: str, title: str, description: str, source: RssSourceConfig) -> bool:
        terms = source.filter_terms or source.default_query_terms
        searchable = f"{title} {description}".lower()
        if topic and topic.lower() in searchable:
            return True
        if terms:
            return any(term.lower() in searchable for term in terms)
        return True

    def _deduplicate(self, records: list[SourceRecord]) -> list[SourceRecord]:
        seen: set[str] = set()
        deduped: list[SourceRecord] = []
        for record in records:
            guid = record.metadata.get("guid")
            key_material = str(guid or record.url or record.title)
            key = hashlib.sha256(key_material.encode("utf-8")).hexdigest()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(record)
        return deduped

    def _truncate(self, value: str, max_chars: int) -> str:
        cleaned = " ".join(value.split())
        if len(cleaned) <= max_chars:
            return cleaned
        return cleaned[: max(0, max_chars - 3)].rstrip() + "..."

    def _text(self, item: ET.Element, tag: str) -> str | None:
        child = item.find(tag)
        if child is None:
            child = item.find(f"{{http://www.w3.org/2005/Atom}}{tag}")
        if child is None or child.text is None:
            return None
        return child.text.strip()

    def _atom_link(self, item: ET.Element) -> str | None:
        link = item.find("{http://www.w3.org/2005/Atom}link")
        if link is None:
            return None
        href = link.attrib.get("href")
        return href.strip() if href else None

    def _published_at(self, item: ET.Element, atom_mode: bool) -> datetime | None:
        raw = (
            self._text(item, "pubDate")
            or self._text(item, "published")
            or self._text(item, "updated")
            or self._text(item, "{http://www.w3.org/2005/Atom}updated")
        )
        if not raw:
            return None
        try:
            parsed = parsedate_to_datetime(raw)
        except (TypeError, ValueError):
            try:
                parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            except ValueError:
                return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)


def load_rss_source_registry(registry_path: str) -> list[RssSourceConfig]:
    path = _resolve_registry_path(registry_path)
    if not path.exists():
        raise RuntimeError(f"RSS source registry not found: {registry_path}")

    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}

    raw_sources = payload.get("sources")
    if not isinstance(raw_sources, list):
        raise RuntimeError(f"RSS source registry is invalid: {registry_path} must contain a sources list")

    sources: list[RssSourceConfig] = []
    for raw in raw_sources:
        if not isinstance(raw, dict):
            continue
        sources.append(
            RssSourceConfig(
                id=str(raw.get("id", "")).strip(),
                name=str(raw.get("name", "")).strip(),
                type=str(raw.get("type", "rss")).strip(),
                enabled=bool(raw.get("enabled", True)),
                url=str(raw.get("url", "")).strip(),
                fallback_urls=list(raw.get("fallback_urls") or []),
                category=raw.get("category"),
                tags=list(raw.get("tags") or []),
                max_items=raw.get("max_items"),
                max_age_days=raw.get("max_age_days"),
                excerpt_chars=raw.get("excerpt_chars"),
                cache_ttl_seconds=raw.get("cache_ttl_seconds"),
                default_query_terms=list(raw.get("default_query_terms") or []),
                filter_terms=list(raw.get("filter_terms") or []),
                notes=raw.get("notes"),
            )
        )

    return sources


def select_rss_sources(sources: list[RssSourceConfig], source_ids: list[str]) -> list[RssSourceConfig]:
    by_id = {source.id: source for source in sources if source.id}
    selected: list[RssSourceConfig] = []
    missing: list[str] = []
    for source_id in source_ids:
        source = by_id.get(source_id)
        if source is None:
            missing.append(source_id)
        elif source.type != "rss":
            raise RuntimeError(f"RSS source '{source_id}' has unsupported type '{source.type}'")
        else:
            selected.append(source)
    if missing:
        raise RuntimeError(f"RSS source ids not found in registry: {', '.join(missing)}")
    return selected


def _resolve_registry_path(registry_path: str) -> Path:
    path = Path(registry_path)
    if path.is_absolute() or path.exists():
        return path

    repo_relative = Path(__file__).resolve().parents[2] / registry_path
    if repo_relative.exists():
        return repo_relative

    workspace_relative = Path(__file__).resolve().parents[3] / registry_path
    return workspace_relative


def get_search_adapter(
    provider: str = "placeholder",
    searxng_base_url: str = "http://searxng:8080",
    rss_feed_urls: str | list[str] = "",
    rss_source_registry_path: str | None = "config/sources/rss_sources.yml",
    rss_source_ids: str | list[str] = "",
    rss_default_max_items: int = 25,
    rss_default_excerpt_chars: int = 800,
    rss_cache_ttl_seconds: int = 900,
) -> SearchAdapter:
    normalized_provider = provider.strip().lower()
    if normalized_provider == "placeholder":
        return PlaceholderSearchAdapter()
    if normalized_provider == "searxng":
        return SearXNGSearchAdapter(base_url=searxng_base_url)
    if normalized_provider == "rss":
        feed_urls = rss_feed_urls.split(",") if isinstance(rss_feed_urls, str) else rss_feed_urls
        source_ids = rss_source_ids.split(",") if isinstance(rss_source_ids, str) else rss_source_ids
        return RssSearchAdapter(
            feed_urls=feed_urls,
            registry_path=rss_source_registry_path,
            source_ids=source_ids,
            default_max_items=rss_default_max_items,
            default_excerpt_chars=rss_default_excerpt_chars,
            cache_ttl_seconds=rss_cache_ttl_seconds,
        )
    raise ValueError(
        f"Unsupported search provider '{provider}'. Supported providers: placeholder, searxng, rss."
    )
