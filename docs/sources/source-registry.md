# Source Registry

Agentic Newsroom uses source registries to keep local-first research sources reusable across workflows and clients.

RSS feeds should be handled by the Python RSS adapter directly. SearXNG remains a metasearch provider and should not be used as the RSS ingestion layer.

## RSS Registry

Default path:

```text
config/sources/rss_sources.yml
```

The registry supports:

- `id`
- `name`
- `type`
- `enabled`
- `url`
- `fallback_urls`
- `category`
- `tags`
- `max_items`
- `max_age_days`
- `excerpt_chars`
- `cache_ttl_seconds`
- `default_query_terms` or `filter_terms`
- `notes`

## First Source

The first configured source is:

```text
zdi_published_2026
```

It points to:

```text
https://www.zerodayinitiative.com/rss/published/2026/
```

Fallback:

```text
https://www.zerodayinitiative.com/rss/published/
```

## Configuration

Registry-based RSS sources are preferred:

```text
SEARCH_PROVIDER=rss
RSS_SOURCE_REGISTRY_PATH=config/sources/rss_sources.yml
RSS_SOURCE_IDS=zdi_published_2026
```

Client requests can still choose result counts through `/research` using `max_sources`. Service-level defaults and caps are controlled by:

```text
NEWSROOM_DEFAULT_MAX_SOURCES=25
NEWSROOM_SYSTEM_MAX_SOURCES=250
```

The registry can define source-level processing preferences such as `max_items`, but `10` is not a fixed newsroom-wide limit.

The older quick-test mode remains available:

```text
RSS_FEED_URLS=https://example.com/feed.xml,https://example.org/rss.xml
```

## Future Cache Options

The current scaffold uses in-memory response caching with placeholder metadata for future conditional requests.

Future persistent cache options:

- local SQLite
- S3 object cache
- DynamoDB metadata cache
