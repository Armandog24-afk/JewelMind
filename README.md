# JewelMind

JewelMind is a parametric jewelry CAD application. It lets you configure a
solitaire ring and generate a real parametric 3D model, an interactive
browser preview, a real STEP file, a real STL file, a JSON project
definition, a readable technical specification, and deterministic
validation results — all without Rhino, MatrixGold, JewelCAD, an
interactive FreeCAD session, any other commercial CAD software, paid APIs,
or an LLM at runtime.

> **JewelMind generates preliminary parametric CAD models. Dimensions,
> tolerances, stone settings and manufacturing suitability must be
> reviewed by a qualified jewelry professional before production.**

## 1. Product description

Configure a solitaire ring's ring size, band, stone, prong setting,
material, and manufacturing method in a desktop-first web UI. Every
parameter change updates a canonical JSON project definition immediately.
Pressing **Generate** sends that definition to a Python/FastAPI backend,
which deterministically builds real CadQuery/OpenCascade geometry, tessellates
it for preview, and returns model metadata plus per-component preview
meshes that the frontend renders in an interactive React Three Fiber
viewport. STEP, STL, JSON, and a Markdown technical specification are all
real, downloadable, backend-generated files.

## 2. Current milestone

**Milestone 1: solitaire ring.** Round stone, 4- or 6-prong setting, flat or
comfort-fit band, five metal choices (cosmetic), two manufacturing methods.
See `docs/known-limitations.md` for exactly what is and isn't implemented.

## 3. What works

- Every parameter in the domain model is editable and validated live.
- The JSON tab reflects the current definition immediately.
- Backend-authoritative validation (16 rules across ring/band/stone/prong/
  setting/manufacturing/geometry — see `docs/validation-rules.md`) blocks
  generation and export on errors; warnings never block anything.
- Real parametric geometry: a genuinely different solid for flat vs.
  comfort-fit bands, and for 4 vs. 6 prongs, deterministically derived from
  the input (same input → same `definitionHash` → same geometry).
- Stone reference geometry stays fully separate from metal geometry.
- Backend-generated STL preview meshes (one per component: band,
  stone_reference, prongs, basket_support) rendered live in an orbit-
  controllable 3D viewport with grid/axes toggles and per-component
  visibility checkboxes.
- Real STEP export (CadQuery/OpenCascade), real STL export (configurable
  mesh tolerance), JSON export, and a Markdown technical specification —
  all downloadable from the browser.
- Stale-state handling: changing a parameter after generating marks the
  model stale and disables export until you regenerate; a failed
  regeneration keeps the last successful preview visible instead of
  blanking the viewport, and a failed preview-mesh reload never disposes
  or blanks an already-visible model.
- Hardened backend data safety: numeric fields reject strings, `NaN`, and
  `Infinity`; `schemaVersion` is locked to the currently supported version;
  `/api/health` returns HTTP 503 (not a false "healthy") when CadQuery
  fails to load; every export uses a unique temp file and is cleaned up
  after both success and failure. See `AUDIT_FIXES.md` for the full list.
- 139 backend tests (pytest) and 41 frontend tests (vitest) passing; see
  §10 below for exact commands. A GitHub Actions workflow
  (`.github/workflows/ci.yml`) runs all of this on every push/PR to `main`.

## 4. What does not work

See `docs/known-limitations.md` for the full list. Highlights: no GLB
preview packaging (STL-per-component + manifest instead, by explicit design
choice), no gemological stone accuracy, no manufacturing tolerancing beyond
the documented validation thresholds, in-memory model cache only (no
database), and the Docker build has been written and reviewed but not
executed end-to-end (Docker was unavailable in the build environment — see
§12 Troubleshooting).

## 5. Architecture

```
jewelmind/
  frontend/   React + TypeScript (strict) + Vite + React Three Fiber
  backend/    Python 3.11 + FastAPI + Pydantic v2 + CadQuery
  shared/     TypeScript domain types & validation mirror
  docs/       Architecture, geometry conventions, domain model, validation
              rules, API reference, development guide, known limitations
  examples/   Sample JewelryDefinition JSON files + a headless generator script
  scripts/    Dev convenience scripts
```

One frontend, one backend — no microservices. Full write-up:
`docs/architecture.md`. Coordinate system: `docs/geometry-conventions.md`.

## 6. Requirements

