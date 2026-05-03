# DynamoDB Persistence Design

Agentic Newsroom uses DynamoDB as a compact run ledger, index, and dashboard query layer. It is not the system of record for large research payloads.

## Design Decision

S3 is the primary artifact store for large payloads:

- Raw inbound requests.
- Raw RSS, search, or provider responses.
- Normalized source sets.
- Full research responses.
- Draft Markdown.
- Fact-check reports.
- Editor decisions.
- Future LLM transcripts.
- Events and logs.

DynamoDB stores compact metadata, operational status, query fields, and S3 pointers. Large JSON blobs, source bodies, transcripts, and logs should be written to S3 and referenced by key.

## Why DynamoDB Stays Compact

DynamoDB items have strict size limits and become harder to query, update, and reason about when large nested payloads are embedded directly. Keep each run item safely below service limits by storing previews and indexes only.

Recommended DynamoDB responsibilities:

- Dashboard list queries.
- Status and lifecycle tracking.
- Compact search/filter fields.
- S3 artifact discovery through pointer fields.
- Fact-check and editor summary fields.

Avoid storing:

- Full source text.
- Raw feeds.
- Full `/research` responses.
- Draft bodies beyond short previews.
- Large fact-check details.
- LLM transcripts.
- Verbose logs.

## Run Ledger Item Shape

Primary key:

```json
{
  "run_id": "run_abc123",
  "record_type": "run"
}
```

Compact metadata fields:

```json
{
  "run_id": "run_abc123",
  "record_type": "run",
  "status": "completed",
  "topic": "latest software vulnerabilities",
  "domain": "research",
  "intent": "briefing",
  "category": "cybersecurity",
  "tags": ["vulnerabilities", "advisories"],
  "source_provider": "rss",
  "source_ids": ["zdi_published_2026"],
  "result_count": 50,
  "created_at": "2026-05-02T22:00:26Z",
  "updated_at": "2026-05-02T22:00:31Z",
  "draft_preview": "This deterministic draft is based on retrieved sources...",
  "fact_check_passed": true,
  "editor_status": "accept"
}
```

S3 pointer fields:

```json
{
  "artifact_bucket": "agentic-newsroom-dev-artifacts",
  "artifact_prefix": "runs/env=dev/year=2026/month=05/day=02/run_id=run_abc123/",
  "manifest_s3_key": "runs/env=dev/year=2026/month=05/day=02/run_id=run_abc123/manifest.json",
  "full_response_s3_key": "runs/env=dev/year=2026/month=05/day=02/run_id=run_abc123/response/full_response.json",
  "draft_s3_key": "runs/env=dev/year=2026/month=05/day=02/run_id=run_abc123/drafts/draft.md",
  "sources_s3_key": "runs/env=dev/year=2026/month=05/day=02/run_id=run_abc123/sources/normalized_sources.json",
  "fact_check_s3_key": "runs/env=dev/year=2026/month=05/day=02/run_id=run_abc123/fact-check/fact_check.json",
  "events_s3_key": "runs/env=dev/year=2026/month=05/day=02/run_id=run_abc123/events/events.jsonl"
}
```

Suggested GSI fields:

- `status` + `created_at` for operational dashboards.
- `category` + `created_at` for domain-specific research views.
- `source_provider` + `created_at` for provider health and audit views.

The current Terraform blueprint defines the `status-created-at` GSI. Additional GSIs should be added only when real dashboard query patterns are clear.

## Write Consistency And Partial Failures

S3 and DynamoDB writes are not one transaction. Persistence code must handle partial failure explicitly.

Recommended write order for completed runs:

1. Write S3 artifacts under the run prefix.
2. Write `manifest.json` last after artifact keys are known.
3. Upsert the compact DynamoDB run item with S3 pointer fields.
4. If DynamoDB fails after S3 succeeds, retry the ledger write and mark the run for reconciliation.
5. If an S3 artifact fails, do not mark the DynamoDB run as complete; write a failed or partial status with the error summary when possible.

For local development, Phase 1 should use a local file artifact store that mimics the same S3 key structure.

