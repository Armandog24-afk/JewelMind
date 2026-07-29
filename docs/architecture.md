# Architecture

JewelMind is a single frontend + single backend monorepo — no
microservices, no message queues, no external CAD services.

```
jewelmind/
  frontend/    React + TypeScript (strict) + Vite + React Three Fiber
  backend/     Python 3.11 + FastAPI + Pydantic v2 + CadQuery
  shared/      TypeScript-only domain types & validation mirror
  docs/        This documentation set
  examples/    Sample JewelryDefinition JSON files + a headless generator script
  scripts/     Dev convenience scripts (run backend/frontend without Docker)
  docker-compose.yml
  .env.example
  Makefile
```

## Backend package layout

```
backend/jewelmind/
  domain/       Pydantic schema, defaults, canonical-JSON disclaimer text
  validation/   Rule engine, rule-ID constants, EU-size <-> diameter sizing utility
  geometry/
    constants.py          coordinate convention (see docs/geometry-conventions.md)
    model.py               GeneratedComponent / GeneratedModel / BoundingBox
    primitives/            small reusable CadQuery selectors (e.g. fillet edge selection)
    components/            band.py, stone.py, prongs.py, basket.py
    assemblies/             solitaire.py — combines the four components
  preview/       Tessellates each component to a binary STL + manifest
  exporters/     STEP / STL / JSON / Markdown-specification exporters, filename sanitizer
  services/      model_service.py — orchestrates validate -> generate -> cache -> export
  api/           FastAPI app, routes, Pydantic request/response schemas, error envelope
  utils/         Structured logging (structlog), definition hashing
```

Domain logic (validation rules, geometry construction) lives entirely
under `domain/`, `validation/`, and `geometry/` — it has no FastAPI or
CadQuery-export imports, and no UI concerns. `api/` and `services/` are the
only layers that know about HTTP; `exporters/` and `preview/` are the only
layers that know about file formats. This separation is what
`CLAUDE.md` asks future changes to preserve.

## Request flow (generate)

1. Frontend `POST /api/models/generate` with the current `JewelryDefinition`.
2. `api/routes.py` hands it to `services/model_service.py`.
3. `model_service` runs `validation/engine.py`. Any `error` result aborts
   with `422 VALIDATION_BLOCKED` before any geometry work happens.
4. `geometry/assemblies/solitaire.py` builds the four named components
   (band, stone_reference, prongs, basket_support), fuses the metal ones
   into one solid when possible, and computes a deterministic
   `definitionHash`.
5. `preview/mesh.py` tessellates each component to its own binary STL file
   in a per-model temporary directory, plus a small JSON manifest.
6. The response carries the model id (= `definitionHash`), validation
   results, volumes/bounding boxes, and one preview URL per component.
7. The frontend fetches each component's STL directly
   (`GET /api/models/{id}/preview/{name}`) and renders it in the React
   Three Fiber viewport — the preview is never anything but backend-derived
   geometry.

## Frontend structure

```
frontend/src/
  api/          fetch-based client + response types (mirrors backend api/schemas.py)
  store/        one zustand store (useProjectStore) holding all app-level state
  hooks/        useComponentGeometries — fetches + parses each component's STL
  components/   presentational React components (see README for the full list)
  styles/       theme.css (CSS variables) + global.css (one stylesheet, no CSS-in-JS)
```

State is intentionally centralized in a single zustand store rather than
scattered across component-local state, matching the recommended shape in
the product spec: `currentDefinition`, `validationResults`,
`generatedModel`, `generationStatus`, `exportStatus`, `backendStatus`,
`lastSuccessfulPreview`, `isStale`.

## Why one frontend mirrors backend validation

`shared/validation/engine.ts` mirrors `backend/jewelmind/validation/engine.py`
rule-for-rule so the UI can show instant feedback while typing, without a
network round trip on every keystroke. It is explicitly documented as a
mirror, not a second source of truth — the backend always re-validates and
its result always wins (see `docs/validation-rules.md`).
