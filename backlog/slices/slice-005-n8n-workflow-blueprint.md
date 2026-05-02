# Slice 005: n8n Workflow Blueprint

## Goal

Define the n8n workflow blueprint for topic intake, job orchestration, Python runner invocation, review loops, notifications, and optional persistence.

## Scope

- Add workflow export JSON under `workflows/n8n`.
- Add webhook intake design for PyGPT.
- Add nodes for validation, queueing, runner invocation, editor review, and notification.
- Add local-only placeholder credentials guidance.
- Add documentation for importing into n8n.
- Add failure and retry path documentation.

## Acceptance Criteria

- Workflow blueprint can be imported into n8n once n8n is available.
- Workflow does not contain real credentials.
- Workflow can run against local placeholder endpoints.
- Failure paths are visible and documented.
- Human review gate is represented before any publish or archive step.
- Optional AWS persistence is clearly separated from local dry-run flow.

## Verification Commands

```powershell
Get-ChildItem workflows/n8n -File
```

```powershell
Get-Content workflows/n8n/*.json
```

Manual verification after n8n exists:

```text
Import the workflow JSON into n8n and confirm all credentials are placeholders.
```
