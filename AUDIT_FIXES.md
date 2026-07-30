# Audit & hardening pass — summary

This document summarizes a security/reliability audit performed on the
existing JewelMind milestone-1 prototype. **No new jewelry features were
added.** Every change below either closes a real gap that testing exposed,
or preserves existing behavior while making it fail safely instead of
silently or destructively. See the linked tests for proof each fix works.

## 1. Backend data safety (Pydantic)

- `JewelryDefinition` and its nested models now set `strict=True` in
  addition to the existing `extra="forbid"` — a numeric field must receive
  a real JSON number, not a numeric-looking string (e.g. `"2.4"` for
  `band.width` is now rejected). Widening `int → float` (e.g. a JSON `16`
  for a `float` field) is still accepted, since that's lossless and is
  exactly what a JSON integer literal parses to.
- Every `float` field now sets `allow_inf_nan=False`. Without it,
  `gt=0`-style constraints are not enough on their own: `float('inf') > 0`
  is `True` in Python, so an infinite mesh tolerance or band width would
  otherwise sail straight through validation and into CadQuery, which
  cannot construct geometry from a non-finite dimension.
- `schemaVersion` changed from a plain `str` to `Literal["0.1.0"]` — an
  obsolete or future/unknown schema version is now rejected outright
  instead of being silently accepted and misinterpreted.
- The same `strict=True` + finite/positive constraints were applied to the
  `meshTolerance`/`angularTolerance` override fields on the STL export
  request (`api/schemas.py`), closing the same class of bug on that path.
- Fixed a real crash this hardening pass discovered: FastAPI's own
  validation-error handler was echoing the client's raw invalid input
  (e.g. a rejected `Infinity`) straight into the JSON error response —
  which itself is not valid JSON and crashed the error handler while it
  was trying to report the very error that caught the bad input. Both
  validation-error handlers now sanitize non-finite floats before
  building the response (`api/app.py::_json_safe`).
- Tests: `backend/tests/test_schema_safety.py` (70 cases), plus coverage
  in `backend/tests/test_api_hardening.py`.

## 2. Health endpoint

- `GET /api/health` now returns HTTP **503** (not 200) with
  `cadEngineReady: false` and a `cadEngineError` message when CadQuery's
  OpenCascade bindings failed to load — instead of always returning 200
  regardless of the actual state.
- The check goes beyond a bare `import cadquery`: it also constructs a
  trivial solid (`services/cad_engine.py`), which catches the case where
  the Python package imports fine but the native bindings fail to
  actually initialize (e.g. a missing shared library in a stripped
  container).
- The check runs once at process start and is cached — the CAD engine's
  availability cannot change during a running process, so re-probing on
  every health-check call would be pure wasted work.
- **Architectural fix, not just a health-endpoint tweak:** the geometry
  package imports CadQuery unconditionally at module scope, so anything
  that transitively imported it used to do so *eagerly*, at backend
  startup. If CadQuery were broken, the whole backend process would have
  crashed before it could serve even `/api/health`. `api/routes.py` now
  imports `model_service` **lazily**, on first use inside a request
  handler, wrapped so an import failure becomes a clean
  `503 CAD_ENGINE_UNAVAILABLE` response instead of a crashed process.
  `/api/models/validate` was also changed to call the validation engine
  directly rather than through `model_service`, since validation has no
  CadQuery dependency and must keep working even when the CAD engine is
  down.
- Tests: `test_health_reports_503_when_cad_engine_not_ready`,
  `test_probe_cad_engine_*`, `test_cad_engine_unavailable_returns_503` in
  `backend/tests/test_api_hardening.py`.

## 3. API error handling

- New documented error codes: `MODEL_GENERATION_FAILED` (500),
  `STEP_EXPORT_FAILED` (500), `STL_EXPORT_FAILED` (500),
  `CAD_ENGINE_UNAVAILABLE` (503) — each endpoint now catches unexpected
  exceptions and re-raises them as the specific documented `AppError`
  subclass, so a client can distinguish "your input was invalid" from
  "the CAD engine crashed" from "the CAD engine isn't available at all."
- Every error response still includes a `requestId` (unchanged) and never
  includes a raw Python traceback (verified by test, not just assumed).
