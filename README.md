# Agentic Newsroom

Agentic Newsroom is a hybrid, local-first Journalist-Editor newsroom system for topic intake, research, drafting, review, fact checking, and durable archiving.

## Architecture Overview

- **PyGPT desktop cockpit:** topic input, prompt testing, human review, and notifications.
- **n8n workflow orchestrator:** local workflow coordination, eventually running in Docker.
- **Python agent runtime:** Journalist Agent, Editor Agent, deterministic fact checker, schema validation, retry handling, and AWS writes.
- **External search adapters:** Tavily, Firecrawl, Serper, Google Search Grounding, or placeholder adapters.
- **AWS persistence:** DynamoDB for run state and metadata, S3 for raw sources, drafts, artifacts, and logs, and SQS for queued jobs.

## Local-First Principles

- Keep development runnable without cloud writes by default.
- Use placeholder adapters until real provider credentials are intentionally configured.
- Never commit real secrets, account IDs, API keys, private credentials, or region-specific ARNs.
- Do not run `terraform apply` from this repository without explicit human approval.

## Planned Runtime Shape

Docker Compose should eventually support:

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

See [IMPLEMENT.md](IMPLEMENT.md) and the backlog slices in [backlog/slices](backlog/slices) for the staged implementation plan.
