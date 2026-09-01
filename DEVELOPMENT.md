# OpenRD Development Guide

The frontend and backend are initialized applications; they are no longer placeholders.

## Current stack

- Frontend: Vue 3, Vite, TypeScript, Vue Router, Pinia, Axios, Reka UI and MSW.
- Backend: Python 3.12, FastAPI, SQLAlchemy/asyncpg, PostgreSQL, Alembic, Redis, JWT and bcrypt.
- Quality tools: `vue-tsc`, ESLint, Oxlint, pytest and Ruff.

## Prerequisites

- Node.js `^20.19.0` or `>=22.12.0`
- Python 3.12+
- uv, PostgreSQL and Redis

## Backend setup

```bash
cd backend
cp .env.example .env
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Set a reachable `DATABASE_URL`, `REDIS_URL`, and a non-default `JWT_SECRET_KEY` first. Swagger is available at `http://127.0.0.1:8000/docs`; health is `GET /api/v1/health`.

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Vite runs on `127.0.0.1:5173` and proxies `/api/v1` to `127.0.0.1:8000`.

MSW is enabled by default in development. Create `frontend/.env.local` for real-backend testing:

```dotenv
VITE_ENABLE_MOCK=false
```

## Checks

```bash
# frontend
npm run type-check
npm run lint
npm run build

# backend
uv run ruff check .
uv run pytest
```

Backend tests currently cover health and authentication basics. The frontend does not yet define a unit/component/E2E test command. Core demand, task, team, permission and admin flows still need integration coverage.

## API contract workflow

FastAPI routes are mounted under `/api/v1`. For cross-end changes:

1. Update the backend schema and route.
2. Update the frontend type and API wrapper.
3. Update MSW to match the same shape.
4. Add backend integration coverage.
5. Verify with `VITE_ENABLE_MOCK=false`.

Known contract gaps remain in admin demand management, user permissions, some team queries, and the “my tasks” path. Do not treat Mock behavior as production integration proof.

## Production readiness

Before public launch, add reproducible deployment, CI/CD gates, environment-specific CORS and secret management, private attachment storage, monitoring and alerts, database backup/restore, and security/privacy/UAT validation.

Historical root files such as `progress.md`, `findings.md` and `task_plan.md` describe earlier stages and are not current setup instructions.