- Temporary files: see §4.
- Tests: `test_generation_failure_maps_to_model_generation_failed`,
  `test_step_export_failure_maps_to_step_export_failed`,
  `test_stl_export_failure_maps_to_stl_export_failed` in
  `backend/tests/test_api_hardening.py`.

## 4. Export reliability

- **Real bug fixed:** STEP/STL exports used to write to a fixed
  `model.step` / `model.stl` path inside the model's shared preview
  directory. Two concurrent export requests for the same model (e.g. one
  with `includeStoneReference: true` and one without, from two browser
  tabs) could overwrite each other's output file mid-write. Every export
  now gets its own uniquely-named temp file (`tempfile.mkstemp`), so
  concurrent exports can never collide.
- The temp file is deleted via a `BackgroundTask` once the HTTP response
  has finished streaming (success path), or immediately in an `except`
  block if the export itself fails (failure path) — verified by a test
  that scans the OS temp directory before/after both a successful and a
  failing export and asserts nothing is left behind.
- The STL export's optional `meshTolerance`/`angularTolerance` overrides
  are now validated (finite, `> 0`) — see §1.
- `stone_reference` continues to be excluded from exports by default
  (unchanged; `includeStoneReference: true` still opts in).
- **Real bug fixed:** the technical specification's "Generated at"
  timestamp used to call `datetime.now()` every time the specification
  was rendered — so downloading the same specification twice a minute
  apart produced two different timestamps for the *same* model.
  `build_specification()` now takes the model's original generation
  timestamp as a parameter and always reports that value, proven by a
  test that downloads the same specification twice and asserts the
  timestamp is identical both times and matches the `generatedAt` field
  from the original `/api/models/generate` response.

## 5. Frontend localStorage safety

- **Real bug fixed:** the persisted project definition was loaded with
  `JSON.parse(raw) as JewelryDefinition` — a type *assertion*, not a
  runtime check. Any valid-JSON-but-wrong-shape value (an empty object, an
  old schema version, a definition with a field renamed or missing) would
  have been accepted as-is and fed straight into the app, which would then
  read `undefined` off missing fields.
- Added a real runtime structural check,
  `isValidJewelryDefinition()` (`shared/types/jewelry-definition.ts`),
  that verifies every section and field exists with the right type/range
  (finite numbers, known enum values, the current `schemaVersion`) before
  the loaded value is trusted. `loadDefinition()` now returns `null` —
  triggering the existing fallback to `createDefaultDefinition()` — for
  anything that fails this check, corrupted JSON, or a thrown
  `localStorage` access (private browsing / disabled storage).
- Tests: `frontend/src/store/persistence.test.ts` (14 cases covering
  corrupted JSON, missing sections, obsolete schema version, string-typed
  numbers, non-finite numbers, invalid enums, and a throwing
  `localStorage`).

## 6. Preview reliability (Three.js / React Three Fiber)

- **Real bug fixed (GPU memory leak):** `BufferGeometry` objects built
  from fetched STL data were never disposed. Regenerating the model
  repeatedly leaked one set of GPU buffers per regeneration. Old
  geometries are now disposed exactly once — when replaced by a
  successfully-loaded new set, or when the hook unmounts — never before a
  replacement is actually ready.
- In-flight preview-mesh fetches are now cancelled with `AbortController`
  when superseded by a newer request (rapid parameter changes no longer
  leave abandoned fetches running in the background).
- A failed preview-mesh fetch (detected via a non-OK HTTP status or a
  network error) no longer clears the currently-displayed geometries — the
  last successful preview stays visible, and a new `hasError` flag lets
  the viewport show a non-blocking notice.
- The stale-marking behavior (`isStale` in `useProjectStore`) was not
  touched and continues to work — a model becomes stale the moment any
  parameter changes after a successful generation.
- Tests: `frontend/src/hooks/useComponentGeometries.test.ts` (7 cases:
  load, skip-null-url, keep-previous-on-error, dispose-on-replace,
  abort-on-supersede, dispose-on-unmount).

## 7. Docker & Vite

- Frontend image bumped from `node:20-slim` to `node:24-slim`; dependency
  install changed from `npm install` to `npm ci` (reproducible install
  from the committed lockfile, matching the CI workflow).
