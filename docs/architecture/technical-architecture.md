# Technical Architecture

Agentic Newsroom is designed as a hybrid local-first system with clear boundaries between cockpit, orchestration, agent runtime, external providers, and persistence.

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
- Placeholder search adapters.

The runner should default to dry-run local mode.

### External Search APIs

Search should be adapter-based. Supported targets may include Tavily, Firecrawl, Serper, Google Search Grounding, or local placeholder adapters.

Adapters must return normalized source records with:

- URL or source identifier.
- Retrieval timestamp.
- Title or label.
- Extracted text or summary.
- Provider metadata.

### AWS Persistence

AWS is optional and should be disabled by default.

- **DynamoDB:** run state, job metadata, story metadata, validation results.
- **S3:** raw source captures, drafts, edited artifacts, fact-check logs, workflow logs.
- **SQS:** queued research or editorial jobs.

Terraform should define resources without hard-coded account IDs, API keys, private credentials, or region-specific ARNs.

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
8. The runner writes local artifacts by default.
9. When enabled, AWS adapters persist metadata to DynamoDB, objects to S3, and queued jobs to SQS.
10. n8n notifies PyGPT or the human operator for review.

See [technical-view.mmd](diagrams/technical-view.mmd) for the detailed architecture diagram.
