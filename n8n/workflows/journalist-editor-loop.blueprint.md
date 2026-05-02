# Research Request Workflow Blueprint

## Goal

Accept structured research requests from PyGPT, n8n manual tests, or future client apps, then forward them to the Python Agent Runner `POST /research` endpoint.

`POST /runs` remains available in the Python service for backward compatibility, but this n8n blueprint uses `/research` as the primary service contract.

## Workflow Stages

1. **Manual Trigger or Webhook Trigger**
   - Manual trigger supports local operator testing through an editable placeholder payload node.
   - Webhook trigger accepts structured research JSON from PyGPT or another client.

2. **Normalize Research Request**
   - Requires `topic`.
   - Preserves optional request fields:
     - `audience`
     - `angle`
     - `source_provider`
     - `source_ids`
     - `max_sources`
     - `tags`
     - `category`
     - `sort`
     - `output_format`
     - `page_size`
     - `cursor`
   - Leaves `max_sources` omitted when the caller omits it, so the Python service applies `NEWSROOM_DEFAULT_MAX_SOURCES`.

3. **Forward To Python Research Service**
   - Calls `http://python-agent-runner:8000/research`.
   - Forwards `X-Newsroom-Api-Key` from incoming webhook headers when present.
   - Does not store or hard-code real secrets.

4. **Return Response**
   - Returns the Python `/research` response directly to the webhook caller.

## Webhook Path

```text
/webhook/newsroom-research
```

## Example Request

```json
{
  "topic": "latest ZDI advisories",
  "audience": "security researchers",
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

n8n does not enforce API-key auth in this placeholder workflow. If the Python runner has `REQUIRE_AUTH=true`, clients can send:

```text
X-Newsroom-Api-Key: <key>
```

The workflow forwards that header to the Python runner. Do not store real keys in the workflow export.

## Placeholder URLs

- Python Agent Runner in Docker: `http://python-agent-runner:8000/research`
- Python Agent Runner on host: `http://localhost:8000/research`

The importable placeholder uses literal local URLs because recent n8n versions block `$env` access in node expressions by default.

## Import Notes

Import [journalist-editor-loop.placeholder.json](journalist-editor-loop.placeholder.json) into n8n. Before activation:

- Confirm the Python Agent Runner URL.
- Edit the manual placeholder payload when using the manual test path.
- Review auth behavior before exposing beyond localhost.
- Keep production publication or archive steps disabled until approved.