- `vite.config.ts` now explicitly sets `server.fs.allow` to include both
  the frontend project root and the sibling `shared/` directory. Locally,
  Vite's dev server auto-detects an allowed root that happens to cover
  `../shared` (via `.git` discovery); inside the Docker image there is no
  `.git` and no shared `package.json` workspace, so without this explicit
  allow-list Vite would refuse to serve `shared/*` files with a 403 even
  though the `@shared/*` alias resolves the path correctly.
- `docker-compose.yml`'s `JEWELMIND_CORS_ORIGINS` and `VITE_API_BASE_URL`
  changed from hardcoded literals to `${VAR:-default}` substitutions, so a
  `.env` file (Compose reads one automatically if present) can override
  either without editing the compose file. `.env.example` documents both
  variables and remains committed; `.env` itself remains gitignored.
  No secrets are needed or invented — both variables are plain URLs.
  Ports are unchanged: frontend on 3000, backend on 8000.
- Docker itself was not available in this environment (see §11) — this
  configuration was reviewed carefully but the live `docker compose up`
  smoke test could not be executed here. It now runs automatically in CI
  (`.github/workflows/ci.yml`, `docker-smoke-test` job).

## 8. Repository cleanup

- Removed an absolute personal Windows path (`C:\Users\ArmandoGervasi\...`)
  from `.claude/launch.json`, replaced with paths relative to the repo
  root (matching how the frontend entry in the same file already worked).
- Removed the personal email address from `backend/pyproject.toml`,
  `frontend/package.json`, and `README.md` — the founder's **name**
  (Armando Gervasi) is kept where it was already present; only the email
  address was removed, since a project manifest doesn't need one.
- Searched the full repository for API keys, tokens, and passwords — none
  were found (a few false-positive matches for the substring "token" were
  all legitimate npm package names, e.g. `js-tokens`).
- Confirmed no generated CAD files (`.step`/`.stl`) or cache directories
  (`__pycache__`, `.pytest_cache`, `.ruff_cache`) were ever committed.
  `.gitignore` was tightened anyway: the Python cache rules now apply
  repo-wide instead of only under `backend/`, and `*.step`/`*.stl` are now
  ignored everywhere (these are always generated output in this project,
  never hand-authored source).

## 9. Continuous integration

New `.github/workflows/ci.yml`, running on every push and pull request
targeting `main`:

- **`backend` job** — Python 3.11, installs the OpenCascade/VTK shared
  libraries CadQuery needs (mirroring `backend/Dockerfile`), installs
  `requirements.txt`, runs `ruff check .`, runs the full `pytest` suite.
- **`frontend` job** — Node 24, `npm ci`, `npm run lint`, `npm run test`,
  `npm run build` (TypeScript strict build + Vite production build).
- **`docker-smoke-test` job** — runs only after both jobs above succeed;
  `docker compose up -d --build`, polls `/api/health` until it responds,
  then verifies the health endpoint, `/docs`, and the frontend root all
  respond; prints `docker compose logs` on failure; always runs
  `docker compose down -v` regardless of outcome.

## 10. Documentation

- `README.md`: corrected the Node.js version (20+ → 24, matching Docker
  and CI), updated the backend/frontend test counts, and added a short
  pointer to this file.
- This file (`AUDIT_FIXES.md`) — new.

## What was verified vs. what could not be

| Item | Status |
|---|---|
| Backend: Python compiles, Ruff, full pytest suite | ✅ Executed directly — 139 passed |
| Frontend: `npm ci`, lint, tests, `tsc -b`, production build | ✅ Executed directly — 41 passed, 0 type errors |
| Docker: `docker compose up --build` live in this environment | ❌ **Not executed** — Docker was not installed/available here. Configuration was reviewed for correctness (YAML syntax validated, variable substitution checked, port mappings unchanged) but the live smoke test only runs in GitHub Actions CI, not in this local pass. Do not read the CI workflow's existence as proof it has actually run successfully yet — check the Actions tab after this is pushed. |

No feature described in the original product spec was removed, renamed, or
had its behavior changed except to make an existing failure mode explicit
and safe instead of silent or crashing.
