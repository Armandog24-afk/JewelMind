---
id: JM-BIBLE-020
title: Architecture Overview
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-007
related_documents:
  - JM-BIBLE-021
  - JM-BIBLE-022
  - JM-BIBLE-ADR-008
  - JM-BIBLE-121
implementation_status: current
---

# Architecture Overview

This document summarizes the architecture at a level above
`docs/architecture.md`, which remains the authoritative, detailed
reference — see that file for the full request-flow walkthrough and
directory-by-directory breakdown.

## Shape: one monorepo, one frontend, one backend

```
jewelmind/
  frontend/   React + TypeScript (strict) + Vite + React Three Fiber
  backend/    Python 3.11 + FastAPI + Pydantic v2 + CadQuery
  shared/     TypeScript-only domain types & validation mirror
  docs/       Technical reference docs + this Bible
  examples/   Sample JewelryDefinition JSON files + a headless generator script
  scripts/    Dev convenience scripts
```

No microservices, no message queue, no separate database service. See
[ADR-008](../03-decisions/ADR-008-monorepo-architecture.md) for why.

## Layering

The backend is organized in strict layers, each with one responsibility:

```
api/        <- HTTP only: routing, request/response schemas, error mapping
services/   <- orchestration: validate -> generate -> cache -> export
validation/ <- business rules, no CadQuery, no HTTP
geometry/   <- CadQuery geometry construction, no HTTP, no business rules
preview/    <- mesh tessellation for the browser
exporters/  <- file format writers (STEP, STL, JSON, specification)
domain/     <- the canonical schema itself
utils/      <- hashing, logging — no domain knowledge
```

`domain/` and `validation/` have zero dependency on FastAPI or CadQuery —
they are pure Python business logic, testable in isolation. `geometry/`
has zero dependency on FastAPI or HTTP concerns. This separation is what
[`022-domain-boundaries.md`](022-domain-boundaries.md) exists to enforce
and document.

## CadQuery / OpenCascade as the geometry core

All 3D geometry is constructed through CadQuery
(`backend/jewelmind/geometry/`), which drives the OpenCascade B-Rep
kernel. This is a deliberate choice over a mesh-only or procedural-only
approach — see [ADR-001](../03-decisions/ADR-001-cadquery-for-mvp.md).
**This layer is formalized as "Atlas"** in Sprint 5 —
[`07-atlas/README.md`](../07-atlas/README.md) — the deterministic
geometry layer that owns primitives, coordinate conventions, component
contracts, and geometric inspection, while jewelry-domain thresholds
remain owned exclusively by Forge ([`06-forge/README.md`](../06-forge/README.md)).

## Preview pipeline

The backend tessellates each named solid to its own binary STL file
(`preview/mesh.py`) rather than packaging everything into one GLB — see
[ADR-007](../03-decisions/ADR-007-backend-generated-preview.md) and
`docs/known-limitations.md` for the reasoning. The frontend fetches and
parses these directly (`frontend/src/hooks/useComponentGeometries.ts`),
never rendering anything not derived from real backend geometry
(LAW-002).

## Export pipeline

STEP, STL, JSON, and Markdown-specification exporters
(`backend/jewelmind/exporters/`) each take the already-generated
`GeneratedModel` and definition, and write a real file. Export requests
are keyed by `modelId` (not by a raw definition), so an export always
corresponds to an already-validated, already-generated model — see
[`023-data-flow.md`](023-data-flow.md).

## Validation pipeline

Two engines run the same sixteen rules: `backend/jewelmind/validation/engine.py`
(authoritative) and `shared/validation/engine.ts` (frontend mirror, for
instant feedback only). The backend always re-validates before generation
and export regardless of what the frontend believes — see Product
Principle 6.

## State management

- **Frontend:** one Zustand store (`frontend/src/store/useProjectStore.ts`)
  holds `currentDefinition`, `validationResults`, `generatedModel`,
  `generationStatus`, `exportStatus`, `backendStatus`,
  `lastSuccessfulPreview`, and `isStale`.
- **Local persistence:** `localStorage`, one project slot, validated on
  load (`frontend/src/store/persistence.ts`).
- **Server-side model cache:** an in-memory, process-lifetime cache of
  generated models keyed by definition hash, capped at 20 entries with
  LRU eviction (`backend/jewelmind/services/model_service.py`). This is
  not a database — see
  [`025-security-and-data-handling.md`](025-security-and-data-handling.md).

## Runtime and deployment

See [`024-runtime-and-deployment.md`](024-runtime-and-deployment.md) for
local non-Docker development, Docker Compose, ports, and CI.
