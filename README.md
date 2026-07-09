# Lite Thinking 2026 — Technical Test

Full-stack application built with a clean-architecture domain layer shared by a
Django backend (issuer) and FastAPI services (validator), with a Next.js
frontend. See `openspec/changes/build-lite-thinking-app/` for the full design.

## Architecture

```
frontend (Next.js) ─▶ backend (Django) ─▶ domain ◀─ services (FastAPI)
                                            ▲
             domain imports nothing (no Django, no SQLAlchemy, no HTTP)
```

| Box         | Responsibility                                                        |
|-------------|-----------------------------------------------------------------------|
| `domain/`   | Pure-Python entities + business rules (Poetry package)                |
| `backend/`  | Django: CRUD, auth (issues JWT), roles, persistence, event publisher  |
| `services/` | FastAPI: PDF+email, AI agent (RAG over products, pgvector) — validates |
| `frontend/` | Next.js, Atomic Design, one client that sends the same Bearer to both |

## Quick start

```bash
cp .env.example .env      # fill in API keys
docker compose up --build
```

- Backend (Django): http://localhost:8000
- AI service (FastAPI): http://localhost:8001
- Frontend (Next.js): http://localhost:3000

## Repository layout

- `domain/` — shared domain package, managed with Poetry
- `backend/` — Django project (application + infrastructure layer)
- `services/` — FastAPI app (documents + ai_agent routers)
- `frontend/` — Next.js app
- `infra/` — Docker init scripts


Usuarios:

admin@acme.com - Admin12345
externo@demo.com - supersecre1