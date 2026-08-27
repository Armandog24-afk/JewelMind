---
id: JM-BIBLE-A06
title: "Appendix: Jewelry Domain Parameter Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on:
  - JM-BIBLE-052
related_documents:
  - JM-BIBLE-A05
  - JM-BIBLE-054
implementation_status: current
professional_validation: preliminary
---

# Appendix: Jewelry Domain Parameter Catalog

Every parameter in the current canonical schema
(`backend/jewelmind/domain/schema.py`, mirrored in
`shared/types/jewelry-definition.ts`). No default below is invented — all
are copied directly from the schema's `Field(default=...)` values.

| Canonical path | Type | Unit | Allowed values | Default | Direct/derived | Geometry influence | Validation influence | Current UI control | Professional-validation status |
|---|---|---|---|---|---|---|---|---|---|
| `project.name` | string | — | 1–200 chars | `"Solitaire Ring"` | direct | none | none | Text input (`project-name`) | not_required |
| `project.units` | string | — | fixed `"mm"` | `"mm"` | direct | implicit (all lengths are mm) | schema-level only | none (fixed) | not_required |
| `jewelry.category` | string | — | fixed `"ring"` | `"ring"` | direct | selects the assembly pipeline (implicitly, always solitaire) | none | none (fixed) | not_required |
| `jewelry.style` | string | — | fixed `"solitaire"` | `"solitaire"` | direct | same as above | none | none (fixed) | not_required |
| `ring.sizeSystem` | string | — | fixed `"EU"` | `"EU"` | direct | none | `JM-RING-003` (via `sizing.py`) | none (fixed) | preliminary |
| `ring.size` | float | dimensionless (size label) | `> 1` and `< 50` (business rule) | `16` | direct | none directly; cross-checked against `innerDiameter` | `JM-RING-002`, `JM-RING-003` | Numeric input (`ring-size`), step 0.5 | preliminary |
| `ring.innerDiameter` | float | mm | `> 10` and `< 30` (business rule) | `17.8` | direct | drives `inner_radius`/`outer_radius`/`band_top_z` | `JM-RING-001`, `JM-RING-003`, `JM-GEOMETRY-001` | Numeric input (`ring-inner-diameter`) | preliminary |
| `band.width` | float | mm | `≥ 1.5` (business rule) | `2.4` | direct | band cross-section (Y extent) | `JM-BAND-001`, `JM-BAND-003`, `JM-GEOMETRY-001`, `JM-MANUFACTURING-001` | Numeric input (`band-width`) | preliminary |
| `band.thickness` | float | mm | `≥ 1.4` (business rule) | `1.8` | direct | band cross-section (radial extent), `outer_radius` | `JM-BAND-002`, `JM-GEOMETRY-001`, `JM-MANUFACTURING-001` | Numeric input (`band-thickness`) | preliminary |
| `band.profile` | string | — | `"flat"` \| `"comfort_fit"` | `"comfort_fit"` | direct | selects cross-section construction path | none directly | Select (`band-profile`) | preliminary |
| `band.widthTaper.mode` | string | — | `"NONE"` \| `"TOWARD_BOTTOM"` | `"NONE"` | direct | selects uniform-revolve vs 48-section tapered-loft construction (Sprint 17) | none directly | none (no UI control this Sprint — API/JDL only) | preliminary |
| `band.widthTaper.bottomRatio` | float | dimensionless (ratio) | `> 0` and `≤ 1` (schema-level) | `1.0` | direct | multiplier applied to `band.width` at the bottom (`u=0.5`) when `mode="TOWARD_BOTTOM"` | none directly | none (no UI control this Sprint — API/JDL only) | preliminary |
| `band.thicknessTaper.mode` | string | — | `"NONE"` \| `"TOWARD_BOTTOM"` | `"NONE"` | direct | selects uniform-revolve vs 48-section tapered-loft construction (Sprint 17) | none directly | none (no UI control this Sprint — API/JDL only) | preliminary |
| `band.thicknessTaper.bottomRatio` | float | dimensionless (ratio) | `> 0` and `≤ 1` (schema-level) | `1.0` | direct | multiplier applied to `(outer_radius - inner_radius)` at the bottom (`u=0.5`) when `mode="TOWARD_BOTTOM"` | none directly | none (no UI control this Sprint — API/JDL only) | preliminary |
| `stone.shape` | string | — | `round` \| `oval` \| `pear` \| `emerald` \| `cushion` \| `princess` \| `marquise` | `"round"` | direct | selects the outline primitive for the shared 3-level loft (Sprint 18) | none directly | Select (`stone-shape`) | preliminary |
| `stone.diameter` | float \| null | mm | `2`–`15` (business rule, ROUND_ONLY) | `6.5` | direct | round's girdle radius; required only when `shape == "round"` | `JM-STONE-001` (ROUND_ONLY), `JM-PRONG-003` (ROUND_ONLY) | Numeric input (`stone-diameter`), shown for round only | preliminary |
| `stone.length` | float \| null | mm | no range rule yet (REQUIRES_RULE_EVOLUTION) | `null` | direct | major horizontal dimension (local Y); required when `shape != "round"` (Sprint 18) | none yet | Numeric input (`stone-length`), non-round only | preliminary |
| `stone.width` | float \| null | mm | no range rule yet (REQUIRES_RULE_EVOLUTION) | `null` | direct | minor horizontal dimension (local X); drives `prong_center_radius`; required when `shape != "round"` (Sprint 18) | none yet | Numeric input (`stone-width`), non-round only | preliminary |
| `stone.depth` | float | mm | `> 0.5` and `< min(resolved length, resolved width)` (business rule) | `4.0` | direct | crown/pavilion heights | `JM-STONE-002` (SHARED) | Numeric input (`stone-depth`) | preliminary |
| `stone.orientation` | float | degrees | none (periodic quantity) | `0.0` | direct | rotation of the finished stone solid around its own local vertical axis (Sprint 18) | none | Numeric input (`stone-orientation`), non-round only, Advanced | preliminary |
| `setting.type` | string | — | fixed `"prong"` | `"prong"` | direct | selects setting construction path | none | none (fixed) | preliminary |
| `setting.prongCount` | integer | count | `4` or `6` (business rule; schema allows any int) | `6` | direct | number of prong solids, angular spacing | `JM-PRONG-001`, `JM-PRONG-003` | Select (`prong-count`, options 4/6) | preliminary |
| `setting.prongDiameter` | float | mm | `≥ 0.8` (business rule) | `1.1` | direct | prong cylinder radius, `prong_center_radius` | `JM-PRONG-002` | Numeric input (`prong-diameter`) | preliminary |
| `setting.prongHeight` | float | mm | `> basketHeight` (business rule) | `4.8` | direct | prong cylinder height | `JM-PRONG-004` | Numeric input (`prong-height`) | preliminary |
| `setting.basketHeight` | float | mm | `> 0`, `< prongHeight` (business rule) | `3.5` | direct | basket height, stone girdle Z position | `JM-PRONG-004`, `JM-SETTING-001`, `JM-SETTING-002` | Numeric input (`basket-height`) | preliminary |
| `material.metal` | string | — | 5 fixed values (see [`050-material-domain.md`](../04-jewelry-domain/050-material-domain.md)) | `"yellow_gold_18k"` | direct | none (preview color only) | none | Select (`metal`) | preliminary |
| `manufacturing.method` | string | — | `"lost_wax_casting"` \| `"direct_resin_printing"` | `"lost_wax_casting"` | direct | none (validation context only) | `JM-MANUFACTURING-001` | Select (`manufacturing-method`) | preliminary |
| `preview.meshTolerance` | float | mm | `> 0`, finite | `0.1` | direct | mesh triangle density only (not the B-Rep solid) | schema-level (`gt=0`, `allow_inf_nan=False`) | none in current UI (schema default used; overridable in the STL export API request only) | not_required |
| `preview.angularTolerance` | float | radians | `> 0`, finite | `0.2` | direct | mesh triangle density only | schema-level | none in current UI (same override note as above) | not_required |

## Derived (non-schema) values referenced elsewhere in this Bible

These are computed, never stored, and therefore have no "canonical path"
of their own — listed here only to avoid a reader mistaking them for
missing schema parameters. Full detail:
[`052-parametric-dependency-model.md`](../04-jewelry-domain/052-parametric-dependency-model.md).

| Derived value | Computed from |
|---|---|
| `inner_radius` | `ring.innerDiameter / 2` |
| `outer_radius` | `inner_radius + band.thickness` |
| `band_top_z` | `outer_radius` |
| `prong_center_radius` | `resolved_width_mm(stone) / 2 − (setting.prongDiameter / 2) × 0.3` (Sprint 18: was `stone.diameter / 2`) |
| `resolved_length_mm` | `stone.diameter` if `shape == "round"` else `stone.length` |
| `resolved_width_mm` | `stone.diameter` if `shape == "round"` else `stone.width` |
| `resolved_depth_mm` | `stone.depth` (identical for every shape) |
| Stone girdle radius (round only) | `stone.diameter / 2` — no single girdle radius exists for a non-round outline |
| Stone girdle Z | `band_top_z + setting.basketHeight` |
| Stone crown/pavilion heights | `stone.depth × 0.35` / `stone.depth × 0.65` |
