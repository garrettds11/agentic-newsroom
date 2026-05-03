# Agentic Newsroom

Agentic Newsroom is a hybrid, local-first Journalist-Editor newsroom system for topic intake, research, drafting, review, fact checking, and durable archiving.

It is also evolving into a reusable local-first research service that other apps can call for normalized source records and reviewed story artifacts.

## Architecture Overview

- **PyGPT desktop cockpit:** topic input, prompt testing, human review, and notifications.
- **n8n workflow orchestrator:** local workflow coordination through Docker Compose.
- **Python agent runtime:** Journalist Agent, Editor Agent, deterministic fact checker, schema validation, retry handling, and AWS writes.
- **Search adapters:** placeholder by default, optional self-hosted SearXNG, RSS feeds, and future paid APIs only when intentionally configured.
- **AWS persistence:** S3 as the artifact store for large research payloads, DynamoDB as the compact run ledger and dashboard index, and SQS for queued jobs.

## Local-First Principles

- Keep development runnable without cloud writes by default.
- Use placeholder adapters until real provider credentials are intentionally configured.
- Do not require Tavily or any paid search API for local development.
- Prefer registry-based RSS sources for reusable feed ingestion.
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
RSS_SOURCE_REGISTRY_PATH=config/sources/rss_sources.yml
RSS_SOURCE_IDS=zdi_published_2026
```

`RSS_FEED_URLS` is still available for quick local experiments, but registry-based sources are preferred. ZDI published advisories are the first test source.

SearXNG is metasearch. It is not used to ingest RSS feeds.

Tavily and other paid APIs are optional future adapters, not required defaults.

## Research Service

Other local apps can call:

```text
POST /research
```

External/local clients should generally call n8n as the listener and orchestrator:

```text
POST /webhook/newsroom-research
```

Result limits are configurable; `10` is not a fixed system limit:

```text
NEWSROOM_DEFAULT_MAX_SOURCES=25
NEWSROOM_SYSTEM_MAX_SOURCES=250
```

Client apps can request larger result sets with `max_sources` within the system safety cap. Future pagination is represented by `page_size`, `cursor`, and `next_cursor`.

PyGPT can ask an LLM to form the JSON request, but PyGPT or an integration tool sends the request to n8n or the Python runner.

Local authentication is optional by default. When exposing beyond localhost, enable API-key checks with:

```text
REQUIRE_AUTH=true
NEWSROOM_API_KEY=replace-with-local-secret-outside-git
```

See [research-request-contract.md](docs/api/research-request-contract.md) for the client request contract.

## Persistence Design

Large research artifacts should be written to S3, while DynamoDB stores compact run metadata and S3 pointers. DynamoDB should not store raw feeds, full source sets, full responses, draft bodies, future LLM transcripts, or verbose logs directly.

Recommended S3 run prefix:

```text
runs/env=<env>/year=<YYYY>/month=<MM>/day=<DD>/run_id=<run_id>/
```

See [dynamodb-persistence-design.md](docs/aws/dynamodb-persistence-design.md) and [s3-artifact-design.md](docs/aws/s3-artifact-design.md) for the artifact manifest, DynamoDB record shape, and phased implementation plan.

See [IMPLEMENT.md](IMPLEMENT.md) and the backlog slices in [backlog/slices](backlog/slices) for the staged implementation plan.
