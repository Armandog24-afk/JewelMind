---
id: JM-BIBLE-474
title: Stone-Metal Separation Inspection
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
  - JM-BIBLE-473
  - JM-BIBLE-471
  - JM-BIBLE-480
  - JM-BIBLE-143
implementation_status: current
professional_validation: not_required
normative: true
---

# Stone-Metal Separation Inspection

LAW-006 (`docs/bible/00-foundation/004-jewelmind-constitution.md`) states: "the stone solid must never be unioned into the metal body, and must never appear in a STEP\STL export unless `includeStoneReference: true` was explicitly requested." [`07-atlas/143-stone-metal-separation-contract.md`](../07-atlas/143-stone-metal-separation-contract.md) (Sprint 5) formalized how the *construction* code enforces this. This document covers the new piece: `assembly.py::_stone_metal_separation()` (`backend/jewelmind/geometry/inspection/assembly.py`), which runs on every generation and reports, as a real fact, whether that guarantee held for the model that was just built.

## The distinction this check exists to make

Two different geometric relationships are easy to conflate and must not be:

1. **"Intersects a production component."** A real, expected geometric fact for the default solitaire. `EMBED_MM = 0.4` (`geometry/constants.py`) is a deliberate construction choice — prongs and the basket support are built to overlap the stone's girdle by design, so a fuse between metal components produces genuine solid contact and the prongs read as gripping the stone. This is reference-geometry realism, not a defect.
2. **"Fused into production metal."** Never happens in the current architecture. `_fuse_metal(band, prongs, basket)` in `geometry/assemblies/solitaire.py` takes exactly three arguments — band, prongs, basket — and its body calls only `band.shape.fuse(basket.shape)` then `.fuse(prongs.shape)`. There is no line of code anywhere in `solitaire.py`, or anywhere else, that passes `stone.shape` to a `.fuse()`/`.cut()`/`.common()` call. This is the same "structural guarantee, not just a runtime check" argument `143-stone-metal-separation-contract.md` already makes for construction; this Sprint's contribution is a runtime fact that *reports* that guarantee on every generation instead of leaving it to be re-derived from reading the source.

## Real code path

`_stone_metal_separation()` (`assembly.py:37-75`):

1. If `stone_reference` is missing or has no solids, returns immediately: `stoneReferenceExists=False`, `fusedIntoProductionMetal=False`, `status="FAIL"`, note `"No stone_reference component was generated."`
2. Otherwise, filters the assembly's real pairwise `IntersectionResult`s (already computed by `inspect_assembly()` before this function runs) down to the ones involving `stone_reference` with `status == "INTERSECTS"` against a component `is_production_component()` (`geometry/roles.py`) reports as production metal. That filtered list becomes `intersectsProductionComponents`.
3. Sets `fused_into_metal = False` unconditionally, with an inline comment explaining why: the stone is never passed to `_fuse_metal()`, so this is verified structurally (by the shape of the code, not by a geometric check), not merely inferred from the intersection volume being zero or non-zero.
4. Returns `StoneMetalSeparationResult(stoneReferenceExists=True, productionIncluded=False, intersectsProductionComponents=[...], fusedIntoProductionMetal=False, status="PASS", note="StoneReference intersecting a production component ... is an expected reference relationship, never evidence that its geometry was fused into production metal.")`.

## `StoneMetalSeparationResult` field meanings

| Field | Meaning |
|---|---|
| `stoneReferenceExists` | Whether `stone_reference` produced at least one solid. |
| `productionIncluded` | Always `False` in the current architecture — the stone is never part of `combined_metal`. |
| `intersectsProductionComponents` | Names of production components whose real intersection with `stone_reference` was `INTERSECTS` (positive boolean-common volume). |
| `fusedIntoProductionMetal` | Always `False` today — see "Why this is always `False`" below. |
| `status` | `PASS` when the stone exists (regardless of intersection); `FAIL` when it does not exist at all. |
| `note` | The exact clarifying sentence quoted above. |

## The real finding for the default solitaire

