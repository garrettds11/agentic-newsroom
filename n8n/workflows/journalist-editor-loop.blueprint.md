# Journalist-Editor Loop Blueprint

## Goal

Coordinate a local-first Journalist-Editor workflow from topic intake through draft creation, fact checking, editorial decision, notification, and approved metadata storage.

## Workflow Stages

1. **Manual Trigger or Webhook Trigger**
   - Manual trigger supports local operator testing inside n8n.
   - Webhook trigger accepts topic payloads from PyGPT or another cockpit.

2. **Validate Topic Input**
   - Require `topic`.
   - Reject blank or very short topics.
   - Pass optional `audience` and `angle` through when supplied.

3. **Create Run Record**
   - Placeholder design: call the Python Agent Runner `POST /runs`.
   - Future AWS design: create a DynamoDB run record before enqueueing work.

4. **Enqueue Or Execute Job**
   - Current local blueprint calls the Python Agent Runner directly.
   - Future cloud blueprint can enqueue to SQS and have the Python runner consume jobs.

5. **Wait For Decision**
   - Current placeholder receives the decision in the immediate runner response.
   - Future async mode can poll DynamoDB or wait for an n8n callback webhook.

6. **Notify PyGPT/User**
   - Placeholder HTTP Request node posts to `https://example.invalid/pygpt-webhook`.
   - Replace with a real local PyGPT webhook, desktop notification bridge, or review queue endpoint later.

7. **Store Approved Content Metadata**
   - Placeholder node shapes metadata for approved stories.
   - Future AWS node can write metadata to DynamoDB and artifact pointers to S3.

## Expected Input

```json
{
  "topic": "Required newsroom assignment topic",
  "audience": "Optional audience",
  "angle": "Optional reporting angle"
}
```

## Python Runner Request

```json
{
  "topic": "={{ $json.topic }}",
  "audience": "={{ $json.audience }}",
  "angle": "={{ $json.angle }}"
}
```

## Python Runner Response

The current FastAPI runner returns:

```json
{
  "run_id": "run_example",
  "status": "completed",
  "story": {
    "run_id": "run_example",
    "status": "completed",
    "topic": "Example topic",
    "draft": {},
    "sources": [],
    "fact_check": {},
    "editor_decision": {}
  }
}
```

## Placeholder URLs

- Python Agent Runner in Docker: `http://python-agent-runner:8000/runs`
- Python Agent Runner on host: `http://localhost:8000/runs`
- PyGPT/user notification placeholder: `https://example.invalid/pygpt-webhook`

## Import Notes

Import [journalist-editor-loop.placeholder.json](journalist-editor-loop.placeholder.json) into n8n. Before activation:

- Confirm the Python Agent Runner URL.
- Replace notification placeholder URL.
- Replace any future AWS placeholder node with reviewed credentials.
- Keep production publication or archive steps disabled until approved.

