---
id: JM-BIBLE-575
title: Stone Capability Model
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
  - JM-BIBLE-563
  - JM-BIBLE-573
  - JM-BIBLE-A115
implementation_status: current
professional_validation: not_required
normative: true
---

# Stone Capability Model

## The central point

> **Stone-generation capability and Setting compatibility are independent axes.** A shape that generates real, valid CAD geometry is not, by that fact, a shape whose setting is valid. (STONE-GOV-009)

Conflating the two would be the single most misleading thing this Sprint could have done. Six new shapes generate correct reference geometry and assemble into complete rings; not one of them has a prong setting designed for it. The capability model exists to make that distinction machine-readable rather than a footnote.

## The five capability axes

`geometry/stone/capability.py::StoneShapeCapability`:

| Axis | Type | Meaning |
|---|---|---|
| `generationSupported` | bool | `build_stone()` constructs real CAD geometry for this shape. |
| `jdlSupported` | bool | The shape is a real, accepted `StoneShape` enum member. |
| `inspectionSupported` | bool | Covered by real runtime inspection facts (generic component facts + the 6 `STONE_*` dimension facts). |
| `visionSupported` | bool | Vision renders the shape's real generated geometry. |
| `currentSettingCompatibility` | `SUPPORTED` \| `EXPERIMENTAL` \| `UNSUPPORTED` | Whether the **current** setting geometry places metal meaningfully for this shape. |

Plus three descriptive fields: `requiredDimensions`, `symmetryClass`, and `referenceGeometryVersion` (`"1.0.0"`), and a `status` of `current` or `planned`.

`visionSupported` is `true` for every generatable shape for a structural reason, not by coincidence: Vision parses whatever STL the backend produces and has no shape-specific code path (VISION-GOV-001/002). A shape that generates therefore renders, automatically. No frontend change was needed for any of the six new shapes.

## The real registry

All 7 shapes are `status: current` with `generationSupported: true`, `jdlSupported: true`, `inspectionSupported: true`, `visionSupported: true`.

The axis that differs:

| Shape | Symmetry class | Required dimensions | `currentSettingCompatibility` |
|---|---|---|---|
| `round` | `RADIAL` | `diameter`, `depth` | **`SUPPORTED`** |
| `oval` | `ELONGATED_SMOOTH` | `length`, `width`, `depth` | `EXPERIMENTAL` |
| `marquise` | `ELONGATED_SMOOTH` | `length`, `width`, `depth` | `EXPERIMENTAL` |
| `pear` | `ASYMMETRIC` | `length`, `width`, `depth` | `EXPERIMENTAL` |
| `emerald` | `RECTILINEAR_ANGULAR` | `length`, `width`, `depth` | `EXPERIMENTAL` |
| `princess` | `RECTILINEAR_ANGULAR` | `length`, `width`, `depth` | `EXPERIMENTAL` |
| `cushion` | `ROUNDED_RECTILINEAR` | `length`, `width`, `depth` | `EXPERIMENTAL` |

Each `EXPERIMENTAL` entry carries a specific recorded reason naming the real deficiency — tips unsupported for marquise, no tip-awareness for pear, no corner-awareness for the three angular shapes, generic circular placement for oval. See [`573-stone-setting-interface.md`](573-stone-setting-interface.md).

The full table with descriptions is in [`../appendices/stone-capability-catalog.md`](../appendices/stone-capability-catalog.md).

## Single source of truth

`STONE_SHAPE_CAPABILITIES` in `geometry/stone/capability.py` is the only place a capability may be asserted (STONE-GOV-014). `specs/stone/v1/shape-registry.json` is a **generated mirror**, not a second hand-maintained copy — it was produced by serialising the live registry, and `test_stone_schemas.py::test_shape_registry_matches_the_real_capability_registry_live` re-derives it and asserts byte equality of every field.

No documentation, Designer capability list, or Studio option may claim a capability this registry marks otherwise. Two consumers currently mirror it by hand and must be updated in the same change:

- `frontend/src/components/ConfigurationPanel.tsx::STONE_SHAPE_OPTIONS` — the Studio shape selector.
- `backend/jewelmind/designer/normalizer.py::STONE_SHAPE_SYNONYMS` — the IT/EN natural-language table.

Designer's `current_capabilities()` reads `StoneShape` directly via `get_args()`, so it cannot drift.

## Invariants enforced by test

| Test | Invariant |
|---|---|
| `test_stone_schemas.py::test_shape_registry_matches_the_real_capability_registry_live` | The mirror equals the live registry, field for field. |
| `test_stone_schemas.py::test_registry_never_marks_a_non_generatable_shape_as_current` | No `status: current` entry has `generationSupported: false`. |
| `test_stone_schemas.py::test_only_round_is_setting_compatibility_supported` | Exactly `["round"]` is `SUPPORTED` — the generation/setting separation, asserted rather than described. |
| `test_stone_schemas.py::test_all_seven_target_shapes_are_present_and_current` | The `current` set is exactly the 7 target shapes. |
| `test_stone.py::TestStoneCapabilityRegistry` (5 tests) | Per-shape capability metadata exists; round is `SUPPORTED`; every non-round shape is `EXPERIMENTAL`; no shape is `planned`; an unknown shape returns `None`. |

The `test_only_round_is_setting_compatibility_supported` assertion is deliberately exact rather than a `<=` bound. If a future sprint makes a shape genuinely settable, that test must be updated consciously — which is the point.

## No `planned` shapes

`STONE_SHAPE_CAPABILITIES` contains no `planned` entries. All 7 target shapes reached `current`, so the Sprint's strong target was fully met and there was nothing honest to mark otherwise.

Future shapes (asscher, radiant, heart, trillion, baguette, cabochon, custom outlines, calibrated stones) are **not** pre-registered as `planned`. Listing them would imply a commitment and a design that does not exist; per STONE-GOV/RFC governance each requires an RFC before it becomes a registry entry. They are recorded as open questions in [`579-open-stone-questions.md`](579-open-stone-questions.md) instead.

This differs deliberately from the Shank capability registry (Sprint 17), which *does* carry `planned` entries — there, named future capabilities like split shank and cathedral had already been architecturally reserved by an earlier sprint's documentation, so recording them honestly as `planned` was more accurate than omitting them. No equivalent prior commitment exists for stone shapes.

## Adding a capability

Per STONE-GOV-014/015 and the governance rules in [`560-stone-governance.md`](560-stone-governance.md):

1. An RFC for a new shape (a jewelry-domain extension).
2. A `STONE_SHAPE_CAPABILITIES` entry with an **honest** `currentSettingCompatibility` — `EXPERIMENTAL` unless the setting geometry genuinely handles it.
3. Regenerate `specs/stone/v1/shape-registry.json` from the live registry; never hand-edit it.
4. Update the two hand-mirrored consumers above.
5. Real generation, orientation, and inspection tests, plus the shape's **own new** Golden case.

## `referenceGeometryVersion`

Every entry carries `"1.0.0"`. It is bumped on any MAJOR change to how a shape's outline or loft is built — a changed construction primitive, a changed reference proportion, a changed corner treatment. Because such a change alters generated geometry, it also requires a documented Golden baseline update and, per [`560-stone-governance.md`](560-stone-governance.md), an ADR for the construction change itself.
