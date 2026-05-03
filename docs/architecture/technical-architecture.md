# Technical Architecture

Agentic Newsroom is designed as a hybrid local-first system with clear boundaries between cockpit, orchestration, agent runtime, external providers, and persistence.

The Python runner is also shaped as a reusable research service for other local apps. `/runs` remains backward compatible, while `/research` is the service-oriented endpoint for future clients.

## Components

### PyGPT Desktop Cockpit

PyGPT is the human-facing cockpit for:

- Topic input.
- Prompt testing.
- Draft review.
- Notifications.
- Manual approval gates.

PyGPT should call local endpoints, n8n webhooks, or file-based handoff points depending on the implementation slice.

### n8n Orchestrator

n8n coordinates workflow state and handoffs:

- Intake from PyGPT.
- Queue job creation.
- Python Agent Runner invocation.
- Review loop routing.
- Notification steps.
- Optional persistence handoff.

n8n should run locally in Docker Compose when implemented. Postgres should back n8n state in local development.

### Python Agent Runner

The Python runtime owns the deeper newsroom behavior:

- Journalist Agent.
- Editor Agent.
- Deterministic fact checker.
- Schema validation.
- Retry handling.
- Source capture normalization.
- S3, DynamoDB, and SQS adapters.
- Placeholder, SearXNG, and RSS search adapters.

The runner should default to dry-run local mode.

### External Search APIs

Search should be adapter-based. The default target is the local placeholder adapter. No-cost/local-first targets include self-hosted SearXNG and configured RSS feeds. Tavily, Firecrawl, Serper, Google Search Grounding, or other paid APIs may be added later as optional adapters, but they are not required.

SearXNG is a metasearch provider. RSS feeds are ingested directly by the RSS adapter through the source registry.

Adapters must return normalized source records with:

- URL or source identifier.
- Retrieval timestamp.
- Title or label.
- Extracted text or summary.
- Provider metadata.

Current provider values:

- `placeholder`: default dry-run source.
- `searxng`: self-hosted SearXNG endpoint, normally `http://searxng:8080` inside Docker Compose.
- `rss`: registry-based RSS ingestion through `RSS_SOURCE_REGISTRY_PATH` and `RSS_SOURCE_IDS`.

`RSS_FEED_URLS` remains available for quick local experiments, but the registry is preferred for reusable sources.

### Inbound Research Requests

Future clients should call `POST /research` with optional fields such as:

- `topic`
- `audience`
- `angle`
- `source_provider`
- `source_ids`
- `max_sources`
- `sort`
- `time_window`
- `tags`
- `category`
- `output_format`
- `page_size`
- `cursor`

Auth is disabled by default for local development. When exposed beyond localhost, enable `REQUIRE_AUTH=true` and provide `NEWSROOM_API_KEY` outside source control.

Result limits are service-layer configuration, not adapter business rules. Defaults are `NEWSROOM_DEFAULT_MAX_SOURCES=25` and `NEWSROOM_SYSTEM_MAX_SOURCES=250`. Clients may request larger sets within the safety cap. Pagination is planned through `page_size`, `cursor`, and `next_cursor`, with `next_cursor` currently returned as `null`.

### RSS Source Registry

The default registry is [rss_sources.yml](../../config/sources/rss_sources.yml). The first test source is `zdi_published_2026`, backed by ZDI published advisories.

The RSS adapter supports enabled-source filtering, fallback URLs, max item limits, excerpt truncation, deduplication, newest-first sorting when dates are available, source metadata preservation, and in-memory cache TTLs. Future persistent cache options include local SQLite, S3 object cache, and DynamoDB metadata cache.

### AWS Persistence

AWS is optional and should be disabled by default.

- **S3:** primary artifact store and system of record for raw requests, raw feed/search payloads, normalized sources, full responses, drafts, fact-check reports, editor decisions, future transcripts, and logs.
- **DynamoDB:** compact run ledger, dashboard index, status tracker, metadata store, and S3 pointer layer.
- **SQS:** queued research or editorial jobs.

Large payloads must be written to S3, not embedded in DynamoDB items. DynamoDB should store compact fields such as `run_id`, `status`, `topic`, `category`, `tags`, `source_provider`, `source_ids`, `result_count`, `draft_preview`, `fact_check_passed`, `editor_status`, and S3 keys such as `manifest_s3_key`, `full_response_s3_key`, `draft_s3_key`, `sources_s3_key`, `fact_check_s3_key`, and `events_s3_key`.

S3 keys should follow the run-scoped layout:

```text
runs/env=<env>/year=<YYYY>/month=<MM>/day=<DD>/run_id=<run_id>/
```

S3 and DynamoDB writes are not transactional together, so persistence code must handle partial failures and reconciliation. The first implementation phase should use a local file artifact store that mirrors the S3 key structure before enabling AWS writes.

Terraform should define resources without hard-coded account IDs, API keys, private credentials, or region-specific ARNs.

See [dynamodb-persistence-design.md](../aws/dynamodb-persistence-design.md) and [s3-artifact-design.md](../aws/s3-artifact-design.md).

### Presentation Layer

The dashboard list should read compact metadata from DynamoDB through a backend API. Run detail views should read the DynamoDB item, then load the S3 manifest and selected artifacts through the backend. Browsers should not directly access DynamoDB or S3 in v1.

### Optional Ollama

Ollama may be included in Docker Compose for local model experiments. It must remain optional because not all operators will have the same hardware or model inventory.

## Data Flow

1. PyGPT sends a topic to n8n.
2. n8n creates or receives a job request.
3. n8n invokes the Python Agent Runner directly or through a queue.
4. The runner uses search adapters to collect source material.
5. The Journalist Agent creates a sourced draft.
6. The deterministic fact checker validates citations, schema, source coverage, and prohibited claims.
7. The Editor Agent reviews the draft and requests revisions when needed.
8. The runner stays in dry-run local mode by default; the current scaffold uses in-memory storage stubs.
9. When enabled, AWS adapters persist metadata to DynamoDB, objects to S3, and queued jobs to SQS.
10. n8n notifies PyGPT or the human operator for review.

See [technical-view.mmd](diagrams/technical-view.mmd) for the detailed architecture diagram.
