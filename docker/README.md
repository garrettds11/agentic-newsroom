# Local Docker Blueprint

This Compose blueprint runs Agentic Newsroom local development services without requiring n8n to be installed on the host.

## Services

- `n8n`: workflow orchestrator, exposed on `127.0.0.1:5678` by default.
- `postgres`: n8n database, stored in a named Docker volume.
- `python-agent-runner`: FastAPI runner, exposed on `127.0.0.1:8000` by default.
- `ollama`: optional local model service, enabled only with the `ollama` profile.
- `searxng`: optional self-hosted metasearch service, enabled with the `searxng` or `search` profile.

## Configuration

Use placeholder values only:

```powershell
Copy-Item docker/.env.example .env
```

Review `.env` before starting services. Do not place real production secrets in it.

You can also avoid creating a root `.env` and pass the example file directly:

```powershell
docker compose --env-file docker/.env.example config
```

## Start

Start n8n, Postgres, and the Python runner:

```powershell
docker compose --env-file docker/.env.example up --build
```

Start in the background:

```powershell
docker compose --env-file docker/.env.example up --build -d
```

Start with optional Ollama:

```powershell
docker compose --env-file docker/.env.example --profile ollama up --build
```

Start with optional SearXNG:

```powershell
docker compose --env-file docker/.env.example --profile searxng up --build
```

Equivalent generic search profile:

```powershell
docker compose --env-file docker/.env.example --profile search up --build
```

Run the Python runner against SearXNG:

```text
SEARCH_PROVIDER=searxng
SEARXNG_BASE_URL=http://searxng:8080
```

Run the Python runner against RSS feeds:

```powershell
SEARCH_PROVIDER=rss
RSS_SOURCE_REGISTRY_PATH=config/sources/rss_sources.yml
RSS_SOURCE_IDS=zdi_published_2026
```

`RSS_FEED_URLS` remains available for quick experiments, but registry-based RSS sources are preferred.

Configure service-level result limits:

```text
NEWSROOM_DEFAULT_MAX_SOURCES=25
NEWSROOM_SYSTEM_MAX_SOURCES=250
```

Client apps can request larger result sets with `/research.max_sources` within the system safety cap. Future pagination placeholders are `page_size`, `cursor`, and `next_cursor`.

## URLs

- n8n: `http://localhost:5678`
- Python Agent Runner health: `http://localhost:8000/health`
- Ollama, when enabled: `http://localhost:11434`
- SearXNG, when enabled: `http://localhost:8080`
- Python Agent Runner research endpoint: `http://localhost:8000/research`

## Shutdown

Stop services and keep volumes:

```powershell
docker compose down
```

Stop services and remove local named volumes:

```powershell
docker compose down --volumes
```

Remove built images created for this stack:

```powershell
docker compose down --rmi local
```

## Notes

- n8n runs from the official container image.
- Postgres is available only inside the Compose network by default.
- n8n and the Python runner are bound to localhost.
- The Python runner defaults to dry-run mode and placeholder adapters.
- No AWS, paid search, model, or Ollama calls are required unless explicitly configured later.
- SearXNG is metasearch. RSS feeds are fetched directly by the Python RSS adapter.
- API-key auth is disabled by default for localhost and should be enabled before exposing the runner beyond localhost.