Running the real pipeline against the default definition (verified directly, not assumed):

```
stone_reference vs band            NO_INTERSECTION  0.0 mm3
stone_reference vs prongs          INTERSECTS        2.1008137959215842 mm3
stone_reference vs basket_support  INTERSECTS        3.6189901204267514 mm3
```

So `intersectsProductionComponents == ["prongs", "basket_support"]`, `fusedIntoProductionMetal == False`, `status == "PASS"`. Both intersections are real, positive-volume, `INTERSECTS`-status boolean-common results — not `TOUCHES`, not a zero-volume tangency — and both are the expected consequence of `EMBED_MM`-driven grip geometry, exactly as `_stone_metal_separation()`'s own note states.

## Why `fusedIntoProductionMetal` is always `False` today

This is a real, honest, deliberate simplicity finding, not a placeholder or an unfinished check. There is currently no code path in `backend/jewelmind/geometry/` that could ever produce a stone solid that has actually been unioned into `combined_metal` — `_fuse_metal()`'s signature (`band`, `prongs`, `basket`) makes it structurally impossible, the same way `143-stone-metal-separation-contract.md` already describes for the construction side. Consequently `StoneMetalSeparationResult.fusedIntoProductionMetal` cannot currently be assigned `True` by any input; the field exists so that if a future geometry change ever introduced a path where the stone *could* reach a fuse call, the inspection layer would already have a place to report `True` rather than requiring a schema change at that point. It is not doing continuous verification against a scenario that could occur — it is reporting a fact that is currently invariant by construction.

## Relationship to the Sprint 5 contract

`07-atlas/143-stone-metal-separation-contract.md` names one real gap: no runtime or test-time check historically confirmed zero geometric intersection volume between `stone_reference` and `combined_metal` (only a bounding-box separation check existed, `ATLAS-GAP-006`). This Sprint's `inspect_intersection()` (see [`471-component-intersection-model.md`](471-component-intersection-model.md)) is real intersection-volume measurement between `stone_reference` and each production component individually — but that measurement's *purpose*, per `_stone_metal_separation()`'s own note, is never to flag those individual intersections as violations; only Forge could ever make that judgment, and no Forge rule currently reads this fact (`forgeConsumptionStatus: "not_consumed"` for `STONE_METAL_SEPARATE` in `specs/geometry-inspection/v2/fact-registry.json`). `ATLAS-GAP-006` itself is not closed by this Sprint — it was about `combined_metal` (the fused compound) vs. `stone_reference`, and this Sprint measures `stone_reference` against each production component separately, which is a related but not identical measurement.

## Tests

`backend/tests/test_geometry_inspection.py::TestStoneReferenceRole` (3 tests): `test_stone_reference_is_counted_as_the_only_reference_component`, `test_stone_metal_separation_reports_stone_exists_and_is_not_fused`, and `test_stone_intersecting_prongs_is_expected_not_a_fusion_signal` — the last one exists specifically to assert `"prongs" in separation.intersectsProductionComponents` alongside `separation.fusedIntoProductionMetal is False` in the same test, so the two facts can never silently drift apart. `TestStoneExportSeparation::test_stone_reference_is_excluded_from_combined_metal` covers the export-time half of the same guarantee at the `GeneratedModel.combined_metal` level.

## Cross-references

- LAW-006 — `docs/bible/00-foundation/004-jewelmind-constitution.md`.
- [`07-atlas/143-stone-metal-separation-contract.md`](../07-atlas/143-stone-metal-separation-contract.md) — the construction-time contract this document restates at the inspection layer.
- [`471-component-intersection-model.md`](471-component-intersection-model.md) — the underlying pairwise intersection mechanism.
- [`480-assembly-graph-model.md`](480-assembly-graph-model.md) — `fullAssemblyConnectivity` includes `stone_reference`; `productionConnectivity` does not.
- [`487-forge-fact-contract.md`](487-forge-fact-contract.md) — why `STONE_METAL_SEPARATE` is not yet consumed by any Forge rule.
