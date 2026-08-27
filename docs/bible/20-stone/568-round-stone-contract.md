---
id: JM-BIBLE-568
title: Round Stone Contract
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
  - JM-BIBLE-567
  - JM-BIBLE-576
  - JM-BIBLE-577
implementation_status: current
professional_validation: not_required
normative: true
---

# Round Stone Contract

## Status

| Property | Value |
|---|---|
| Symmetry class | `RADIAL` |
| Required dimensions | `diameter`, `depth` |
| Generation | CURRENT |
| Current setting compatibility | **`SUPPORTED`** — the only shape with this status |
| Reference geometry version | `1.0.0` |

Round is the shape the whole solitaire pipeline was originally designed around, and the only one whose prong setting placement is genuinely intended for it rather than provisional.

## The preserved construction

`_build_round_stone()` in `geometry/stone/builder.py` is the pre-Sprint-18 builder, moved but not modified:

```python
girdle_r   = definition.stone.diameter / 2
crown_h    = definition.stone.depth * _CROWN_FRACTION      # 0.35
pavilion_h = definition.stone.depth * _PAVILION_FRACTION   # 0.65
table_r    = girdle_r * _TABLE_TO_GIRDLE_RATIO             # 0.56
girdle_z   = band_top_z(definition) + definition.setting.basketHeight

solid = (
    cq.Workplane("XY")
    .workplane(offset=girdle_z - pavilion_h)
    .circle(_CULET_RADIUS_MM)          # 0.05 mm, absolute
    .workplane(offset=pavilion_h)
    .circle(girdle_r)
    .workplane(offset=crown_h)
    .circle(table_r)
    .loft(ruled=True)
)
```

Note that this is the **fluent** `Workplane.loft()` form, not the `cq.Solid.makeLoft()` form the non-round path uses. That difference is intentional and is the point of the whole contract: the fluent chain is the exact code that produced every pre-Sprint-18 Golden baseline, character for character.

## Why round was deliberately not refactored

The obvious tidy-up would have been to route round through `_build_non_round_stone()` with a `round_outline` — the outline function exists, the loft is the same three levels, and it would have removed a branch.

It was not done, on purpose (STONE-GOV-016):

1. **Byte-identical output is the guarantee.** `cq.Solid.makeLoft()` over three separately-translated wires is not provably bit-identical to a fluent `.workplane(offset=…).circle()` chain: the wire construction order, the workplane transforms, and the internal OCC section ordering all differ. Even a difference in the last floating-point digit would have shown up as a Golden diff across 12 existing cases.
2. **The absolute culet does not translate.** Round uses `_CULET_RADIUS_MM = 0.05` — a fixed 0.05 mm circle regardless of stone size. The non-round path uses `_CULET_SCALE_RATIO = 0.05` — a proportional 5% outline. For a 6.5 mm round stone these give different culets (0.05 mm vs 0.1625 mm), so routing round through the shared path would have changed its geometry outright.
3. **Code aesthetics is not a reason to move geometry.** This is the same discipline Sprint 17 applied to the uniform shank: *"Do not alter round geometry merely to harmonize code aesthetics."*

The cost is one extra branch and one small duplicated constant set. The benefit is a provable zero-regression guarantee. That trade is correct.

## Verified backward compatibility

Two independent proofs, both real:

**1. The exact recorded volume.** `test_stone.py::TestRoundStoneBackwardCompatibility::test_default_definition_produces_the_pre_sprint18_recorded_volume` asserts:

```python
assert stone.volume_mm3 == pytest.approx(58.22141924499569, rel=1e-9)
```

That figure is the pre-Sprint-18 value, matching `SOL-001-default-solitaire`'s stored `stone_reference` volume exactly.

**2. Zero Golden baseline updates.** All 12 pre-existing Golden cases (`SOL-001` through `SOL-012`) verify `PASS`/`PASS_WITH_KNOWN_LIMITATIONS` with **no** baseline changes. Since 9 of those cases (`SOL-001`–`SOL-009`) contain round stones, and one (`SOL-007`) is specifically a stone-dimension variation, this exercises round geometry across several real dimension combinations, not just the default.

Additionally, `specs/stone/v1/test-vectors/backward-compatibility-vectors.json` records that a pre-Sprint-18-shaped document — `{"shape": "round", "diameter": 6.5, "depth": 4.0}`, with no `length`, `width`, or `orientation` — still validates and still produces that volume. It is re-verified live by `test_stone_schemas.py::test_backward_compatibility_vector_reproduces_the_pre_sprint18_volume`.

## Round-specific metadata

Round's generated component reports two fields no other shape does:

| Field | Why round only |
|---|---|
| `girdleRadiusMm` | A radially symmetric outline *has* one girdle radius. An oval has two semi-axes; an emerald's perimeter has clipped corners. There is no single honest radius for those. |
| `tableRadiusMm` | Same reasoning at the table level. |

Rather than invent an "equivalent radius" for non-round shapes, the fields are simply absent there — the same refusal that governs equivalent diameter (see [`578-current-code-mapping-and-gaps.md`](578-current-code-mapping-and-gaps.md)).

Round also reports `lengthMm == widthMm == diameter`, from the internal normalization in `domain/stone_dimensions.py`, so any consumer reading resolved dimensions works uniformly across shapes. Asserted by `TestRoundStoneBackwardCompatibility::test_round_stone_reports_length_equals_width_equals_diameter`.

## Orientation

`stone.orientation` is applied to round like every other shape, with no special case. Because round is `RADIAL`, rotating it about its own vertical axis is geometrically equivalent to not rotating it — verified by `TestStoneOrientation::test_round_orientation_does_not_change_volume_or_bounding_box` at 45°. At the default `0.0` the orientation code early-returns the shape unchanged, so the byte-identical guarantee is unaffected.

## Forge rules that are round-only because of this shape

Two real rules are scoped `ROUND_ONLY` precisely because their semantics were tuned for a diameter:

- `JM-STONE-001` (`STONE_DIAMETER_RANGE`, 2–15 mm) — round has a diameter; no other shape does.
- `JM-PRONG-003` (`PRONG_COUNT_VS_STONE_SIZE`, > 8 mm with 4 prongs → warning) — the threshold was chosen against a round stone's diameter, and generalizing it needs justification this Sprint does not provide.

Neither is evaluated against a substituted dimension for a non-round stone. See [`578-current-code-mapping-and-gaps.md`](578-current-code-mapping-and-gaps.md).

## Not a gemological claim

Round's construction is a three-level loft with a 0.56 table ratio and a 0.35/0.65 crown/pavilion split. A real round brilliant has 57–58 facets and quite different proportions. The name `round` denotes the *outline*, not a certified brilliant cut, and `isGemologicalReproduction` is `false` (STONE-GOV-011). This was already true before Sprint 18 and is unchanged.
