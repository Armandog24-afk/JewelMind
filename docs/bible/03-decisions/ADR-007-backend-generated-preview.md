---
id: JM-BIBLE-ADR-007
title: "ADR-007: Backend-generated, per-component STL preview (not GLB)"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on:
  - JM-BIBLE-ADR-001
related_documents:
  - JM-BIBLE-004
  - JM-BIBLE-026
implementation_status: current
---

# ADR-007: Backend-generated, per-component STL preview (not GLB)

## Status

Accepted.

## Context

The browser preview must be derived from real backend geometry
([LAW-002](../00-foundation/004-jewelmind-constitution.md#LAW-002)), with
per-component visibility toggles and distinct materials (metal vs. stone).
A single packaged file (e.g. GLB) can carry multiple named meshes and
materials in one request, which is attractive — but CadQuery's GLB export
path was evaluated and judged unreliable for this milestone's timeline.

## Decision

Tessellate each named component (band, stone reference, prongs, basket
support) to its **own binary STL file**, tied together by a small JSON
manifest returned from `/api/models/generate` (`previewComponents`). The
frontend fetches and parses each STL directly.

## Alternatives considered

- **Single packaged GLB with all components and materials embedded.**
  Evaluated first, since it would have been a single request and would
  carry material information natively. Not adopted: CadQuery's GLB export
  support was judged unreliable enough, within this milestone's scope, to
  risk shipping a broken preview pipeline chasing it.
- **A single combined STL for the whole assembly (no per-component
  files).** Rejected: would lose per-component visibility toggling and
  the metal/stone material distinction required by
  [LAW-006](../00-foundation/004-jewelmind-constitution.md#LAW-006) and
  the product spec's component-visibility requirement.
- **Per-component STL + manifest (the chosen path).** Selected — the
  product spec explicitly allows this as a fallback strategy, and it maps
  cleanly onto the existing `GeneratedModel.components` structure with no
  new geometry-side complexity.

## Positive consequences

- No dependency on an unreliable export path — STL export is already
  needed for the download feature anyway (`stl_exporter.py`), so the
  preview pipeline reuses proven code.
- Per-component visibility and material distinction (metal vs.
  transparent stone) fall out naturally from having separate files.
- Frontend loading logic (`useComponentGeometries.ts`) is simple: fetch,
  parse, done — no GLB material/scene-graph parsing needed.

## Negative consequences

- One HTTP request per visible component instead of one combined request
  — more network round trips for a fully-visible model (four requests
  today: band, stone, prongs, basket).
- No embedded material/color data in the files themselves — the frontend
  assigns materials by component name (`ModelViewport.tsx`'s
  `METAL_COLORS` map), which is a reasonable but separate source of
  truth from the geometry.

## Risks

- If CadQuery's GLB support becomes reliable in a future version, revisit
  whether consolidating to one request is worth the migration — this
  would be a new ADR, not a silent change, since it affects the API
  response shape (`previewComponents`).

## Review trigger

Revisit if request-count/latency for the per-component approach becomes
a measured problem (see
[`015-success-metrics.md`](../01-product/015-success-metrics.md) for why
no such measurement exists yet), or if CadQuery's GLB export matures.

## Related implementation files

`backend/jewelmind/preview/mesh.py`,
`frontend/src/hooks/useComponentGeometries.ts`.

## Related tests

`backend/tests/test_api.py::test_preview_component_endpoint_returns_nonempty_stl`;
`frontend/src/hooks/useComponentGeometries.test.ts` (7 tests).
