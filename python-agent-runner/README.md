# Python Agent Runner

Minimal FastAPI-based agent runner skeleton for Agentic Newsroom.

This service is intentionally local-first. It does not call Tavily, OpenAI, Gemini, Ollama, DynamoDB, S3, or SQS in this slice.

## What It Provides

- `GET /health` health endpoint.
- `POST /runs` endpoint accepting a topic.
- Pydantic schemas for run requests, source records, drafts, editor decisions, and final story records.
- Placeholder search adapter.
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

## Test

```powershell
pytest
```

No cloud credentials are required for tests.

