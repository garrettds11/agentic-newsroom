# AGENTS.md

## Project

This repository implements Agentic Newsroom, a hybrid local-first Journalist-Editor agentic workflow.

The system uses:
- PyGPT as the local desktop cockpit.
- n8n as the workflow orchestrator.
- Python as the agent execution and validation runtime.
- External search APIs for web retrieval.
- AWS DynamoDB, S3, and SQS for cloud persistence and queueing.
- Terraform/OpenTofu for infrastructure blueprints.
- Docker Compose for local development services.

## Working Rules

- Do not create, store, or commit secrets.
- Do not hard-code AWS account IDs, access keys, secret keys, or private ARNs.
- Use `.env.example` for configuration examples.
- Prefer documentation-first changes before implementation.
- Prefer small, reviewable slices.
- Do not run `terraform apply`.
- Do not deploy infrastructure unless explicitly instructed.
- Do not assume n8n is installed outside Docker.
- Keep local execution and cloud persistence clearly separated.
- Keep non-technical and technical architecture views separate.

## Architecture Principles

- n8n orchestrates workflows.
- Python owns the agent loop and deterministic guardrails.
- DynamoDB stores job state, metadata, status, scores, and source URLs.
- S3 stores large artifacts, raw source text, drafts, final Markdown, and logs.
- SQS decouples orchestration from execution.
- PyGPT is a cockpit, not the production runtime.
- Ollama is optional local model infrastructure.

## Verification Expectations

When changing Python code:
- Run unit tests if present.
- Add tests for schema validation and fact-checking logic.

When changing Terraform:
- Run `terraform fmt`.
- Run `terraform validate` when Terraform is installed.
- Never run `terraform apply` without explicit instruction.

When changing Docker files:
- Prefer Docker Compose services with clear environment variables.
- Do not bake secrets into images.

When changing documentation:
- Keep diagrams and architecture descriptions aligned.
