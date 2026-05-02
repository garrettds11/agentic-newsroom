# IMPLEMENT.md

This file defines the staged implementation path for the Agentic Newsroom control pack.

## Target System

The repository should grow into a hybrid local-first system with:

- PyGPT as the desktop cockpit for topic entry, prompt testing, review, and notifications.
- n8n as the workflow orchestrator, eventually running under Docker Compose.
- A Python Agent Runner that owns agent execution, deterministic fact checking, schema validation, retries, and AWS persistence adapters.
- Optional external search integrations through swappable adapters.
- Optional AWS persistence through DynamoDB, S3, and SQS.
- Optional Ollama for local model experimentation.

## Delivery Order

1. Repository foundation and control docs.
2. Local Docker blueprint for n8n, Postgres, Python Agent Runner, and optional Ollama.
3. AWS IaC blueprint for DynamoDB, S3, and SQS.
4. Python Agent Runner skeleton.
5. n8n workflow blueprint.
6. PyGPT integration guide and operator workflow.

## Security Baseline

- No real secrets in source control.
- Use `.env.example` only for placeholder names.
- Use least-privilege IAM examples when IaC is added.
- Keep AWS region, account, and resource naming configurable.
- Keep local dry-run mode as the default.
- Do not run `terraform apply` as part of automated verification.

## Verification Baseline

Use these commands as the repo grows:

```powershell
git status --short
```

```powershell
terraform fmt -check -recursive infra/terraform
```

```powershell
terraform validate
```

```powershell
python -m compileall src tests
```

```powershell
pytest
```

Commands that depend on future files are listed in the relevant backlog slices.
