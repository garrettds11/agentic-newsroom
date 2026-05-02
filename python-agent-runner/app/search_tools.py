from abc import ABC, abstractmethod
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

import requests

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


class RssSearchAdapter(SearchAdapter):
    def __init__(self, feed_urls: list[str], timeout_seconds: int = 10) -> None:
        self.feed_urls = [url.strip() for url in feed_urls if url.strip()]
        self.timeout_seconds = timeout_seconds

    def search(self, topic: str) -> list[SourceRecord]:
        if not self.feed_urls:
            raise RuntimeError("RSS search failed safely: RSS_FEED_URLS is empty")

        sources: list[SourceRecord] = []
        for feed_url in self.feed_urls:
            try:
                response = requests.get(feed_url, timeout=self.timeout_seconds)
                response.raise_for_status()
            except requests.RequestException as exc:
                raise RuntimeError(f"RSS search failed safely for {feed_url}: {exc}") from exc

            sources.extend(self._parse_feed(response.text, feed_url, topic))

        if not sources:
            raise RuntimeError("RSS search failed safely: no usable feed items with links were returned")

        return sources

    def _parse_feed(self, feed_content: str, feed_url: str, topic: str) -> list[SourceRecord]:
        try:
            root = ET.fromstring(feed_content)
        except ET.ParseError as exc:
            raise RuntimeError(f"RSS search failed safely for {feed_url}: feed XML could not be parsed") from exc

        items = root.findall(".//item")
        if not items:
            items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

        sources: list[SourceRecord] = []
        for item in items:
            title = self._text(item, "title") or "Untitled RSS item"
            link = self._text(item, "link") or self._atom_link(item)
            description = (
                self._text(item, "description")
                or self._text(item, "summary")
                or self._text(item, "{http://www.w3.org/2005/Atom}summary")
                or title
            )

            if not link:
                continue
            if topic and topic.lower() not in f"{title} {description}".lower():
                continue

            sources.append(
                SourceRecord(
                    title=title,
                    url=link,
                    excerpt=description,
                    retrieved_at=datetime.now(timezone.utc),
                    provider="rss",
                    metadata={"feed_url": feed_url},
                )
            )

        return sources

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


def get_search_adapter(
    provider: str = "placeholder",
    searxng_base_url: str = "http://searxng:8080",
    rss_feed_urls: str | list[str] = "",
) -> SearchAdapter:
    normalized_provider = provider.strip().lower()
    if normalized_provider == "placeholder":
        return PlaceholderSearchAdapter()
    if normalized_provider == "searxng":
        return SearXNGSearchAdapter(base_url=searxng_base_url)
    if normalized_provider == "rss":
        urls = rss_feed_urls.split(",") if isinstance(rss_feed_urls, str) else rss_feed_urls
        return RssSearchAdapter(feed_urls=urls)
    raise ValueError(
        f"Unsupported search provider '{provider}'. Supported providers: placeholder, searxng, rss."
    )
