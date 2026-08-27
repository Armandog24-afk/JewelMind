---
id: JM-BIBLE-577
title: Stone Golden Strategy
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-STONE-README
  - JM-BIBLE-560
related_documents:
  - JM-BIBLE-QUALITY-README
  - JM-BIBLE-514
  - JM-BIBLE-574
implementation_status: current
professional_validation: not_required
normative: true
---

# Stone Golden Strategy

## Zero regression for the 12 pre-existing cases

`goldens/solitaire-v1/manifest.json` held 12 cases before this Sprint (9 from Sprint 15, 3 from Sprint 17). **All 12 required zero baseline updates.**

This is the primary regression guarantee, and it is stronger than it looks. Nine of the twelve (`SOL-001`–`SOL-009`) contain round stones across several real dimension combinations — including `SOL-007-stone-dimension-variation`, which exists specifically to vary stone geometry. That the entire set verified unchanged is real evidence that `_build_round_stone()` is byte-identical, not merely approximately equal (STONE-GOV-016).

No baseline was regenerated to make anything pass. Per QUALITY-GOV-003/004 the only path to changing an accepted `snapshot.json` is the explicit `geometry-quality accept --reason "..."` CLI command, and it was not used this Sprint.

## The 6 new cases

One per new shape (STONE-GOV-015 — a new shape gets its **own new** case, never a retrofit of an existing one):

| Golden ID | Shape | Dimensions (mm) |
|---|---|---|
| `SOL-013-oval-solitaire` | `oval` | 8.0 × 6.0 |
| `SOL-014-pear-solitaire` | `pear` | 9.0 × 6.0 |
| `SOL-015-emerald-solitaire` | `emerald` | 8.0 × 6.0 |
| `SOL-016-cushion-solitaire` | `cushion` | 7.0 × 7.0 |
| `SOL-017-princess-solitaire` | `princess` | 6.5 × 6.5 |
| `SOL-018-marquise-solitaire` | `marquise` | 10.0 × 5.0 |

All at `depth = 4.0`, `baselineStatus: STABLE`, on the default ring/band/setting so the stone is the only variable.

The dimensions are deliberately not uniform. Each is chosen to exercise something real about its shape: `marquise` at 10 × 5 is strongly elongated (2:1), where a pointed lens is most likely to misbehave; `pear` at 9 × 6 gives the asymmetry room to be measurable; `cushion` and `princess` are square, since equal half-extents make `min(hw, hl)` — the basis of both corner ratios — degenerate in the most demanding way; `oval` and `emerald` at 8 × 6 give a moderate 4:3 baseline.

Each case's `knownLimitations` records the honest setting caveat:

> *"Prong setting compatibility for this shape is EXPERIMENTAL — the current prong layout is a generic, provisional circular placement, not shape-optimized. See docs/bible/20-stone/README.md and geometry/stone/capability.py."*

which is why all six verify as `PASS_WITH_KNOWN_LIMITATIONS` rather than plain `PASS`. That status is the correct one: the geometry is a valid, accepted baseline, and the recorded limitation is real.

## `fullSuite` only, not `fastSuite`

The 6 new cases were appended to `goldenIds` and `fullSuite`. `fastSuite` is unchanged and still contains exactly `SOL-001`, `SOL-002`, `SOL-003`.

`fastSuite` exists as a quick pre-commit signal, and its value depends on staying fast. Its three cases already cover the shared pipeline — band, prongs, basket, metal fuse, round stone — so a new stone shape adds no new *pipeline* coverage there, only more geometry to build. The shapes' real protection comes from `fullSuite`, which runs in CI. Same reasoning Sprint 17 applied to its three taper cases.

## What the Golden facts protect

Each snapshot captures, per component, the facts `geometry_quality/snapshot.py` already recorded — no new snapshot fields were needed for stones:

| Fact | What a change in it would mean for a stone |
|---|---|
| Component presence and identity | `stone_reference` silently vanished, or was renamed. |
| Solid count | An outline change produced a multi-solid or empty result. |
| Volume | Any outline, corner-ratio, or crown/pavilion-proportion drift. |
| Bounding box | Accidental scaling, an axis swap, or an orientation regression. |
| `designConsistency.stoneReferenceIsProductionMetal` | The StoneReference was fused into metal — an exact invariant (QUALITY-GOV-013). |
| Artifact expectations | STEP/STL export stopped producing valid output for this shape. |

The combination is what makes it discriminating. Volume alone would not catch an axis swap (a 9 × 5 oval and a 5 × 9 oval have identical volume); the bounding box catches that. The bounding box alone would not catch a corner-ratio change (an emerald's clip does not alter its extents); volume catches that.

Two things the Golden Suite deliberately does **not** rely on:

- **STEP byte equality.** CadQuery's STEP writer embeds variable OpenCascade metadata, so two exports of identical geometry are not byte-identical (QUALITY-GOV-007/008). Artifact checks re-import and compare geometric facts.
- **Screenshots.** Visual comparison is not part of Golden verification. Shape regressions are caught numerically.

Not captured, and worth stating: the snapshot does not record a stone's **centroid offset**, so a shape silently symmetrized while preserving volume and extents would not be caught by the Golden Suite alone. That specific invariant is covered instead by `test_stone.py::TestPearAsymmetry` — see [`571-asymmetric-stone-contract.md`](571-asymmetric-stone-contract.md). Golden coverage and unit coverage are complementary here, not redundant.

## Assembly-level, not stone-only

Every new case is a **complete solitaire**, not an isolated stone solid. Each therefore also exercises positioning against the girdle-plane anchor, the prong and basket build against `resolved_width_mm`, the metal fuse, connectivity inspection, and STEP/STL export — the integration the brief required (section 47), well beyond the minimum of oval plus one angular shape.

## Verification

All 18 cases were independently reverified against their own saved baselines with `verify_golden(golden_id, check_artifacts=True)` immediately after generation, in a separate pass from the pass that wrote them:

```
SOL-001 … SOL-008: PASS
SOL-009 … SOL-018: PASS_WITH_KNOWN_LIMITATIONS
All 12 golden(s) PASS → later: All 18 golden(s) PASS
```

`backend/tests/test_geometry_quality_*.py` (49 tests) passes with the expanded suite. Baselines were generated by a one-off script run once against live code and then deleted — never hand-authored (QUALITY-GOV / brief section 46: *"Do not manually invent snapshot numbers"*).

Every new case is recorded in [`../appendices/golden-update-register.md`](../appendices/golden-update-register.md) as `INITIAL_BASELINE`, per QUALITY-GOV-018.

## Golden status is not professional approval

`baselineStatus: STABLE` means one thing: *this geometry was generated from real code, independently reverified, and is now the reference for detecting unintended change.* It carries no professional, manufacturing, or gemological endorsement — see [`../17-geometry-quality/514-professional-validation-boundary.md`](../17-geometry-quality/514-professional-validation-boundary.md).

For the six new shapes this distinction is especially load-bearing: each has a `STABLE` baseline **and** an `EXPERIMENTAL` setting compatibility at the same time, and those are not in conflict. The baseline says the geometry is reproducible; the compatibility field says the setting around it is provisional. The active professional-validation registry remains at **zero records**.

## Adding a Golden case for a future shape

1. Generate the case from live code with a one-off script; delete the script afterward.
2. Include an honest `knownLimitations` entry if the shape's setting compatibility is not `SUPPORTED`.
3. Append to `goldenIds` and `fullSuite`; leave `fastSuite` alone unless the case covers a genuinely new pipeline path.
4. Reverify **all** cases with `check_artifacts=True` in a separate pass.
5. Record an `INITIAL_BASELINE` row in the golden update register.
6. Never modify an existing case to accommodate the new shape.
