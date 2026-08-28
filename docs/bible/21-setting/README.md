---
id: JM-BIBLE-SETTING-README
title: Setting System v1 — Index
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-27
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-120
  - JM-BIBLE-RING-README
  - JM-BIBLE-STONE-README
related_documents:
  - JM-BIBLE-README
  - JM-BIBLE-573
  - JM-BIBLE-528
implementation_status: current
professional_validation: not_required
normative: false
---

# Setting System v1 — Index

This is **Sprint 19** of the Technical Bible: **Setting System v1**. Before this Sprint, "the setting" was whatever `geometry/components/prongs.py` happened to do — a single prong builder that read ring fields directly, computed placement from `stone.diameter`, and defined by accident what every future setting would have to look like. This Sprint extracts it into a **category-neutral Setting System** and adds a second, genuinely different family: a real parametric bezel.

**Read this README, then [`setting-governance.md`](setting-governance.md), before changing anything in `backend/jewelmind/setting/`, `backend/jewelmind/geometry/setting_adapter.py`, or `domain/schema.py::SettingSpec`.**

## The fundamental rule

> A Setting defines how metal geometry interacts with one or more stones. A RingHead defines how a setting is structurally incorporated into a ring. **Setting System must not import Ring architecture.**

```
Stone System            (Sprint 18 — category-neutral)
      ↓  StoneSettingReference
Setting System          (THIS SPRINT — category-neutral)
      ↓  SettingAttachmentInterface
Category integration    (RingHead today; PendantBody / EarringBody later)
      ↓
Jewelry assembly
```

The dependency arrow is one-way and enforced:

```
Ring/assembly → geometry/setting_adapter.py → jewelmind.setting → Stone contracts
```

`jewelmind.setting` never imports `jewelmind.ring`, `jewelmind.jewelry_category`, the Shank subsystem, or even `JewelryDefinition` — the last of those would smuggle the whole ring domain across the boundary in one import. Proven by AST inspection in [`backend/tests/test_setting_system_no_ring_dependency.py`](../../../backend/tests/test_setting_system_no_ring_dependency.py) (13 tests), which also asserts the *reverse* direction is real so the arrow is documented both ways.

## What changed vs. what didn't

**Changed (real geometry and real architecture):** a new `backend/jewelmind/setting/` package (models, capability, stone_interface, placement, prong, bezel, dispatch, errors). Prong placement is now **shape-aware**: `RADIAL` for a radially symmetric stone, `OUTLINE_CARDINAL` — sampled from the stone's own girdle outline — for every other shape. A **real parametric bezel** is built by offsetting the stone's own outline, and all 7 current stone shapes produce a valid single-solid bezel. `SettingSpec` gains the `bezel` enum member plus two optional bezel fields as an additive MINOR JDL change. 8 new Setting inspection facts. Studio gains a capability-driven setting selector; Designer gains IT/EN setting normalization.

**Unchanged (verified):** every round 4/6-prong configuration is byte-identical to pre-Sprint-19 — `combined_metal_volume_mm3 == 341.44334316909976` exactly, and all 12 round-stone Golden cases required **zero** baseline updates. The `prongs` component name, its production role, `stone_reference`'s exclusion from default exports, and the Shank and Stone subsystems are untouched.

## Generation capability is NOT professional validation

Every Setting family is `generatable: true` **and** `professionalValidationStatus: "NOT_REVIEWED"` at the same time (SETTING-GOV-007). Those axes are independent, and **no Setting geometry in this repository has been reviewed by a qualified human.**

Likewise `seatSupport`, `bearingSupport`, and `cutterSupport` are **`PLANNED` for every family**. No seat, bearing, or cutter geometry exists. Stone/metal overlap is *not* a seat and must never be renamed as one — see [`setting-inspection-contract.md`](setting-inspection-contract.md).

## Shape-aware, not professionally correct

