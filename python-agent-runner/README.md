# Python Agent Runner

Minimal FastAPI-based agent runner skeleton for Agentic Newsroom.

This service is intentionally local-first. It does not require Tavily, OpenAI, Gemini, Ollama, DynamoDB, S3, or SQS in this slice.

## What It Provides

- `GET /health` health endpoint.
- `POST /runs` endpoint accepting a topic.
- Pydantic schemas for run requests, source records, drafts, editor decisions, and final story records.
- Placeholder search adapter.
- Optional self-hosted SearXNG search adapter.
- RSS feed search adapter.
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
$env:RSS_FEED_URLS="https://example.com/feed.xml,https://example.org/rss.xml"
```

Tests mock SearXNG and RSS responses and do not call real external services.

## Test

```powershell
pytest
```

No cloud credentials are required for tests.
