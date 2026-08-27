---
id: JM-BIBLE-STONE-README
title: Stone System v1 — Index
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-040
  - JM-BIBLE-120
  - JM-BIBLE-RING-README
  - JM-BIBLE-SHANK-README
related_documents:
  - JM-BIBLE-README
  - JM-BIBLE-046
  - JM-BIBLE-529
implementation_status: current
professional_validation: not_required
normative: false
---

# Stone System v1 — Index

This is **Sprint 18** of the Technical Bible: **Stone System v1** — the second consecutive REAL GEOMETRY milestone. Before this Sprint, `StoneReference` was a single round-only builder with `stone.diameter`/`stone.depth` hardcoded into geometry, Forge rules, Studio, and Designer. This Sprint generalizes it into a reusable, **category-neutral** Stone System with 7 genuinely-generating shapes.

**Read this README, then [`560-stone-governance.md`](560-stone-governance.md), before changing anything in `backend/jewelmind/geometry/stone/`, `backend/jewelmind/domain/stone_dimensions.py`, or `domain/schema.py::StoneSpec`.**

## The fundamental rule

> Stone System is SHARED jewelry infrastructure. Ring may position a stone; Setting may interact with a stone; Vision may render a stone; Forge may evaluate rules involving stone facts. **None of those systems owns `StoneDefinition`.**

```
JewelryDefinition
  ├── CategoryDefinition          (Sprint 16 — ring: CURRENT)
  ├── StoneArrangement            (Sprint 16 — SINGLE_CENTER: CURRENT)
  │     └── StoneDefinition       ← THIS SPRINT, category-neutral
  │           ├── Shape           (7 shapes, all CURRENT)
  │           ├── Dimensions      (LENGTH / WIDTH / DEPTH, resolved per shape)
  │           ├── Orientation     (degrees, own local vertical axis)
  │           └── ReferenceGeometryProfile  (software_reference_profile)
  ├── SettingSystem               (Sprint 19 — PLANNED)
  ├── Material
  └── Manufacturing
```

`jewelmind.geometry.stone` and `jewelmind.domain.stone_dimensions` **never import `jewelmind.ring`** (STONE-GOV-001) — proven by AST inspection in [`backend/tests/test_stone_system_no_ring_dependency.py`](../../../backend/tests/test_stone_system_no_ring_dependency.py), not merely asserted.

## STONE_REFERENCE is not a gemstone model

A `StoneReference` is deterministic geometric reference suitable for CAD construction, layout, setting construction, component relationships, clearance/intersection analysis, Vision, and technical communication. It may approximate a table/crown region, a girdle, a pavilion/depth, and an outline. It **never** guarantees an exact facet pattern, optical behavior, commercial cutting proportions, gemological certification, or vendor dimensions (STONE-GOV-011). A richer `FACETED_GEM_MODEL` layer, and a future `MEASURED_STONE` (supplier/scan/imported) mode, are separate future concerns — documented in [`567-stone-reference-geometry-contract.md`](567-stone-reference-geometry-contract.md), deliberately not implemented.

## What changed vs. what didn't

**Changed (real geometry):** `domain/schema.py::StoneSpec` gained 6 new `shape` enum members plus `length`/`width`/`orientation` — an additive, backward-compatible MINOR JDL change (`schemaVersion` stays `"0.1.0"`). A new `geometry/stone/` package (`outline`, `builder`, `capability`, `errors`) builds real, deterministic 3-level crown/girdle/pavilion lofts for `oval`, `pear`, `emerald`, `cushion`, `princess`, and `marquise`. `domain/stone_dimensions.py` resolves the public per-shape fields into one canonical LENGTH/WIDTH/DEPTH contract. Geometry Inspection gained 6 real `STONE_REQUESTED_*`/`STONE_MEASURED_*` fact types. Studio gained a capability-driven shape selector; Designer gained IT/EN shape normalization for all 7 shapes.

**Unchanged (by design, verified by the Golden Suite):** Every `round` configuration uses the byte-identical pre-Sprint-18 construction — **zero baseline updates** across all 12 pre-existing Golden cases. The `stone_reference` component name, its exclusion from default production exports (LAW-006), Ring Architecture v2, and the Shank System are all untouched.

## Generation capability is NOT setting compatibility

Only `round` has `currentSettingCompatibility: SUPPORTED`. All 6 new shapes are honestly `EXPERIMENTAL` (STONE-GOV-009): they generate real CAD geometry, but the current prong layout is a **generic, provisional circular placement**, not shape-optimized. A shape generating correctly is never a claim that its setting is professionally valid. Shape-aware setting geometry is Sprint 19's Setting System.

