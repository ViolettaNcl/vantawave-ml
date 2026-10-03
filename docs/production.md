# Production Engineering

## Configuration

VantaWave reads configuration from environment variables.

Key settings:

- `VANTAWAVE_ENV`
- `VANTAWAVE_HOST`
- `VANTAWAVE_PORT`
- `VANTAWAVE_LOG_LEVEL`
- `VANTAWAVE_LOG_FORMAT`
- `VANTAWAVE_DATABASE_URL`
- `VANTAWAVE_KNOWLEDGE_PATHS`
- `VANTAWAVE_READINESS_REQUIRES_DATABASE`

See `.env.example`.

Secrets must not be committed.

## Logging

Production logging defaults to newline-delimited JSON.

Standard context fields include:

- timestamp;
- level;
- logger;
- component;
- incident ID;
- experiment ID;
- session ID;
- model version.

## Health and readiness

`GET /health` indicates that the process is running.

`GET /ready` checks application dependencies and optionally the database.

In Docker Compose:

`VANTAWAVE_READINESS_REQUIRES_DATABASE=true`

so the API does not report ready until PostgreSQL is reachable.

## Docker

Build:

```powershell
docker build -t vantawave-ml .
```

Run the full stack:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

The Compose stack contains:

- `api`;
- `postgres`.

Alembic migrations are applied before API startup.

## Non-root container

The runtime image runs as the `vantawave` system user.

## Security CI

The repository contains a separate security workflow with:

- `pip-audit`;
- Bandit;
- production Docker image build.

It runs on pull requests, manually, and on a weekly schedule.
