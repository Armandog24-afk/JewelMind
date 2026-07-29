# Development guide

## Requirements

- Python 3.11
- Node.js 20+ (Node 24 also verified working)
- Docker + Docker Compose (optional — see "Non-Docker workflow" below)

CadQuery is installed via plain `pip install cadquery`. Its OpenCascade
bindings (`cadquery-ocp`) ship as prebuilt wheels for Windows, Linux, and
macOS on recent Python versions, so **no conda/micromamba is required** —
this was verified directly in this project's development environment.

## Non-Docker workflow

This is how the project was actually built and tested in this milestone
(no Docker was available in the development environment).

### Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m uvicorn jewelmind.api.app:app --reload --host 0.0.0.0 --port 8000
# macOS/Linux:
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m uvicorn jewelmind.api.app:app --reload --host 0.0.0.0 --port 8000
```

Or use the provided scripts: `scripts/dev-backend.ps1` (Windows) /
`scripts/dev-backend.sh` (macOS/Linux) — both create the virtualenv on
first run automatically.

Backend tests and linting:

```bash
cd backend
.venv/Scripts/python -m pytest -q         # Windows
.venv/bin/python -m pytest -q             # macOS/Linux
.venv/Scripts/python -m ruff check .      # or .venv/bin/python -m ruff check .
```

### Frontend

```bash
cd frontend
npm install
npm run dev       # http://localhost:3000
npm run build     # tsc -b && vite build
npm run test      # vitest run
npm run lint      # oxlint
```

Or `scripts/dev-frontend.ps1` / `scripts/dev-frontend.sh`.

The frontend reads the backend's base URL from `VITE_API_BASE_URL`
(defaults to `http://localhost:8000` if unset — see
`frontend/src/api/client.ts`).

### Both at once

```bash
make backend-install frontend-install   # first time only
make backend-run     # in one terminal
make frontend-dev    # in another terminal
```

(`make` targets shell out to the same commands above; see the root
`Makefile`.)

## Docker workflow

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API docs: http://localhost:8000/docs

The backend image is a plain `python:3.11-slim` base with `pip install -r
requirements.txt` plus the handful of shared libraries OpenCascade/VTK need
(`libgl1`, `libglu1-mesa`, `libxrender1`, `libxext6`, `libsm6`, `libgomp1`).
See `backend/Dockerfile` for the exact list and
`docs/known-limitations.md` for what has/hasn't been verified about this
image (Docker itself was not available in the environment this project was
built in, so the Docker build has not been executed end-to-end — only
reviewed against the locally-verified pip install).

The frontend image runs the Vite dev server (not a production nginx build)
— see `docs/known-limitations.md`.

## Generating a model without the API

```bash
python scripts/generate_example.py examples/solitaire-default.json examples/output
```

Writes `model.step`, `model.stl`, and `specification.md` directly from the
`jewelmind` package, bypassing FastAPI entirely — useful for a quick
sanity check of the geometry pipeline.

## Project conventions

- Millimeters everywhere — see `docs/geometry-conventions.md`.
- Domain logic (`validation/`, `geometry/`) has no framework imports; keep
  it that way.
- Every new validation rule needs a rule-ID constant, an entry in both the
  backend and frontend engines, a test, and a docs update — see
  `docs/validation-rules.md`.
- Run backend and frontend tests before considering a change complete.
