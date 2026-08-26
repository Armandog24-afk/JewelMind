---
id: JM-BIBLE-A108
title: "Appendix: Shared Jewelry System Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-RING-README
  - JM-BIBLE-520
related_documents:
  - JM-BIBLE-521
implementation_status: current
professional_validation: not_required
normative: false
---

# Appendix: Shared Jewelry System Catalog

The 5 shared systems named in `CATEGORY_CAPABILITIES.sharedSystems`
(every category's entry lists the same 5 —
[`backend/jewelmind/jewelry_category/registry.py`](../../../backend/jewelmind/jewelry_category/registry.py)),
each backed by a real, unmodified `domain/schema.py` type
(JEWELRY-ARCH-GOV-007).

| Shared system | Real `domain/schema.py` type | Ring Architecture consumption |
|---|---|---|
| `material` | `MaterialSpec` (`material.metal`) | Not part of `RingDefinition` at all — `ring/models.py` defines no material field. Consumed as-is by geometry/export layers, unchanged. |
| `manufacturing` | `ManufacturingSpec` (`manufacturing.method`) | Same as `material` — no `RingDefinition` field; consumed as-is. |
| `stone` | `StoneSpec` (`shape`, `diameter`, `depth`) | Wrapped, not duplicated: `StoneArrangementDefinition.stone = definition.stone.model_copy()` in `ring/adapter.py` — the real `StoneSpec` object itself, copied whole. |
| `setting` | `SettingSpec` (`type`, `prongCount`, `prongDiameter`, `prongHeight`, `basketHeight`) | Split across two `RingDefinition` destinations by field, never re-typed: `type`/`prongCount`/`prongDiameter`/`prongHeight` -> `SettingAttachmentDefinition`; `basketHeight` -> `RingHeadDefinition.basketHeightMm` (ring-structural attachment — see JEWELRY-ARCH-GOV-005). |
| `preview` | `PreviewSpec` (`meshTolerance`, `angularTolerance`) | Not part of `RingDefinition` — consumed directly by the preview/export layers, unchanged. |

In every case, Ring Architecture **consumes** the existing type — it
never defines a competing `MaterialDefinition`, `ManufacturingContext`,
or similar. Confirmed by reading `backend/jewelmind/ring/models.py` in
full: none of its 7 classes (`RingModel`, `RingSizing`,
`ShankDefinition`, `ShoulderDefinition`, `RingHeadDefinition`,
`StoneArrangementDefinition`, `SettingAttachmentDefinition`,
`RingDefinition`) redefines a material, manufacturing, or preview field;
`StoneArrangementDefinition.stone` is typed directly as the real
`StoneSpec` imported from `domain/schema.py`, not a Ring-local copy of
its shape.

See [`533-solitaire-migration-model.md`](../18-ring-architecture/533-solitaire-migration-model.md)
for the full field-by-field mapping this table summarizes, and
[`535-category-extension-test-model.md`](../18-ring-architecture/535-category-extension-test-model.md)
for the honest note that shared-system reuse is verified here by code
inspection, not (yet) by a dedicated `SHARED_MATERIAL_REUSE_TEST`.
