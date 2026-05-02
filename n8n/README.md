# n8n Workflow Blueprints

This directory contains importable n8n workflow blueprints for Agentic Newsroom.

The first workflow is the Journalist-Editor loop:

- [Workflow design](workflows/journalist-editor-loop.blueprint.md)
- [Placeholder n8n export](workflows/journalist-editor-loop.placeholder.json)

## Safety

- No real credentials are included.
- URLs use placeholders or local development defaults.
- Credential names are placeholders only.
- Do not connect production webhooks, AWS resources, or notification targets until reviewed.

## Import

Once n8n is running, import the placeholder export:

1. Open n8n at `http://localhost:5678`.
2. Select **Workflows**.
3. Choose **Import from File**.
4. Select `n8n/workflows/journalist-editor-loop.placeholder.json`.
5. Review every placeholder URL and disabled production step before activating.

## Local Development Defaults

The placeholder workflow expects the Python Agent Runner to be reachable from n8n at:

```text
http://python-agent-runner:8000/runs
```

The local dry-run notification placeholder is:

```text
http://python-agent-runner:8000/notifications/placeholder
```

When running n8n outside Docker, use:

```text
http://localhost:8000/runs
```

## Webhook

The placeholder webhook path is:

```text
/webhook/newsroom-topic
```

Example payload:

```json
{
  "topic": "Local election reporting workflow",
  "audience": "general readers",
  "angle": "public accountability"
}
```
