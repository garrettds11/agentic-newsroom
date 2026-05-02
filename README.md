# Agentic Newsroom

Agentic Newsroom is a hybrid, local-first Journalist-Editor newsroom system for topic intake, research, drafting, review, fact checking, and durable archiving.

## Architecture Overview

- **PyGPT desktop cockpit:** topic input, prompt testing, human review, and notifications.
- **n8n workflow orchestrator:** local workflow coordination through Docker Compose.
- **Python agent runtime:** Journalist Agent, Editor Agent, deterministic fact checker, schema validation, retry handling, and AWS writes.
- **Search adapters:** placeholder by default, optional self-hosted SearXNG, RSS feeds, and future paid APIs only when intentionally configured.
- **AWS persistence:** DynamoDB for run state and metadata, S3 for raw sources, drafts, artifacts, and logs, and SQS for queued jobs.

## Local-First Principles

- Keep development runnable without cloud writes by default.
- Use placeholder adapters until real provider credentials are intentionally configured.
- Do not require Tavily or any paid search API for local development.
- Never commit real secrets, account IDs, API keys, private credentials, or region-specific ARNs.
- Do not run `terraform apply` from this repository without explicit human approval.

## Planned Runtime Shape

Docker Compose includes a local blueprint for:

- n8n
- Postgres for n8n persistence
- Python Agent Runner
- Optional Ollama for local model experiments

## Prerequisites

Future implementation slices may require:

- Docker Desktop
- Python 3.11+
- Terraform
- AWS CLI configured outside the repository
- Optional external search API keys
- Optional OpenAI, Gemini, or local Ollama model access

## Search Providers

Default dry-run mode:

```text
SEARCH_PROVIDER=placeholder
```

Self-hosted SearXNG mode:

```text
SEARCH_PROVIDER=searxng
SEARXNG_BASE_URL=http://searxng:8080
```

RSS mode:

```text
SEARCH_PROVIDER=rss
RSS_FEED_URLS=https://example.com/feed.xml,https://example.org/rss.xml
```

Tavily and other paid APIs are optional future adapters, not required defaults.

See [IMPLEMENT.md](IMPLEMENT.md) and the backlog slices in [backlog/slices](backlog/slices) for the staged implementation plan.
