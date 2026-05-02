import pytest
import requests

from app.search_tools import (
    PlaceholderSearchAdapter,
    RssSearchAdapter,
    SearXNGSearchAdapter,
    get_search_adapter,
)


class MockResponse:
    def __init__(self, json_payload=None, text: str = "", status_error: Exception | None = None) -> None:
        self._json_payload = json_payload
        self.text = text
        self._status_error = status_error

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
    with pytest.raises(RuntimeError, match="RSS_FEED_URLS is empty"):
        RssSearchAdapter([]).search("topic")
