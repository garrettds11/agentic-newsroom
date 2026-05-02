# Research Request Contract

Agentic Newsroom is a local-first research service for PyGPT, n8n, and future client apps.

The LLM may help form a JSON request, but the host app or integration tool sends that JSON to n8n or the Python Agent Runner. n8n is the preferred listener and orchestrator for external clients. The Python Agent Runner is the runtime and research service.

Current drafts are deterministic source-grounded drafts assembled from retrieved `SourceRecord` objects. Drafts include a `source_support` map that links each key item back to source IDs, titles, URLs, providers, timestamps when available, excerpt hashes, and excerpt previews.

LLM summarization and richer generated analysis are future functionality. Any future LLM synthesis must preserve source support.

Auth is optional for local development. Enable API-key auth before exposing endpoints beyond localhost.

## Endpoint

Preferred service endpoint:

```text
POST /research
```

n8n webhook endpoint for external clients:

```text
POST /webhook/newsroom-research
```

Backward-compatible endpoint:

```text
POST /runs
```

## Request Fields

- `topic`: natural-language research topic.
- `source_provider`: `placeholder`, `rss`, `searxng`, or future `auto`.
- `source_ids`: registry source IDs such as `zdi_published_2026`.
- `category`: broad source category, such as `cybersecurity`.
- `tags`: source or query tags.
- `max_sources`: caller-requested result count. If omitted or null, the service uses `NEWSROOM_DEFAULT_MAX_SOURCES`.
- `sort`: requested sort, such as `published_desc`.
- `time_window`: requested time window, such as `24h`, `7d`, or `30d`.
- `output_format`: requested output shape, such as `brief`, `story`, or `detailed_report`.
- `page_size`: future pagination page size placeholder.
- `cursor`: future pagination cursor placeholder.

## Result Limits

Result limits are configurable:

```text
NEWSROOM_DEFAULT_MAX_SOURCES=25
NEWSROOM_SYSTEM_MAX_SOURCES=250
```

There is no fixed system limit of 10. Client apps may request larger result sets with `max_sources`, and the service caps requests at `NEWSROOM_SYSTEM_MAX_SOURCES`.

The `/research` response includes:

- `requested_max_sources`
- `effective_max_sources`
- `system_max_sources`
- `capped`
- `result_count`
- `page_size`
- `cursor`
- `next_cursor`

`next_cursor` is currently `null`; persistent pagination is future work.

## Example A

User asks:

```text
get me the latest software vulnerabilities
```

JSON:

```json
{
  "topic": "latest software vulnerabilities",
  "source_provider": "rss",
  "category": "cybersecurity",
  "tags": ["vulnerabilities", "advisories"],
  "sort": "published_desc",
  "max_sources": 50,
  "output_format": "brief"
}
```

`source_provider` may become `auto` in a future routing layer. Today, use `rss` or another implemented provider.

## Example B

User asks:

```text
get me the latest ZDI advisories
```

JSON:

```json
{
  "topic": "latest ZDI advisories",
  "source_provider": "rss",
  "source_ids": ["zdi_published_2026"],
  "sort": "published_desc",
  "max_sources": 100,
  "output_format": "brief"
}
```

## Example C

User asks:

```text
summarize the latest cybersecurity advisories from configured feeds
```

JSON:

```json
{
  "topic": "latest cybersecurity advisories",
  "source_provider": "rss",
  "source_ids": ["zdi_published_2026"],
  "category": "cybersecurity",
  "tags": ["vulnerabilities", "advisories"],
  "sort": "published_desc",
  "max_sources": 100,
  "output_format": "detailed_report"
}
```

When more configured feeds exist, clients can include multiple `source_ids`.

## Auth

For local-only development:

```text
REQUIRE_AUTH=false
```

Before exposing beyond localhost:

```text
REQUIRE_AUTH=true
NEWSROOM_API_KEY=<local-secret-outside-git>
```

Send one of:

```text
X-Newsroom-Api-Key: <key>
```

```text
Authorization: Bearer <key>
```

When clients call n8n, they may include `X-Newsroom-Api-Key`. The placeholder n8n workflow forwards this header to the Python runner. n8n itself does not enforce auth yet.
