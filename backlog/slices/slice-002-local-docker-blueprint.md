# Slice 002: Local Docker Blueprint

## Goal

Define a Docker Compose blueprint for local n8n, Postgres, Python Agent Runner, and optional Ollama.

## Scope

- Add `docker-compose.yml`.
- Add `.env.example` with placeholder-only values.
- Add Dockerfile or container notes for the Python Agent Runner.
- Configure n8n to use Postgres.
- Keep Ollama optional behind a Compose profile.
- Document local startup and shutdown commands.

## Acceptance Criteria

- `docker compose config` succeeds with placeholder environment values.
- n8n and Postgres services are declared without assuming n8n is installed on the host.
- Python Agent Runner service is declared.
- Ollama is optional and does not start by default.
- No real secrets are present.
- Local volumes are named clearly.

## Verification Commands

```powershell
docker compose config
```

```powershell
docker compose --profile local up --dry-run
```
