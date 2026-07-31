---
id: JM-BIBLE-022
title: Domain Boundaries
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on:
  - JM-BIBLE-020
related_documents:
  - JM-BIBLE-004
implementation_status: current
---

# Domain Boundaries

This document states, explicitly, what must never cross which
architectural boundary — the enforcement mechanisms behind Product
Principles 4–7 and the corresponding Constitution laws.

## UI must not own geometry logic

**Boundary:** `frontend/src/components/` and `frontend/src/hooks/` must
never construct or reason about CAD geometry — they only fetch and
render meshes the backend already built.

**Why:** geometry construction must be deterministic and testable in one
place (`backend/jewelmind/geometry/`); duplicating it in JavaScript would
create two sources of truth that can silently drift.

**Current compliance:** `useComponentGeometries.ts` parses STL bytes into
`THREE.BufferGeometry` — it does not compute any dimension; every number
in the mesh came from the backend.

## Exporters must not own validation logic

**Boundary:** `backend/jewelmind/exporters/` must never independently
decide whether a definition is valid — they only operate on an
already-generated `GeneratedModel`, which by construction could only
exist if `services/model_service.py::generate()` already confirmed no
validation errors.

**Why:** duplicating validation inside an exporter risks it disagreeing
with the authoritative check, and violates LAW-008 (invalid definitions
cannot generate or export).

**Current compliance:** none of the four exporter modules import
`validation/engine.py`; all export endpoints resolve a model by
`modelId` (see [`023-data-flow.md`](023-data-flow.md)), not by accepting a
raw definition to re-check.

## CadQuery objects must not leak into frontend code

**Boundary:** no `cq.Workplane`, `cq.Shape`, or any OpenCascade type ever
crosses the API boundary — the frontend only ever sees JSON metadata and
binary STL bytes.

**Why:** CadQuery objects are not serializable across the network in any
meaningful way, and coupling the frontend to backend-internal types would
break the layering in [`020-architecture-overview.md`](020-architecture-overview.md).

**Current compliance:** `api/routes.py` never returns a raw geometry
object; `GenerateResponse`/`ModelMetadataResponse` (in `api/schemas.py`)
are plain Pydantic models of primitives, dicts, and lists.

## Frontend validation must never be treated as authoritative

**Boundary:** `shared/validation/engine.ts` exists only to give the user
instant feedback. Every backend generate/export endpoint re-runs
`backend/jewelmind/validation/engine.py` itself.

**Why:** a client could be running stale code, be compromised, or simply
disagree with the backend by a bug — the backend must never trust a
client's self-report of validity. This is Product Principle 6 /
[LAW-008](../00-foundation/004-jewelmind-constitution.md#LAW-008).

**Current compliance:** `services/model_service.py::generate()` calls
`validate_definition()` itself and raises `ValidationBlockedError` before
touching CadQuery, regardless of what the frontend sent alongside the
definition (which is nothing — the frontend does not send its own
validation verdict at all).

## Stone reference must not be confused with production metal

**Boundary:** `combined_metal` (the fused band + prongs + basket) and
`stone_reference` are always distinct fields on `GeneratedModel`; no
exporter unions them unless `include_stone=True` is explicitly passed.

**Why:** [LAW-006](../00-foundation/004-jewelmind-constitution.md#LAW-006) — a
manufacturing file that accidentally included the (non-manufacturable)
stone reference solid would be simply wrong.

**Current compliance:** `geometry/assemblies/solitaire.py::_fuse_metal`
only ever receives `band`, `basket`, `prongs` — `stone` is never passed to
it. `step_exporter.py` / `stl_exporter.py` both default
`include_stone=False`.

## Summary table

| Boundary | Enforced by | Test |
|---|---|---|
| UI ↛ geometry logic | Code structure (no CadQuery-equivalent in `frontend/`) | Code review |
| Exporters ↛ validation logic | `modelId`-keyed export endpoints | `test_api.py::test_export_with_unknown_model_id_returns_404` |
| CadQuery objects ↛ frontend | Pydantic response schemas | Code review of `api/schemas.py` |
| Frontend validation ↛ authoritative | Backend always re-validates | `test_api.py::test_generate_invalid_definition_returns_422` |
| Stone ↛ production metal | Separate fields, explicit opt-in | `test_geometry.py::test_stone_reference_is_valid_and_separate_from_metal` |