- Python 3.11
- Node.js 24 (also runs fine on Node 20+; CI and Docker both pin Node 24)
- Docker + Docker Compose (optional; see §8/§12)

CadQuery installs via plain `pip install cadquery` — its OpenCascade
bindings ship as prebuilt wheels, no conda/micromamba required (verified
directly; see `docs/development.md`).

## 7. Docker installation

```bash
docker compose up --build
```

Builds and starts both services. See §9 for URLs and §12 if the build
fails (Docker was not available in the environment this project was built
in, so this has not been executed end-to-end — see
`docs/known-limitations.md`).

## 8. Startup command

**Docker:**

```bash
docker compose up --build
```

**Without Docker** (verified working during development):

```bash
# Terminal 1 — backend
cd backend
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt   # .venv/bin/pip on macOS/Linux
.venv/Scripts/python -m uvicorn jewelmind.api.app:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — frontend
cd frontend
npm install
npm run dev
```

Or use `scripts/dev-backend.ps1` / `.sh` and `scripts/dev-frontend.ps1` /
`.sh`. Full details: `docs/development.md`.

## 9. Local URLs

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend | http://localhost:8000 |
| API docs (Swagger) | http://localhost:8000/docs |
| Health check | http://localhost:8000/api/health |

## 10. Test commands

```bash
# Backend (139 tests)
cd backend && .venv/Scripts/python -m pytest -q   # .venv/bin/python on macOS/Linux

# Frontend (41 tests)
cd frontend && npm run test

# Type-check + build the frontend
cd frontend && npx tsc -b && npm run build

# Lint
cd backend && .venv/Scripts/python -m ruff check .
cd frontend && npm run lint
```

## 11. Export workflow

1. Configure the ring in the left panel. The JSON and Validation tabs
   update immediately.
2. Fix any **error**-severity validation results (shown in the Validation
   tab) — warnings and information results don't block anything.
3. Click **Generate model**. The center viewport shows the real
   backend-generated geometry.
4. Export buttons (STEP / STL / JSON) are enabled once generation succeeds
   and stay enabled until you change a parameter (which marks the model
   "stale" and disables export again until you regenerate).
5. Click **Export STEP**, **Export STL**, or **Export JSON** to download
   the real file. Use the **Specification** tab to read (or the
   `POST /api/models/specification` endpoint to download) the technical
   specification Markdown.

## 12. Troubleshooting

- **`cadquery` fails to import / install:** confirm you're on Python 3.11
  and a clean virtualenv; `pip install cadquery` should pull prebuilt
  `cadquery-ocp` wheels with no compilation. See `docs/development.md`.
- **Backend health check shows `cadEngineReady: false`:** CadQuery failed
  to import in that process; check the backend's startup logs for the
  actual import error.
- **Frontend shows "Backend unreachable":** confirm the backend is running
  and that `VITE_API_BASE_URL` (default `http://localhost:8000`) matches
  where it's actually listening; check CORS via
  `JEWELMIND_CORS_ORIGINS` if the frontend runs on a non-default port.
- **Docker build fails on the backend image:** the most likely cause is a
  missing system library for OpenCascade/VTK; see the apt package list in
  `backend/Dockerfile` and `docs/known-limitations.md`.
- **Port 3000 or 8000 already in use:** override via `docker-compose.yml`
  port mappings, or run the dev servers with a different port and update
  `VITE_API_BASE_URL` / `JEWELMIND_CORS_ORIGINS` to match.
- **Windows: `python` prints a Microsoft Store message instead of running.**
  This is the Windows "app execution alias" stub, not a real Python
  install. Install Python 3.11 from python.org (per-user install, no admin
  needed: run the official installer with `InstallAllUsers=0`) and use its
  full path, or disable the alias under Settings → Apps → Advanced app
  settings → App execution aliases.

## 13. Professional review disclaimer

**JewelMind generates preliminary parametric CAD models. Dimensions,
tolerances, stone settings and manufacturing suitability must be reviewed
by a qualified jewelry professional before production.** This applies to
every exported STEP/STL file, every technical specification, and the
application as a whole. See `docs/known-limitations.md` for specifics.

---

Further reading: `docs/architecture.md`, `docs/geometry-conventions.md`,
`docs/domain-model.md`, `docs/validation-rules.md`, `docs/api.md`,
`docs/development.md`, `docs/known-limitations.md`, `CLAUDE.md`.

**Author:** Armando Gervasi
