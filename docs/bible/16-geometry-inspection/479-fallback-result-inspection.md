---
id: JM-BIBLE-479
title: Fallback Result Inspection
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-INSPECTION-README
  - JM-BIBLE-460
related_documents:
  - JM-BIBLE-478
  - JM-BIBLE-462
implementation_status: current
professional_validation: not_required
normative: true
---

# Fallback Result Inspection

## This Sprint does not introduce a new fallback-tracking mechanism

This is the single most important thing to understand about fallback inspection in Geometry Inspection v2: **the fallback signal already existed**, as real free-text warning strings, before this Sprint. What this Sprint adds is a *structured, queryable* representation of the same signal — `BooleanOperationResult.fallbackUsed` (a real `bool`) and `ComponentInspectionResult.fallbackUsed` (also a real `bool`) — not a second, independent detection mechanism running in parallel.

## The pre-existing mechanism (Sprint 5 and earlier)

[`appendices/atlas-fallback-register.md`](../appendices/atlas-fallback-register.md) (`ATLAS-FALLBACK-001`, `ATLAS-FALLBACK-002`) documents the two fallback paths that exist anywhere in the current geometry codebase, both from Sprint 5 or earlier:

1. **Band outer-rim fillet** (`ATLAS-FALLBACK-001`) — if `_try_fillet_outer_rim()` raises or yields zero solids, `build_ring_band()` (`geometry/components/band.py`) catches the exception, falls back to the pre-fillet sharp-edged solid, and appends a human-readable warning string to `GeneratedComponent.warnings`: `"Outer rim fillet could not be applied ({exc}); falling back to sharp edges."` It also sets `metadata["filletApplied"] = False`.
2. **Combined-metal boolean fuse** (`ATLAS-FALLBACK-002`) — if `_fuse_metal()`'s `.fuse()` chain raises or yields zero solids, `solitaire.py` falls back to `cq.Compound.makeCompound([band.shape, basket.shape, prongs.shape])` and appends: `"Combined metal union failed ({exc}); exporting band, prongs, and basket as a multi-solid compound instead of a single fused solid."`

Both of these were, until this Sprint, only discoverable by reading a warning string — either directly in `GeneratedComponent.warnings`/`GeneratedModel.warnings`, or by a human reading the technical specification text these warnings feed into (`exporters/specification.py`). There was no `True`/`False` field anywhere a caller could check programmatically.

## What this Sprint's audit found

Per the Sprint 14 brief's own explicit instruction to search for "fallback geometry never inspected" (echoing ATLAS-GOV-004/005's requirement that any new fallback path be reported and registered): the actual finding from that audit was **not** that fallback geometry goes unreported. It was already reported, as prose. The gap was that it was reported *only* as prose — a string a human has to read and interpret, not a structured value a caller (or, eventually, Forge) could compare, filter, or assert against without string-matching. This Sprint's real contribution is surfacing the same two real signals through the new `GeometricFact`/`BooleanOperationResult` shape:

- `ComponentInspectionResult.fallbackUsed` — set to `bool(component.warnings)` in `inspect_component()` (`components.py:91`), for every one of the 4 components, not only `band`.
- `BooleanOperationResult.fallbackUsed` — for the 3 per-component boolean entries, the same `comp.fallbackUsed` value carried through; for `combined_metal`, an independently re-derived signal (`combined_solids.solids > 1`, see [`478-boolean-result-inspection.md`](478-boolean-result-inspection.md)) that measures the real geometric consequence of the fallback rather than re-reading the warning list.

This was a deliberate reuse decision, not an oversight requiring a fix: the existing warning-string convention remains the single source of truth for *why* a fallback fired (the exception message is only ever captured in the warning string, never in a structured field); the new structured fields answer *whether* one fired, in a form a caller can check without parsing text.

## Real current finding: neither fallback fires for the default solitaire

Verified directly: the band's fillet succeeds (`metadata["filletApplied"] = true`, `warnings = []`), and `combined_metal` is exactly 1 solid (the `.fuse()` chain succeeds). So for the default solitaire, every `fallbackUsed` field in the report — component-level and boolean-operation-level — is `False`. Neither `ATLAS-FALLBACK-001` nor `ATLAS-FALLBACK-002` has a dedicated regression test that forces it to trigger (the register itself states this: "no test forces this fallback to trigger; it is verified only by code review"), so this Sprint's inspection code has likewise never been exercised against an actual fallback firing in an automated test — only against the non-fallback path.

## Tests

`backend/tests/test_geometry_inspection.py::TestFallbackInspection::test_band_fillet_fallback_state_is_visible_via_metadata` and `test_combined_metal_multi_solid_is_detectable_as_a_fallback_signal` both confirm the *mechanism* works (the fields read the right underlying values), not that a fallback has ever actually fired end-to-end.

## Cross-references

- [`478-boolean-result-inspection.md`](478-boolean-result-inspection.md) — the concrete field-by-field description of `BooleanOperationResult`.
- [`appendices/atlas-fallback-register.md`](../appendices/atlas-fallback-register.md) — the authoritative, pre-existing register this document builds on.
- [`07-atlas/135-fillets-rounding-and-fallbacks.md`](../07-atlas/135-fillets-rounding-and-fallbacks.md) — the Sprint 5 fallback contract.
