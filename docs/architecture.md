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
  stone/ gem/ arrangement/ family/ halo/ pave/ setting/ ring_family/
                CATEGORY- AND KERNEL-NEUTRAL subsystems. Each owns one domain,
                imports no jewelry category and no geometry, and is enforced by
                an AST-parsing test. Every one's __init__.py deliberately
                imports NOTHING: domain/schema.py imports their models modules,
                so an eager package init would make the graph cyclic.
  geometry/
    constants.py          coordinate convention (see docs/geometry-conventions.md)
    model.py               GeneratedComponent / GeneratedModel / BoundingBox
    primitives/            small reusable CadQuery selectors (e.g. fillet edge selection)
    components/            band.py, stone.py, prongs.py, basket.py (thin re-exports)
    shank/                 the Shank subsystem: profile, taper, builder, architecture
    stone/                 the Stone placement adapter, outlines and profiles
    shoulder.py            shoulder arches (Sprint 28)
    signet.py              the signet body (Sprint 28)
    setting_adapter.py     JewelryDefinition -> Setting contracts
    ring_family_adapter.py JewelryDefinition -> resolved ring family (Sprint 28)
    assemblies/             solitaire.py — the RingHead, combining every component
  preview/       Tessellates each component to a binary STL + manifest
  exporters/     STEP / STL / JSON / Markdown-specification exporters, filename sanitizer
  services/      model_service.py — orchestrates validate -> generate -> cache -> export
  api/           FastAPI app, routes, Pydantic request/response schemas, error envelope
  utils/         Structured logging (structlog), definition hashing
```

Domain logic (validation rules, geometry construction) lives entirely
under `domain/`, `validation/`, the neutral subsystems and `geometry/` — it has
no FastAPI or CadQuery-export imports, and no UI concerns. The neutral
subsystems go further: they may not import geometry or the CAD kernel at all,
and each has ONE sanctioned meeting point with `JewelryDefinition`
(`geometry/setting_adapter.py`, `geometry/ring_family_adapter.py`,
`family/effective.py`), so a domain layer can never reach a solid. `api/` and `services/` are the
only layers that know about HTTP; `exporters/` and `preview/` are the only
layers that know about file formats. This separation is what
`CLAUDE.md` asks future changes to preserve.

## Request flow (generate)

1. Frontend `POST /api/models/generate` with the current `JewelryDefinition`.
2. `api/routes.py` hands it to `services/model_service.py`.
3. `model_service` runs `validation/engine.py`. Any `error` result aborts
   with `422 VALIDATION_BLOCKED` before any geometry work happens.
4. `geometry/ring_family_adapter.py::effective_definition()` resolves the
   ring family and applies its DERIVATIONS, producing the *effective*
   document the geometry is built from (Sprint 28). It returns the ORIGINAL
   object when the family changes nothing, so a document declaring no family
   reaches the exact path it always did.
5. `geometry/assemblies/solitaire.py` builds the named components — band,
   stone_reference, prongs, basket_support, plus whatever the design asks for
   (a setting family's own component, pavé stones and retention, halo stones,
   shoulders, a signet body) — fuses the production-metal ones into one solid
   when possible, and computes a deterministic `definitionHash` **from the
   ORIGINAL document**, not the effective one: the identity is what the author
   wrote, so a derived value never becomes part of the design's name.

   The fuse falls back to a multi-solid compound, with a warning, if it raises
   OR if it returns a volume smaller than its largest input — a union cannot be
   smaller than any body it unions, and Sprint 28 found a fuse that succeeded
   and returned negative volumes without raising.
6. `preview/mesh.py` tessellates each component to its own binary STL file
   in a per-model temporary directory, plus a small JSON manifest.
7. The response carries the model id (= `definitionHash`), validation
   results, volumes/bounding boxes, and one preview URL per component.
8. The frontend fetches each component's STL directly
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
