---
id: JM-BIBLE-585
title: Prong Setting Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-27
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-SETTING-README
  - JM-BIBLE-580
related_documents:
  - JM-BIBLE-586
  - JM-BIBLE-589
implementation_status: current
professional_validation: not_required
normative: true
---

# Prong Setting Contract

## Status

| Property | Value |
|---|---|
| Family | `prong` |
| Implementation status | `CURRENT` |
| Stone shapes `SUPPORTED_SOFTWARE` | `round` |
| Stone shapes `EXPERIMENTAL` | `oval`, `pear`, `emerald`, `cushion`, `princess`, `marquise` |
| Prong counts | 4 and 6 |
| Styles | `ROUND_PRONG` only |
| Seat / bearing / cutter | `PLANNED` — none exists |
| Professional validation | `NOT_REVIEWED` |

## Parameters

`ProngSettingDefinition` (`setting/models.py`):

| Field | Source |
|---|---|
| `prongCount` | JDL `setting.prongCount` |
| `prongDiameterMm` | JDL `setting.prongDiameter` |
| `prongHeightMm` | JDL `setting.prongHeight` |
| `placementStrategy` | **Not** from JDL — resolved from the stone's real symmetry by `placement.py::resolve_strategy()` |
| `style` | `ROUND_PRONG`; internal |

`placementStrategy` being resolved rather than requested is deliberate. A caller asking for `RADIAL` placement on a marquise would be asking for the old wrong behaviour; the strategy is a consequence of the stone, not a user preference. (The generator still accepts an explicit override, which is what lets tests compare the two strategies directly on the same stone.)

## Construction

```python
prong_r = prong.prongDiameterMm / 2
base_z  = attachment.attachmentPlaneZMm - attachment.embedMm
height  = prong.prongHeightMm + attachment.embedMm

positions, strategy = prong_positions(stone, generated_count, prong_r, prong.placementStrategy)

for x, y in positions:
    cq.Workplane("XY").workplane(offset=base_z).center(x, y).circle(prong_r).extrude(height)
```

Plain vertical cylinders, embedded past the attachment plane so the boolean union produces genuine overlap. Character-for-character the pre-Sprint-19 construction — only where the positions come from changed.

## Prong count

`SUPPORTED_PRONG_COUNTS = (4, 6)`, matching the real Forge rule `JM-PRONG-001`, which is the authority. `test_setting.py` keeps the two in sync.

An unsupported requested count is **not** silently corrected. The generator builds `max(requested, 0)` prongs, records a real warning, and reports both counts:

- `metadata["requestedCount"]` / `["generatedCount"]`
- `SettingGeometryResult.requestedProngCount` / `.generatedProngCount`
- the `SETTING_REQUESTED_PRONG_COUNT` / `SETTING_GENERATED_PRONG_COUNT` inspection facts

Geometry generation is expected to be blocked upstream by the validation error in that case; the generator stays honest about what it was asked to build (SETTING-GOV-009).

## Component identity

Prongs remain **one compound named `prongs`**, unchanged.

Brief section 14 asked for stable individual identities (`prong_0`, `prong_1`, …) *"if current architecture stores all prongs as one compound: perform only the smallest safe refactor necessary."* Splitting them was assessed and rejected as far exceeding that bound: it would change `GEOMETRY_ROLE`/`PRODUCTION_ROLE`, every preview manifest, every export component list, the connectivity graph's node set, and all 23 Golden baselines.

What inspection actually needs — comparing requested against generated count, and knowing where each prong is — is provided as real facts instead: the count pair above, plus `metadata["positions"]` carrying every prong's `(x, y)`. This is recorded as an accepted design decision rather than an unmet requirement; see [`code-mapping-and-gaps.md`](code-mapping-and-gaps.md).

## Styles

Only `ROUND_PRONG` (a cylinder) is implemented, and `ProngStyle` is a single-member literal.

`CLAW`, `V_PRONG`, `SHARED_PRONG` and `CUSTOM_PRONG` are named in the capability architecture but are **not** enum members and have no geometry. `V_PRONG` matters most: it is what real pear and marquise tip protection requires, and its absence is exactly why those shapes are `EXPERIMENTAL` rather than supported. Advanced styles are Sprint 23 territory.

## Backward compatibility

`SETTING-GOV-017`, verified two ways:

- `test_setting.py::TestRoundProngBackwardCompatibility` asserts `combined_metal_volume_mm3 == 341.44334316909976` and prong volume `== 29.650351464580467` — exact equality, not approximate.
- All 12 round-stone Golden cases (`SOL-001`–`SOL-012`) verified with **zero** baseline updates.

A third test guards against future drift: `geometry/constants.py::prong_center_radius()` is still used by the basket builder, and the Setting System computes the same radius independently. `test_radial_placement_matches_the_legacy_prong_center_radius_helper` asserts the two agree to `rel=1e-12`, so they cannot silently diverge.

Legacy metadata keys (`requestedCount`, `generatedCount`, `prongRadiusMm`, `centerRadiusMm`, `positions`) are all preserved. `centerRadiusMm` is now `None` for `OUTLINE_CARDINAL` placement, honestly — under that strategy the prongs do not lie on a single circle, so reporting one would be false.

## Forge rules

All four prong rules are `PRONG_ONLY` as of this Sprint (`validation/engine.py::_prong_rules` returns early unless `setting.type == "prong"`):

| Rule | Scope |
|---|---|
| `JM-PRONG-001` (count is 4 or 6) | PRONG_ONLY |
| `JM-PRONG-002` (diameter minimum) | PRONG_ONLY |
| `JM-PRONG-003` (count vs stone size) | PRONG_ONLY **and** ROUND_ONLY (Sprint 18) |
| `JM-PRONG-004` (height vs basket height) | PRONG_ONLY |

Before this change, a valid bezel would have been blocked on `setting.prongCount` — the mis-scoping brief section 32 calls out. Mirrored identically in `shared/validation/engine.ts` (FORGE-GOV-004).

## Not a professional claim

Cylindrical prongs at provisional positions, with no seat, no bearing, and no finishing. `professionalValidationStatus` is `NOT_REVIEWED` and every non-round combination is `EXPERIMENTAL`. See [`prong-placement-model.md`](prong-placement-model.md) for exactly what the placement does and does not claim.
