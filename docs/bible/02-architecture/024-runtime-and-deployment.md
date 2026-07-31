---
id: JM-BIBLE-024
title: Runtime and Deployment
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on: []
related_documents:
  - JM-BIBLE-020
  - JM-BIBLE-A03
implementation_status: current
---

# Runtime and Deployment

Authoritative step-by-step commands live in `docs/development.md` and the
root `README.md`; this document records the *shape* of runtime and
deployment for the Bible's architectural picture.

## Local non-Docker development

- **Backend:** Python 3.11 virtualenv, `pip install -r
  backend/requirements.txt` (CadQuery installs from prebuilt wheels — no
  conda/micromamba required), `uvicorn jewelmind.api.app:app`.
- **Frontend:** Node.js 24 (also runs on Node 20+), `npm ci`, `npm run
  dev` (Vite dev server).
- Both can be started via `scripts/dev-backend.*` / `scripts/dev-frontend.*`.

## Docker Compose

- `docker-compose.yml` builds and runs both services with a health check
  on the backend.
- Backend image: `python:3.11-slim` + the OpenCascade/VTK shared
  libraries CadQuery needs (`backend/Dockerfile`).
- Frontend image: `node:24-slim`, runs the Vite dev server (not a
  production nginx build — see
  [`026-known-technical-limitations.md`](026-known-technical-limitations.md)).
- `vite.config.ts` explicitly allow-lists the sibling `shared/` directory
  for Vite's dev-server filesystem access (`server.fs.allow`), since
  inside the container there is no `.git` for Vite to auto-detect a wider
  workspace root.

## Ports

| Service | Port |
|---|---|
| Frontend | 3000 |
| Backend | 8000 |
| Backend API docs (`/docs`) | 8000 |
| Backend health check (`/api/health`) | 8000 |

## Environment variables

| Variable | Consumed by | Purpose | Default |
|---|---|---|---|
| `JEWELMIND_CORS_ORIGINS` | Backend | Comma-separated allowed browser origins. | `http://localhost:3000,http://localhost:5173` |
| `VITE_API_BASE_URL` | Frontend | Base URL the browser uses to reach the backend. | `http://localhost:8000` |

Both are overridable via a `.env` file (Docker Compose reads it
automatically); `.env.example` documents both and remains committed,
while `.env` itself stays gitignored. No secret or API key is required or
invented anywhere in this configuration.

## GitHub Actions (CI)

`.github/workflows/ci.yml` runs on every push and pull request targeting
`main`:

1. **`backend`** — Python 3.11, installs OpenCascade/VTK runtime
   libraries, `pip install -r requirements.txt`, `ruff check .`,
   `pytest -q`.
2. **`frontend`** — Node 24, `npm ci`, `npm run lint`, `npm run test`,
   `npx tsc -b`, `npx vite build`.
3. **`docker-smoke-test`** — runs only if both jobs above succeed;
   `docker compose up -d --build`, polls `/api/health`, verifies
   `/api/health`, `/docs`, and the frontend root, prints logs on failure,
   always runs `docker compose down -v`.

There is no deployment step beyond this — JewelMind has no hosted
environment in this milestone. See
[`026-known-technical-limitations.md`](026-known-technical-limitations.md).