The placement change is a measurable software improvement, not a claim of correctness. For an 8 × 6 oval, off-axis prongs sat **0.784 mm away** from the stone outline under the old radial placement — floating, not gripping — and sit **0.049 mm** from it now, while the on-axis prong is unchanged at the intended girdle inset.

But every non-round combination is honestly `EXPERIMENTAL`: the layout still does not cluster prongs at a marquise's tips, protect a pear's tip, or align to an angular stone's corners, and real `V_PRONG` geometry does not exist. See [`prong-placement-model.md`](prong-placement-model.md).

## Reading order

1. [`setting-governance.md`](setting-governance.md) — the 18 SETTING-GOV-* rules.
2. [`setting-architecture.md`](setting-architecture.md), [`setting-domain-model.md`](setting-domain-model.md).
3. Interfaces: [`stone-setting-interface.md`](stone-setting-interface.md), [`setting-attachment-interface.md`](setting-attachment-interface.md).
4. Families: [`prong-setting-contract.md`](prong-setting-contract.md), [`prong-placement-model.md`](prong-placement-model.md), [`bezel-setting-contract.md`](bezel-setting-contract.md).
5. Cross-system: [`setting-inspection-contract.md`](setting-inspection-contract.md), [`setting-capability-model.md`](setting-capability-model.md), [`setting-golden-strategy.md`](setting-golden-strategy.md).
6. Migration and gaps: [`current-prong-migration.md`](current-prong-migration.md), [`code-mapping-and-gaps.md`](code-mapping-and-gaps.md).

## Machine-readable specification

[`specs/setting/v1/`](../../../specs/setting/v1/README.md) — 7 JSON Schemas, a generated `setting-registry.json` (capabilities + reserved families + the full Stone × Setting matrix), 5 examples, 5 test-vector files. Plus the cross-product **Capability Coverage Guard** at [`specs/capabilities/`](../../../specs/capabilities/jewelmind-capabilities.json) — 101 capabilities across 26 domains, validated by [`backend/tests/test_capability_coverage.py`](../../../backend/tests/test_capability_coverage.py).

## The single most important finding of this Sprint

**A true geometric offset of an ellipse does not survive STEP export, and the fix had to be triggered by curve type rather than shape name.** `cq.Wire.offset2D()` on an ellipse produces edges whose `geomType()` is `OFFSET`; extruding that surface writes a STEP file that re-imports as a `Shell` with **zero solids** — silently breaking Foundry for exactly one stone shape. Every other shape offsets to `CIRCLE`/`LINE` edges and round-trips exactly.

Hardcoding `if shape == "oval"` would have worked and would have been wrong: it would have re-introduced the per-shape branching brief section 19 exists to prevent, and would silently miss any future custom outline built from splines. The implemented trigger inspects the real edge `geomType()`, so it generalizes. Blanket resampling was also rejected — it measurably rounds the angular shapes' crisp corners.

## What was investigated, not invented

Four bezel construction strategies were prototyped against the real installed CadQuery 2.8.0 before any production code was written (annular-face extrusion, boolean cut, loft-between-copies, and expanded-semi-axes), and the STEP round-trip was tested on the bare wall *and* on the realistically fused metal body — which is what surfaced the ellipse problem, since a bare-shape test alone would have been ambiguous. The rejected approaches and the measured deviations are recorded in [`bezel-setting-contract.md`](bezel-setting-contract.md).

Three genuine architectural leaks were found and fixed by inspecting real inspection output rather than by reading code: `REQUIRED_COMPONENT_NAMES` hardcoded `prongs` (so every valid bezel assembly inspected as `FAIL`), prong count was reported as `FAIL` rather than `NOT_APPLICABLE` for a bezel, and pairwise intersection inspection was driven by a hardcoded 4-name tuple that silently skipped the `bezel` component entirely.

## Validation of this sprint

See [`SPRINT-19-VALIDATION-REPORT.md`](SPRINT-19-VALIDATION-REPORT.md).
