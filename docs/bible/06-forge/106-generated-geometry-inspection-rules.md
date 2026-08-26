---
id: JM-BIBLE-106
title: Generated Geometry Inspection Rules
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-093
related_documents:
  - JM-BIBLE-111
  - JM-BIBLE-140
implementation_status: partial
professional_validation: not_required
normative: true
---

# Generated Geometry Inspection Rules

**Relationship to Atlas (Sprint 5):** [`07-atlas/140-geometry-inspection-framework.md`](../07-atlas/140-geometry-inspection-framework.md)
is the full Atlas-level formalization of the finding below, with the
complete GEOMETRIC-FACT-vs-FORGE-INTERPRETATION vocabulary
(`checkType`, `status`: `PASS`/`FAIL`/`UNKNOWN`/`NOT_APPLICABLE`) this
document's table anticipates but does not itself define. Nothing in
Sprint 5 changes the finding immediately below.

**Sprint 14 (Geometry Inspection v2) materially closes this gap** —
see [`16-geometry-inspection/README.md`](../16-geometry-inspection/README.md).
`backend/jewelmind/geometry/inspection/` now runs, unconditionally, on
every real `ModelService.generate()` call — not only in
`test_geometry.py`. The table below is updated to reflect the real
current runtime/test-only split; see
[`16-geometry-inspection/493-current-solitaire-inspection-map.md`](../16-geometry-inspection/493-current-solitaire-inspection-map.md)
for the full per-relationship breakdown this table summarizes.

## CURRENT: most of the table below is now genuinely runtime

Before Sprint 14, only one geometry-inspection check ran at request time: `FORGE-GEOM-001` — `_fuse_metal()`'s `if not fused.Solids(): raise ValueError(...)` (caught internally, triggering the documented compound fallback with a warning; see `backend/jewelmind/geometry/assemblies/solitaire.py`). As of Sprint 14, `ModelService.generate()` also calls `jewelmind.geometry.inspection.inspect_model()` unconditionally on every real generation, and its result is stored on `ModelRecord.inspection_report` — most of the table below is now genuinely runtime, not test-only.

| Property | Verified by | Runtime or test-only? |
|---|---|---|
| Component exists (band, stone_reference, prongs, basket_support all present) | `test_solitaire_assembly_has_all_required_components` (dev-time) **and** `inspect_component()`/`AssemblyInspectionResult.requiredComponentsPresent` (Sprint 14) | **Runtime** |
| Shape not null / has solids | Same dev-time tests **and** `ComponentInspectionResult.exists`/`solidCount` | **Runtime** |
| Positive volume | Same dev-time tests **and** `ComponentInspectionResult.volumeMm3` (finite/non-negative check) | **Runtime** |
| Plausible bounding box | Same dev-time tests **and** `ComponentInspectionResult.boundingBox` | **Runtime** (a real bounding box is now always computed; "plausibility" itself is still not interpreted — that remains Forge's job, unimplemented) |
| Requested prong count equals generated count | Same dev-time tests **and** `AssemblyInspectionResult.prongCount` | **Runtime** |
| Stone remains separate from metal | Same dev-time test **and** `AssemblyInspectionResult.stoneMetalSeparation` (structural — the stone's shape is never an argument to any fuse call) | **Runtime** |
| Combined metal is a usable solid (or falls back to a compound) | `_fuse_metal()` (`FORGE-GEOM-001`) **and** `AssemblyInspectionResult.booleanOperations`'s `combined_metal` entry | **Runtime** (now doubly so: the original blocking check, plus a structured fact) |
| Production connectivity (are band/prongs/basket_support geometrically one connected group?) | New in Sprint 14 — no prior test existed for this | **Runtime** (`AssemblyInspectionResult.productionConnectivity`) — a genuinely new fact this codebase could not previously state at all |
| Pairwise component intersections/distances | New in Sprint 14 — no prior test existed for this | **Runtime** (`AssemblyInspectionResult.intersections`/`distances`) |
| Export shape exists | Implicit in `export_step`/`export_stl` succeeding; still no dedicated pre-export geometry check | Test-only (via `backend/tests/test_api.py`'s export endpoint tests) — Sprint 14 deliberately did NOT make export depend on inspection, see [`16-geometry-inspection/489-foundry-inspection-integration.md`](../16-geometry-inspection/489-foundry-inspection-integration.md) |

## What remains a real, honest gap after Sprint 14

Sprint 14 reports real geometric facts; it still does not *interpret* any of them as a jewelry-domain or manufacturing violation — that remains exclusively Forge's job, and no Forge rule currently consumes a `GeometricFact` (see [`16-geometry-inspection/487-forge-fact-contract.md`](../16-geometry-inspection/487-forge-fact-contract.md)). So a caller still cannot get "your specific definition produced a component with implausible proportions" as a diagnosed rule violation — only the raw fact itself, via `GET /api/models/{id}/inspection` or the concise summary embedded in `/generate`/`/metadata`. See [`111-domain-rule-gap-analysis.md`](111-domain-rule-gap-analysis.md) and [`115-open-forge-questions.md`](115-open-forge-questions.md) for this remaining gap, and [`16-geometry-inspection/494-current-runtime-inspection-gap-analysis.md`](../16-geometry-inspection/494-current-runtime-inspection-gap-analysis.md) for the full Sprint 14 gap list.

## PLANNED checks (still not implemented, do not exist in any form)

Self-intersection detection (beyond pairwise named-component intersection), minimum local thickness analysis, non-manifold geometry detection (beyond the binary `isValid()` check), trapped-volume detection, inaccessible-polishing-region detection, support continuity verification. **None of these has any code, test, or partial implementation in this repository.** Disconnected-metal-bodies detection and stone-metal interference/separation detection — both listed as PLANNED in earlier Sprints — are the two items Sprint 14 actually implemented for real; they are removed from this list accordingly. See [`16-geometry-inspection/494-current-runtime-inspection-gap-analysis.md`](../16-geometry-inspection/494-current-runtime-inspection-gap-analysis.md) for why each remaining item matters and what expertise would be needed to implement it correctly.
