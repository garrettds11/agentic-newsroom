# Slice 006: PyGPT Integration

## Goal

Document and implement the PyGPT cockpit integration path for topic input, prompt testing, review, and notifications.

## Scope

- Add PyGPT operator guide.
- Define topic intake payloads.
- Define local webhook or file handoff options.
- Define review response payloads.
- Define notification expectations.
- Add example prompts for Journalist and Editor testing.
- Add troubleshooting notes for local-first operation.

## Acceptance Criteria

- Operator can submit a topic from PyGPT to the local workflow path.
- Payload schemas are documented.
- Review and revision loop is documented.
- No real credentials are required for dry-run mode.
- Prompt testing can be performed without cloud persistence.
- Notifications are documented as local placeholders until configured.

## Verification Commands

```powershell
Get-Content docs/pygpt/*.md
```

Future local webhook verification:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:5678/webhook/newsroom-topic -ContentType "application/json" -Body '{"topic":"Test assignment"}'
```
