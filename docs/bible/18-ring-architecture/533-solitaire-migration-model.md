---
id: JM-BIBLE-533
title: Solitaire Migration Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-RING-README
  - JM-BIBLE-520
related_documents:
  - JM-BIBLE-521
implementation_status: current
professional_validation: not_required
normative: true
---

# Solitaire Migration Model

The complete field-by-field mapping from every real
[`domain/schema.py`](../../../backend/jewelmind/domain/schema.py) field
into `RingDefinition` v2, cross-checked against the real
[`ring/adapter.py::ring_definition_from_jdl()`](../../../backend/jewelmind/ring/adapter.py)
implementation and evidenced by real generated data at
[`specs/ring/v2/test-vectors/solitaire-migration-vectors.json`](../../../specs/ring/v2/test-vectors/solitaire-migration-vectors.json).

## Field-by-field mapping

Each real JDL field group is tagged with one of the eight category
labels this document uses to organize the mapping: `SHARED`, `RING`,
`SOLITAIRE`, `SETTING`, `STONE`, `MATERIAL`, `MANUFACTURING`, `PREVIEW`.
(These are a table-organization device for this document specifically —
the underlying, authoritative three-bucket design classification
[`SHARED` / `RING-SPECIFIC` / `POTENTIALLY-SHARED-BUT-CONTEXTUAL`] is
[`521-shared-vs-category-specific-domain.md`](521-shared-vs-category-specific-domain.md);
the two are consistent, not competing, taxonomies.)

| Category | Real JDL field(s) | `RingDefinition` v2 destination | Notes |
|---|---|---|---|
| `SHARED` | `project.name`, `project.units` | *(not consumed)* | Metadata only; `RingDefinition` never references `project`. |
| `SHARED` | `jewelry.category` | *(not consumed by `RingDefinition`)* | Consumed one level up, by `jewelry_category.dispatch`, to select the generator. |
| `SOLITAIRE` | `jewelry.style` | `RingDefinition.family` | `family=definition.jewelry.style` — direct assignment, no transformation. Today `JewelryStyle = Literal["solitaire"]`, so this is always `"solitaire"`. |
| `RING` | `ring.sizeSystem`, `ring.size`, `ring.innerDiameter` | `RingSizing.sizeSystem` / `.size` / `.innerDiameter` | 1:1, no unit conversion (mm/EU throughout, LAW-007). |
| `RING` | `band.width`, `band.thickness`, `band.profile` | `ShankDefinition.widthMm` / `.thicknessMm` / `.profile` | 1:1; note the field rename `width` -> `widthMm` / `thickness` -> `thicknessMm` (naming clarity only, same value, same unit). |
| `STONE` | `stone.shape`, `stone.diameter`, `stone.depth` | `StoneArrangementDefinition.stone` | Copied via `definition.stone.model_copy()` — the entire real `StoneSpec` object, not individual fields re-typed. `StoneArrangementDefinition.arrangement` is set to the literal `"SINGLE_CENTER"` (not read from JDL — there is no arrangement field in `domain/schema.py` today; single-center is the only arrangement real geometry produces). |
| `SETTING` | `setting.type`, `setting.prongCount`, `setting.prongDiameter`, `setting.prongHeight` | `SettingAttachmentDefinition.settingType` / `.prongCount` / `.prongDiameterMm` / `.prongHeightMm` | 1:1, with the same `Diameter`/`Height` -> `...Mm` naming clarification as `band`. |
| `SETTING` | `setting.basketHeight` | `RingHeadDefinition.basketHeightMm` | The one field of `SettingSpec` that maps to `head`, not `setting`, in `RingDefinition` v2 — see [`531-ring-component-graph.md`](531-ring-component-graph.md) and [`521-shared-vs-category-specific-domain.md`](521-shared-vs-category-specific-domain.md) for why. |
| `MATERIAL` | `material.metal` | *(not consumed)* | `RingDefinition` has no material field at all; the real `MaterialSpec` is used as-is by geometry/export, never re-implemented (JEWELRY-ARCH-GOV-007). |
| `MANUFACTURING` | `manufacturing.method` | *(not consumed)* | Same as `MATERIAL` — `RingDefinition` has no manufacturing field. |
| `PREVIEW` | `preview.meshTolerance`, `preview.angularTolerance` | *(not consumed)* | Same pattern — consumed directly by the preview/export layers, never by `RingDefinition`. |

