# Slice 004: Python Agent Runner

## Goal

Create the Python runtime skeleton for agent execution, validation, retries, and persistence adapters.

## Scope

- Add `src` package structure.
- Add Journalist Agent and Editor Agent interfaces.
- Add deterministic fact-checker module.
- Add schema models for assignment, source, draft, claim, fact-check report, and run state.
- Add retry handling primitives.
- Add placeholder search adapters.
- Add dry-run AWS adapter interfaces for S3, DynamoDB, and SQS.
- Add CLI entry point for local execution.
- Add focused unit tests.

## Acceptance Criteria

- Runner can execute a local dry-run job without external credentials.
- Placeholder search adapter returns normalized source records.
- Fact checker can pass and fail sample drafts deterministically.
- Schema validation rejects incomplete artifacts.
- Retry state is recorded in local output.
- AWS adapters do not write to AWS unless explicitly configured.

## Verification Commands

```powershell
python -m compileall src tests
```

```powershell
pytest
```

```powershell
python -m agentic_newsroom.runner --dry-run --topic "Test assignment"
```
