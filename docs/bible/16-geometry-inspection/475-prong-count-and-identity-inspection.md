---
id: JM-BIBLE-475
title: Prong Count and Identity Inspection
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
  - JM-BIBLE-474
  - JM-BIBLE-476
  - JM-BIBLE-494
implementation_status: partial
professional_validation: not_required
normative: true
---

# Prong Count and Identity Inspection

## What `_prong_count()` actually does

`assembly.py::_prong_count()` (`backend/jewelmind/geometry/inspection/assembly.py:78-91`) does not recompute a prong count from geometry. It reads two values that `build_prongs()` (`geometry/components/prongs.py`) already computed and stored on the `prongs` component:

```python
requested = prongs.metadata.get("requestedCount")
generated = prongs.metadata.get("generatedCount")
```

If either key is missing (a component that never went through `build_prongs()`, e.g. a test fixture), the result is `ProngCountResult(requestedCount=0, generatedCount=0, matches=False, status="UNKNOWN")`. Otherwise it returns `requestedCount`, `generatedCount`, `matches = requested == generated`, and `status = "PASS" if matches else "FAIL"`.

This is a re-reporting inspection, not an independent measurement — it trusts the geometry builder's own bookkeeping rather than, say, independently counting solids in the compound and comparing that count to the requested value. `TestSolidCount::test_prongs_solid_count_matches_generated_count` (`backend/tests/test_geometry_inspection.py`) is the test that separately confirms `ComponentInspectionResult.solidCount` for `prongs` (derived independently, via `Shape.Solids()`) agrees with `metadata["generatedCount"]` — the two numbers are cross-checked, just not by `_prong_count()` itself.

## Where 4/6 validation actually lives

`build_prongs()`'s own docstring is explicit: "geometry generation is expected to be blocked upstream by validation errors" for an unsupported count — it stays honest about what it was asked to build rather than refusing to build it. The real gate is Forge's `JM-PRONG-001` rule (`backend/jewelmind/validation/rules.py:33`, enforced in `backend/jewelmind/validation/engine.py:136-146`), which flags `d.setting.prongCount not in (4, 6)` as a validation error at `ModelService.generate()`'s validation step, before geometry construction ever runs for real user-submitted input. `_prong_count()` in `geometry/inspection/` never reads or references `JM-PRONG-001` — per INSPECT-GOV-002, no file under `backend/jewelmind/geometry/inspection/` imports `backend/jewelmind/validation/`. The inspection result and the Forge rule report on the same real fact (requested vs. supported prong count) at two different, deliberately separated layers.

## Real clamping behavior for unsupported input

`build_prongs()`:

```python
generated_count = requested_count if requested_count in (4, 6) else max(requested_count, 0)
```

A requested count of `-1` clamps to `generated_count = 0` (no prong solids built at all, `positions = []`). This only happens when `build_solitaire_ring()` is called directly, bypassing validation — the same pattern `test_negative_requested_count_is_reported_as_a_mismatch` uses on purpose. In that case `_prong_count()` reports `requestedCount=-1`, `generatedCount=0`, `matches=False`, `status="FAIL"`. A requested count of `5` (also unsupported, but non-negative) clamps to `generated_count = max(5, 0) = 5` — `build_prongs()` happily builds 5 real prong solids; only Forge's `JM-PRONG-001` would flag this as invalid, never the geometry builder or this inspection.

## Individual prong identity: investigated, not implemented

The question of whether individual prongs could carry a stable identity (e.g. `prong_0`, `prong_1`, ...) was investigated directly against `build_prongs()` rather than assumed either way:

- `_prong_positions()` returns an ordered `list[tuple[float, float]]` — position `i` is always `(radius * cos(2*pi*i/count), radius * sin(2*pi*i/count))`, a deterministic, index-stable ordering.
- The `for x, y in positions:` loop builds each prong solid in that same order and appends it to `solids` in order.
- `cq.Compound.makeCompound(solids)` merges all of them into **one** compound shape, discarding the per-solid identity the `solids` list had — the compound has no per-sub-solid name or index attached to it as returned.
- `GeneratedModel.components` (`geometry/model.py`) has exactly one key for `prongs` — not `prongs_0`, `prongs_1`, etc.

So the ordering that *would* support an index-based identity genuinely exists inside `build_prongs()` at construction time, but nothing downstream currently captures or exposes it. `ComponentInspectionResult` treats `prongs` as one component with `solidCount=6` (or 4), not as six separately-identified sub-results — there is no `factId` of the shape `component.prongs.0.volume` anywhere in `inspector.py`, and no schema field for a per-prong identity anywhere in `models.py`.

The correct framing for this is "not implemented at all yet," not "schema-complete-but-not-implemented" — unlike, say, `IntersectionStatus`'s `UNKNOWN` value (which the schema *and* the code both support, just rarely reached), there is no `models.py` field reserved for per-prong identity at all. This is a real, current architectural limitation, not a broken promise: nothing in the Sprint 14 brief or `docs/bible/16-geometry-inspection/460-inspection-governance.md` requires per-prong identity, and it is recorded as a candidate future capability in [`494-current-runtime-inspection-gap-analysis.md`](494-current-runtime-inspection-gap-analysis.md) (written concurrently by another agent in this Sprint) rather than treated as an oversight in this document.

## Tests

`backend/tests/test_geometry_inspection.py::TestProngCountInspection` — `test_requested_matches_generated_for_supported_counts` (parametrized over `[4, 6]`) and `test_negative_requested_count_is_reported_as_a_mismatch`. `TestSolidCount::test_prongs_solid_count_matches_generated_count` independently cross-checks the solid count.

## Cross-references

- [`476-component-presence-inspection.md`](476-component-presence-inspection.md) — restates the "one compound component, not N named components" finding at the presence-inspection level.
- [`494-current-runtime-inspection-gap-analysis.md`](494-current-runtime-inspection-gap-analysis.md) — where per-prong identity is recorded as a deferred candidate.
- [`06-forge/110-current-rule-inventory.md`](../06-forge/110-current-rule-inventory.md) — `JM-PRONG-001` and the other three `JM-PRONG-*` rules.
