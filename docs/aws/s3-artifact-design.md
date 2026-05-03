# S3 Artifact Design

S3 is the artifact store and system of record for large Agentic Newsroom research payloads. DynamoDB should point to these objects instead of embedding large blobs.

## Bucket Role

The artifact bucket stores:

- Raw inbound request JSON.
- Raw feed or search payloads.
- Normalized source records.
- Full research response JSON.
- Draft Markdown.
- Fact-check report JSON.
- Editor decision JSON.
- Events and logs.
- `manifest.json` for artifact discovery.

The bucket must keep public access blocked and server-side encryption enabled. Versioning is recommended for auditability and recovery.

## Key Structure

Use a run-scoped prefix:

```text
runs/env=<env>/year=<YYYY>/month=<MM>/day=<DD>/run_id=<run_id>/
```

Recommended object keys:

```text
runs/env=<env>/year=<YYYY>/month=<MM>/day=<DD>/run_id=<run_id>/request/raw_request.json
runs/env=<env>/year=<YYYY>/month=<MM>/day=<DD>/run_id=<run_id>/raw/provider_payload.json
runs/env=<env>/year=<YYYY>/month=<MM>/day=<DD>/run_id=<run_id>/sources/normalized_sources.json
runs/env=<env>/year=<YYYY>/month=<MM>/day=<DD>/run_id=<run_id>/response/full_response.json
runs/env=<env>/year=<YYYY>/month=<MM>/day=<DD>/run_id=<run_id>/drafts/draft.md
runs/env=<env>/year=<YYYY>/month=<MM>/day=<DD>/run_id=<run_id>/fact-check/fact_check.json
runs/env=<env>/year=<YYYY>/month=<MM>/day=<DD>/run_id=<run_id>/editor/editor_decision.json
runs/env=<env>/year=<YYYY>/month=<MM>/day=<DD>/run_id=<run_id>/events/events.jsonl
runs/env=<env>/year=<YYYY>/month=<MM>/day=<DD>/run_id=<run_id>/manifest.json
```

## Manifest Schema

`manifest.json` is the compact discovery document for a run's artifacts.

```json
{
  "run_id": "run_abc123",
  "environment": "dev",
  "created_at": "2026-05-02T22:00:26Z",
  "topic": "latest software vulnerabilities",
  "artifact_version": "1",
  "objects": {
    "raw_request": {
      "bucket": "agentic-newsroom-dev-artifacts",
      "key": "runs/env=dev/year=2026/month=05/day=02/run_id=run_abc123/request/raw_request.json",
      "content_type": "application/json",
      "size_bytes": 512,
      "sha256": "optional-hex-digest"
    },
    "normalized_sources": {
      "bucket": "agentic-newsroom-dev-artifacts",
      "key": "runs/env=dev/year=2026/month=05/day=02/run_id=run_abc123/sources/normalized_sources.json",
      "content_type": "application/json",
      "size_bytes": 48192,
      "sha256": "optional-hex-digest"
    },
    "full_response": {
      "bucket": "agentic-newsroom-dev-artifacts",
      "key": "runs/env=dev/year=2026/month=05/day=02/run_id=run_abc123/response/full_response.json",
      "content_type": "application/json",
      "size_bytes": 62344,
      "sha256": "optional-hex-digest"
    },
    "draft_markdown": {
      "bucket": "agentic-newsroom-dev-artifacts",
      "key": "runs/env=dev/year=2026/month=05/day=02/run_id=run_abc123/drafts/draft.md",
      "content_type": "text/markdown",
      "size_bytes": 8192,
      "sha256": "optional-hex-digest"
    },
    "fact_check": {
      "bucket": "agentic-newsroom-dev-artifacts",
      "key": "runs/env=dev/year=2026/month=05/day=02/run_id=run_abc123/fact-check/fact_check.json",
      "content_type": "application/json",
      "size_bytes": 4096,
      "sha256": "optional-hex-digest"
    },
    "editor_decision": {
      "bucket": "agentic-newsroom-dev-artifacts",
      "key": "runs/env=dev/year=2026/month=05/day=02/run_id=run_abc123/editor/editor_decision.json",
      "content_type": "application/json",
      "size_bytes": 2048,
      "sha256": "optional-hex-digest"
    },
    "events": {
      "bucket": "agentic-newsroom-dev-artifacts",
      "key": "runs/env=dev/year=2026/month=05/day=02/run_id=run_abc123/events/events.jsonl",
      "content_type": "application/x-ndjson",
      "size_bytes": 16384,
      "sha256": "optional-hex-digest"
    }
  }
}
```

`size_bytes` and `sha256` are optional at first but should be populated once artifact writes become production paths.

## Presentation Reads

The browser should not access S3 or DynamoDB directly in v1.

Recommended presentation flow:

1. Dashboard list API queries DynamoDB for compact run metadata.
2. Run detail API reads the DynamoDB item.
3. Run detail API loads `manifest.json` from S3.
4. Run detail API loads selected artifacts from S3 as needed.
5. Backend returns a UI-safe response to the browser.

This keeps AWS credentials, bucket names, and raw artifacts behind the backend service boundary.

## Persistence Implementation Plan

Phase 1: Local file artifact store.

- Write files under a local path that mirrors S3 keys.
- Produce `manifest.json`.
- Keep DynamoDB writes disabled by default.

Phase 2: S3 artifact writes.

- Add an S3 artifact store adapter.
- Write raw request, raw provider payloads, normalized sources, full response, draft, fact-check, editor decision, events, and manifest.
- Retry transient S3 failures.

Phase 3: DynamoDB metadata and index writes.

- Upsert compact run ledger items.
- Store S3 pointer fields.
- Keep large payloads out of DynamoDB.

Phase 4: Presentation API.

- Dashboard list reads DynamoDB metadata.
- Run detail reads DynamoDB plus S3 manifest/artifacts.
- Browser receives backend-mediated summaries and selected artifact content.