## No fake equivalent diameter

An `oval 8 × 6` is never collapsed into `diameter = 7` for rule compatibility (brief section 44). `JM-STONE-001` and `JM-PRONG-003` are explicitly scoped **ROUND_ONLY**; `JM-STONE-002` was genuinely generalized to the stone's real minimum horizontal extent. **Zero** fake equivalent-diameter mappings exist. See [`578-current-code-mapping-and-gaps.md`](578-current-code-mapping-and-gaps.md).

## Reading order

1. [`560-stone-governance.md`](560-stone-governance.md) — the 16 STONE-GOV-* rules.
2. [`561-stone-architecture-overview.md`](561-stone-architecture-overview.md), [`562-stone-domain-model.md`](562-stone-domain-model.md), [`563-stone-shape-model.md`](563-stone-shape-model.md).
3. Dimensions and coordinates: [`564-stone-dimension-model.md`](564-stone-dimension-model.md), [`565-stone-coordinate-and-orientation.md`](565-stone-coordinate-and-orientation.md).
4. Geometry contracts: [`566-stone-outline-contract.md`](566-stone-outline-contract.md), [`567-stone-reference-geometry-contract.md`](567-stone-reference-geometry-contract.md).
5. Per-shape-family contracts: [`568-round-stone-contract.md`](568-round-stone-contract.md), [`569-elongated-stone-contract.md`](569-elongated-stone-contract.md), [`570-angular-stone-contract.md`](570-angular-stone-contract.md), [`571-asymmetric-stone-contract.md`](571-asymmetric-stone-contract.md).
6. Generation and integration: [`572-stone-generation-pipeline.md`](572-stone-generation-pipeline.md), [`573-stone-setting-interface.md`](573-stone-setting-interface.md).
7. Cross-system boundaries: [`574-stone-inspection-contract.md`](574-stone-inspection-contract.md), [`575-stone-capability-model.md`](575-stone-capability-model.md), [`577-stone-golden-strategy.md`](577-stone-golden-strategy.md).
8. Migration and gaps: [`576-current-round-migration.md`](576-current-round-migration.md), [`578-current-code-mapping-and-gaps.md`](578-current-code-mapping-and-gaps.md), [`579-open-stone-questions.md`](579-open-stone-questions.md).

## Appendices

[`stone-shape-catalog.md`](../appendices/stone-shape-catalog.md), [`stone-capability-catalog.md`](../appendices/stone-capability-catalog.md), [`stone-test-matrix.md`](../appendices/stone-test-matrix.md).

## Machine-readable specification

[`specs/stone/v1/`](../../../specs/stone/v1/README.md) — 5 JSON Schemas, a real `shape-registry.json` generated from `geometry/stone/capability.py`, 7 examples (one per shape), and 5 test-vector files, all produced by running the real code.

## The single most important finding of this Sprint

**A 3-level loft over a shared outline primitive generalizes to all 7 shapes without a single per-shape special case in the builder body.** The riskiest assumption going in was that pointed shapes (marquise, pear) would need numerical stabilization — a microscopic tip blunting the brief explicitly pre-authorized. Real experiments showed none was needed: both build valid single solids, survive a STEP roundtrip, and rotate cleanly. What *did* require real correction was mundane and API-level, not geometric: `Workplane.val()` returns an `Edge` rather than a `Wire` unless `.close()` is called, and cushion's first two corner-arc formulations failed outright in OpenCascade before the `k = cr·cos(45°)` construction worked. See [`572-stone-generation-pipeline.md`](572-stone-generation-pipeline.md).

## What was investigated, not invented

Every shape's construction was prototyped against the real installed CadQuery 2.8.0 before being written into the package — including STEP roundtrip and 90° rotation checks for the two pointed shapes. A real circular import was found and fixed during implementation (`geometry/constants.py` needs `resolved_width_mm`, while `geometry/stone/builder.py` needs `band_top_z` from `geometry/constants.py`), resolved by making `geometry/stone/__init__.py` deliberately non-eager and verified from 6 independent fresh-process import entry points. The `definitionHash` drift caused by the additive `StoneSpec` fields was investigated, confirmed not to affect Golden regression detection, and documented explicitly rather than silently absorbed.

## Validation of this sprint

See [`SPRINT-18-VALIDATION-REPORT.md`](SPRINT-18-VALIDATION-REPORT.md) for the checks run against this section and the findings from that pass.
