# PyGPT Webhook Trigger Example

This page documents how PyGPT can submit a topic to the local n8n workflow.

## Endpoint

When n8n is running locally through Docker Compose:

```text
POST http://localhost:5678/webhook/newsroom-topic
```

## Request Body

```json
{
  "topic": "Investigate how local school boards are adopting AI policies",
  "audience": "general readers",
  "angle": "public accountability and implementation gaps"
}
```

Only `topic` is required. `audience` and `angle` are optional.

## PowerShell Test

```powershell
$body = @{
  topic = "Investigate how local school boards are adopting AI policies"
  audience = "general readers"
  angle = "public accountability and implementation gaps"
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:5678/webhook/newsroom-topic" `
  -ContentType "application/json" `
  -Body $body
```

## PyGPT Usage Pattern

In PyGPT, create a local action, plugin, or prompt shortcut that sends the same JSON payload to the n8n webhook.

Suggested operator prompt:

```text
Prepare this topic for the Agentic Newsroom webhook. Return JSON with topic, audience, and angle. Do not invent facts or sources.
```

Then review the JSON before submitting.

## Expected Response

The placeholder n8n workflow returns an accepted response when the topic is valid:

```json
{
  "accepted": true,
  "run_id": "run_example",
  "status": "completed",
  "message": "Run completed and notification placeholder executed."
}
```

Invalid topics should return:

```json
{
  "accepted": false,
  "error": "A topic of at least 3 characters is required."
}
```

## Notes

- Do not send secrets in webhook payloads.
- Do not use PyGPT as the authoritative run-state database.
- Do not treat webhook success as publication approval.
- Keep production webhooks and local development webhooks separate.

