---
id: JM-BIBLE-026
title: Known Technical Limitations
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on: []
related_documents:
  - JM-BIBLE-005
implementation_status: current
---

# Known Technical Limitations

**Authoritative source:** `docs/known-limitations.md` remains the primary,
most detailed reference for this subject and is not duplicated here in
full — this document is a Bible-level index into it, plus the additions
from the later hardening pass (`AUDIT_FIXES.md`).

## Geometry (see `docs/known-limitations.md` "Geometry")

- Stone reference is a simplified approximation, not a gemological
  reproduction.
- Prongs are plain cylinders; basket support is a plain cylindrical
  shell — both deliberately simple rather than decorative.
- The flat band profile's optional outer-rim fillet has a documented
  fallback (sharp edges + warning) if the OpenCascade fillet operation
  fails for a given input.
- No manufacturing-grade tolerancing beyond the sixteen validation rules.
- Metal choice is cosmetic only — it does not affect geometry or export
  content.

## Preview / export (see `docs/known-limitations.md` "Preview / export")

- GLB export was evaluated and deliberately not used — per-component STL
  + manifest was chosen instead (see
  [ADR-007](../03-decisions/ADR-007-backend-generated-preview.md)).
- Combined STL/STEP export depends on a successful boolean fuse; falls
  back to a multi-solid compound if it fails, per LAW-005.

## API / infrastructure

- **In-memory model cache, not persistent storage.** Capped at 20
  entries, cleared on backend restart. No database in this milestone.
- **Docker image serves the frontend via the Vite dev server**, not a
  production build behind a lightweight web server (e.g. nginx). A
  multi-stage production image is a plausible next improvement, not yet
  built.
- **Docker was reviewed, not always live-tested locally.** See
  `AUDIT_FIXES.md`'s verification table for exactly what was and wasn't
  executed in each hardening pass; the `docker-smoke-test` CI job now
  covers this automatically on every push/PR.
- **No authentication, multi-user isolation, or persistence** — by design,
  see [`025-security-and-data-handling.md`](025-security-and-data-handling.md).

## Domain model

- **No shared-schema codegen** — the Pydantic schema and its TypeScript
  mirror are kept in sync by hand.
- **EU/French sizing convention only** — `ring.sizeSystem` is fixed to
  `"EU"`, and the size↔diameter conversion assumes the French/EU civil
  convention specifically (`size = π·diameter − 40`), not the German
  convention.
- **Only round stones and 4/6-prong solitaire settings** — see
  [`006-scope-and-boundaries.md`](../00-foundation/006-scope-and-boundaries.md).

## Hardening-pass additions (from `AUDIT_FIXES.md`)

Beyond what `docs/known-limitations.md` already covered, a subsequent
hardening pass found and fixed (not merely documented) the following real
defects — recorded here so future readers know these classes of bug were
specifically checked, not just assumed absent:

- A malformed `Infinity`/`NaN` value could crash the API's own
  error-reporting path (fixed — see
  [`025-security-and-data-handling.md`](025-security-and-data-handling.md)).
- Concurrent STEP/STL exports for the same model could overwrite each
  other's temp file (fixed — unique per-request temp files).
- The technical specification's timestamp changed on every download
  instead of reflecting the original generation time (fixed).
- The frontend's `localStorage` load path trusted a type assertion
  instead of a runtime structural check (fixed).
- Preview-mesh `BufferGeometry` objects were never disposed, a GPU memory
  leak under repeated regeneration (fixed).

## What remains open

- Performance under concurrent load has no defined budget (see
  [`014-non-functional-requirements.md`](../01-product/014-non-functional-requirements.md)
  JM-NFR-005).
- A production-grade frontend Docker image (nginx-served static build)
  has not been built.
