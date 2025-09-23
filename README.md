# Corner-Pocket Backend

FastAPI + Postgres service for Corner-Pocket. Develop on Linux; deploy anywhere.

## Quickstart

```bash
cp .env.example .env
docker compose up -d db
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

Open http://localhost:8000/docs
