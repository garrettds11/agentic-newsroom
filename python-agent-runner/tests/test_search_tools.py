import pytest
import requests

from app.search_tools import (
    PlaceholderSearchAdapter,
    RssSearchAdapter,
    SearXNGSearchAdapter,
    get_search_adapter,
)


class MockResponse:
    def __init__(
        self,
        json_payload=None,
        text: str = "",
        status_error: Exception | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self._json_payload = json_payload
        self.text = text
        self._status_error = status_error
        self.headers = headers or {}

    def raise_for_status(self) -> None:
        if self._status_error:
            raise self._status_error

    def json(self):
        if isinstance(self._json_payload, Exception):
            raise self._json_payload
        return self._json_payload


def test_placeholder_adapter_still_works() -> None:
    sources = PlaceholderSearchAdapter().search("local newsroom")

    assert len(sources) == 1
    assert sources[0].provider == "placeholder"
    assert str(sources[0].url) == "https://example.com/agentic-newsroom-placeholder-source"


def test_searxng_adapter_parses_mocked_json(monkeypatch) -> None:
    def fake_get(url, params, timeout):
        assert url == "http://searxng:8080/search"
        assert params == {"q": "climate policy", "format": "json"}
        assert timeout == 10
        return MockResponse(
            json_payload={
                "results": [
                    {
                        "title": "Climate policy update",
                        "url": "https://example.com/climate-policy",
                        "content": "A local climate policy story.",
                        "engine": "mock",
                        "score": 1.0,
                    }
                ]
            }
        )

    monkeypatch.setattr(requests, "get", fake_get)

    sources = SearXNGSearchAdapter().search("climate policy")

    assert len(sources) == 1
    assert sources[0].provider == "searxng"
    assert sources[0].title == "Climate policy update"
    assert str(sources[0].url) == "https://example.com/climate-policy"
    assert sources[0].metadata["engine"] == "mock"


def test_rss_adapter_parses_mocked_feed_content(monkeypatch) -> None:
    feed = """
    <rss version="2.0">
      <channel>
        <item>
          <title>Local transit budget approved</title>
          <link>https://example.com/transit-budget</link>
          <description>City officials approved the transit budget.</description>
        </item>
      </channel>
    </rss>
    """

    def fake_get(url, timeout):
        assert url == "https://example.com/feed.xml"
        assert timeout == 10
        return MockResponse(text=feed)

    monkeypatch.setattr(requests, "get", fake_get)

    sources = RssSearchAdapter(["https://example.com/feed.xml"]).search("transit")

    assert len(sources) == 1
    assert sources[0].provider == "rss"
    assert sources[0].title == "Local transit budget approved"
    assert str(sources[0].url) == "https://example.com/transit-budget"
    assert sources[0].metadata["feed_url"] == "https://example.com/feed.xml"


def test_loads_registry_and_selects_source_id(tmp_path) -> None:
    registry = tmp_path / "rss_sources.yml"
    registry.write_text(
        """
sources:
  - id: local_source
    name: Local Source
    type: rss
    enabled: true
    url: https://example.com/rss.xml
    category: local
    tags:
      - civic
""",
        encoding="utf-8",
    )

    from app.search_tools import load_rss_source_registry, select_rss_sources

    sources = load_rss_source_registry(str(registry))
    selected = select_rss_sources(sources, ["local_source"])

    assert selected[0].id == "local_source"
    assert selected[0].category == "local"
    assert selected[0].tags == ["civic"]


def test_rss_adapter_uses_fallback_dedupes_limits_and_preserves_metadata(monkeypatch, tmp_path) -> None:
    RssSearchAdapter._response_cache.clear()
    registry = tmp_path / "rss_sources.yml"
    registry.write_text(
        """
sources:
  - id: fallback_source
    name: Fallback Source
    type: rss
    enabled: true
    url: https://example.com/primary.xml
    fallback_urls:
      - https://example.com/fallback.xml
    category: test
    tags:
      - fallback
    max_items: 1
    excerpt_chars: 20
    cache_ttl_seconds: 900
""",
        encoding="utf-8",
    )
    feed = """
    <rss version="2.0">
      <channel>
        <item>
          <title>Newest fallback item</title>
          <link>https://example.com/newest</link>
          <guid>same-guid</guid>
          <pubDate>Sat, 02 May 2026 14:00:00 GMT</pubDate>
          <description>This description is intentionally long enough to truncate.</description>
        </item>
        <item>
          <title>Duplicate fallback item</title>
          <link>https://example.com/duplicate</link>
          <guid>same-guid</guid>
          <pubDate>Sat, 02 May 2026 13:00:00 GMT</pubDate>
          <description>This duplicate should be removed.</description>
        </item>
      </channel>
    </rss>
    """
    calls: list[str] = []

    def fake_get(url, timeout):
        calls.append(url)
        if "primary" in url:
            raise requests.ConnectionError("primary unavailable")
        return MockResponse(text=feed, headers={"ETag": "abc", "Last-Modified": "Sat, 02 May 2026 14:00:00 GMT"})

    monkeypatch.setattr(requests, "get", fake_get)

    sources = RssSearchAdapter(
        registry_path=str(registry),
        source_ids=["fallback_source"],
        default_max_items=10,
        default_excerpt_chars=100,
    ).search("fallback")

    assert calls == ["https://example.com/primary.xml", "https://example.com/fallback.xml"]
    assert len(sources) == 1
    assert sources[0].title == "Newest fallback item"
    assert sources[0].excerpt.endswith("...")
    assert len(sources[0].excerpt) <= 20
    assert str(sources[0].url) == "https://example.com/newest"
    assert sources[0].metadata["source_id"] == "fallback_source"
    assert sources[0].metadata["source_category"] == "test"
    assert sources[0].metadata["source_tags"] == ["fallback"]
    assert sources[0].metadata["cache"]["etag"] == "abc"


def test_unsupported_provider_raises_clear_error() -> None:
    with pytest.raises(ValueError, match="Unsupported search provider 'paid-api'"):
        get_search_adapter("paid-api")


def test_searxng_adapter_fails_safely_on_bad_json(monkeypatch) -> None:
    def fake_get(url, params, timeout):
        return MockResponse(json_payload=ValueError("bad json"))

    monkeypatch.setattr(requests, "get", fake_get)

    with pytest.raises(RuntimeError, match="response was not valid JSON"):
        SearXNGSearchAdapter().search("topic")


def test_rss_adapter_fails_safely_without_urls() -> None:
    with pytest.raises(RuntimeError, match="configure RSS_SOURCE_IDS with a registry or provide RSS_FEED_URLS"):
        RssSearchAdapter([]).search("topic")