`shoulders` (`ShoulderDefinition`) has no source JDL field at all —
`ring_definition_from_jdl()` constructs it as `ShoulderDefinition()`
(its only field, `modeled: Literal[False] = False`, has no input to
read). This is documented, not silent: see
[`527-shoulder-contract.md`](527-shoulder-contract.md) and
[`536-current-code-mapping-and-gaps.md`](536-current-code-mapping-and-gaps.md).

## Real evidence: one generated migration vector

From
[`solitaire-migration-vectors.json`](../../../specs/ring/v2/test-vectors/solitaire-migration-vectors.json)
(real data, produced by running the actual adapter against a real
`JewelryDefinition`, not hand-invented):

```json
"sourceJDL": {
  "ring": {"sizeSystem": "EU", "size": 16, "innerDiameter": 17.8},
  "band": {"width": 2.4, "thickness": 1.8, "profile": "comfort_fit"},
  "stone": {"shape": "round", "diameter": 6.5, "depth": 4.0},
  "setting": {"type": "prong", "prongCount": 6, "prongDiameter": 1.1,
              "prongHeight": 4.8, "basketHeight": 3.5}
}
```

maps to

```json
"ringDefinitionV2": {
  "family": "solitaire",
  "sizing": {"sizeSystem": "EU", "size": 16.0, "innerDiameter": 17.8},
  "shank": {"profile": "comfort_fit", "widthMm": 2.4, "thicknessMm": 1.8},
  "shoulders": {"modeled": false},
  "head": {"basketHeightMm": 3.5},
  "stoneArrangement": {"arrangement": "SINGLE_CENTER",
    "stone": {"shape": "round", "diameter": 6.5, "depth": 4.0}},
  "setting": {"settingType": "prong", "prongCount": 6,
    "prongDiameterMm": 1.1, "prongHeightMm": 4.8}
}
```

The vector's own recorded note confirms the mapping direction: *"Field-by-field:
ring->sizing, band->shank, stone(+SINGLE_CENTER)->stoneArrangement,
setting.basketHeight->head, setting.{type,prongCount,prongDiameter,prongHeight}->setting."*

`backend/tests/test_ring_architecture_schemas.py::test_default_solitaire_ring_definition_example_is_reproducible_live`
re-derives this same mapping live against
`specs/ring/v2/examples/current-default-solitaire.json` on every test
run, so this table cannot silently drift from the real adapter code.

## No accidental coupling found; no breaking refactor required

The brief anticipated this Sprint might require a "targeted refactor" to
cleanly separate ring-specific data from shared data inside
`domain/schema.py`. That did not happen: auditing every field (the table
above) found **no field whose meaning was tangled across concerns** in a
way that would have forced a change to `domain/schema.py` itself. The
migration is a clean, direct, additive adapter:

- `domain/schema.py` was not modified (JEWELRY-ARCH-GOV-008,
  [`520-jewelry-category-architecture.md`](520-jewelry-category-architecture.md)).
- `ring_definition_from_jdl()` is a pure, deterministic read of an
  unmodified `JewelryDefinition` —
  `test_adapter_is_pure_and_deterministic` in
  `backend/tests/test_ring_architecture.py` proves two calls against the
  same input produce identical output.
- The only design decision this Sprint made about existing fields was
  where each one is *read from* and *copied to* in the new,
  additive `RingDefinition` v2 layer — never how it is stored, typed, or
  validated at the JDL boundary.

The "targeted refactor" the brief anticipated turned out to be
additive-only: a new adapter layer sitting underneath the unchanged JDL
schema, exactly the "existing JDL -> compatibility adapter -> internal
model" pattern the brief's own section 20 recommended over a breaking
JDL migration.
