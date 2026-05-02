# Python Agent Runner

Minimal FastAPI-based agent runner skeleton for Agentic Newsroom.

This service is intentionally local-first. It does not require Tavily, OpenAI, Gemini, Ollama, DynamoDB, S3, or SQS in this slice.

## What It Provides

- `GET /health` health endpoint.
- `POST /runs` endpoint accepting a topic.
- `POST /research` service endpoint for reusable research requests from other apps.
- Pydantic schemas for run requests, source records, drafts, editor decisions, and final story records.
- Placeholder search adapter.
- Optional self-hosted SearXNG search adapter.
- RSS feed search adapter.
- Deterministic/template-based Journalist Agent drafts assembled from retrieved `SourceRecord` objects.
- Deterministic fact-checking stubs for numbers, percentages, dates, quotes, and source URL presence.
- AWS storage wrapper stubs that are safe for unit tests and dry-run local execution.

## Install

```powershell
cd python-agent-runner
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```powershell
uvicorn app.main:app --reload
```

## Search Providers

Default dry-run mode:

```powershell
$env:SEARCH_PROVIDER="placeholder"
```

Self-hosted SearXNG mode:

```powershell
$env:SEARCH_PROVIDER="searxng"
$env:SEARXNG_BASE_URL="http://localhost:8080"
```

RSS mode:

```powershell
$env:SEARCH_PROVIDER="rss"
$env:RSS_SOURCE_REGISTRY_PATH="config/sources/rss_sources.yml"
$env:RSS_SOURCE_IDS="zdi_published_2026"
```

Quick RSS experiments can still use:

```powershell
$env:RSS_FEED_URLS="https://example.com/feed.xml,https://example.org/rss.xml"
```

Registry-based sources are preferred. The first test source is `zdi_published_2026`, with `https://www.zerodayinitiative.com/rss/published/2026/` as primary and `https://www.zerodayinitiative.com/rss/published/` as fallback.

Tests mock SearXNG and RSS responses and do not call real external services.

## Journalist Agent

The current Journalist Agent is deterministic and template-based. It does not call an LLM. Drafts are assembled from the retrieved `SourceRecord` objects and include source titles, URLs, provider/source metadata, published timestamps when present, and source excerpts.

Drafts also include `source_support`, a compact deterministic support map for each key item. Each entry records the source ID, title, URL, provider, published timestamp when present, excerpt hash, excerpt preview, and supported fields.

LLM summarization and richer narrative drafting are future functionality. Any future synthesis step must preserve source support mapping. Current output should be treated as a source-grounded draft packet for editor review, not final reporting.

## Research Endpoint

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8000/research" `
  -ContentType "application/json" `
  -Body '{"topic":"ZDI vulnerability advisory","source_provider":"rss","source_ids":["zdi_published_2026"],"max_sources":5}'
```

The response includes `metadata` with result-limit information:

```json
{
  "requested_max_sources": 100,
  "effective_max_sources": 100,
  "system_max_sources": 250,
  "capped": false,
  "result_count": 25,
  "page_size": null,
  "cursor": null,
  "next_cursor": null
}
```

`max_sources` is optional. Omitted or null values use `NEWSROOM_DEFAULT_MAX_SOURCES`; requests above `NEWSROOM_SYSTEM_MAX_SOURCES` are capped. There is no fixed limit of 10.

Future pagination fields `page_size`, `cursor`, and `next_cursor` are accepted now, but persistent pagination is not implemented yet.

## Optional Local Auth

Auth is disabled by default for local development:

```powershell
$env:REQUIRE_AUTH="false"
```

To test API-key protection:

```powershell
$env:REQUIRE_AUTH="true"
$env:NEWSROOM_API_KEY="replace-with-local-dev-key"
```

Then send either:

```text
X-Newsroom-Api-Key: replace-with-local-dev-key
```

or:

```text
Authorization: Bearer replace-with-local-dev-key
```

## Test

```powershell
pytest
```

No cloud credentials are required for tests.
