# Slice 001: Repository Foundation

## Goal

Create the initial documentation-first repository scaffold for the local-first Journalist-Editor newsroom.

## Scope

- Top-level project README cleanup.
- `AGENTS.md` operating guidance.
- `IMPLEMENT.md` staged implementation guide.
- Architecture docs and diagrams.
- Agent persona docs.
- Guardrail docs.
- Backlog slice structure.

## Acceptance Criteria

- Required control-pack files exist.
- README explains the project without requiring local services.
- Security baseline is documented.
- Diagrams are Mermaid source files.
- Backlog contains six implementation slices.
- No real secrets, account IDs, API keys, private credentials, or region-specific ARNs are committed.

## Verification Commands

```powershell
git status --short
```

```powershell
Get-ChildItem docs,backlog -Recurse -File | Select-Object FullName
```
