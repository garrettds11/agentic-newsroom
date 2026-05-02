# n8n Workflow Blueprints

This directory contains importable n8n workflow blueprints for Agentic Newsroom.

The first workflow is the research request loop:

- [Workflow design](workflows/journalist-editor-loop.blueprint.md)
- [Placeholder n8n export](workflows/journalist-editor-loop.placeholder.json)

## Safety

- No real credentials are included.
- URLs use local development defaults.
- Credential names are placeholders only.
- Do not connect production webhooks, AWS resources, or notification targets until reviewed.

## Import

Once n8n is running, import the placeholder export:

1. Open n8n at `http://localhost:5678`.
2. Select **Workflows**.
3. Choose **Import from File**.
4. Select `n8n/workflows/journalist-editor-loop.placeholder.json`.
5. Review every placeholder URL before activating.

## Local Development Defaults

The placeholder workflow expects the Python Agent Runner to be reachable from n8n at:

```text
http://python-agent-runner:8000/research
```

When running n8n outside Docker, use:

```text
http://localhost:8000/research
```

## Webhook

The placeholder webhook path is:

```text
/webhook/newsroom-research
```

Example payload:

```json
{
  "topic": "latest ZDI advisories",
  "audience": "general readers",
  "angle": "newly published advisories",
  "source_provider": "rss",
  "source_ids": ["zdi_published_2026"],
  "max_sources": 100,
  "tags": ["vulnerabilities", "advisories", "zdi"],
  "category": "cybersecurity",
  "sort": "published_desc",
  "output_format": "brief",
  "page_size": 50,
  "cursor": null
}
```

## Auth

This placeholder workflow does not enforce auth in n8n. If the Python runner has `REQUIRE_AUTH=true`, clients can send `X-Newsroom-Api-Key`; n8n forwards that header to `/research`.

Use placeholders only and keep real keys outside source control.
