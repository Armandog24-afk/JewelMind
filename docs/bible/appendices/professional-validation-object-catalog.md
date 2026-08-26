---
id: JM-BIBLE-A82
title: "Appendix: Professional Validation Object Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-410
related_documents:
  - JM-BIBLE-412
implementation_status: current
professional_validation: not_required
normative: false
---

# Appendix: Professional Validation Object Catalog

The 11 real `ValidationObjectType` values (`backend/jewelmind/professional_validation/schemas.py`), a table-only re-statement of [`412-validation-object-model.md`](../15-professional-validation/412-validation-object-model.md). Every `ValidationTarget.objectType` is one of these; a new value beyond these 11 requires an RFC ([`410-validation-governance.md`](../15-professional-validation/410-validation-governance.md)). None of the examples below is a claim that the example has been reviewed — the active registry contains zero records.

| Value | Meaning | Concrete JewelMind example |
|---|---|---|
| `FORGE_RULE` | One rule from `specs/forge/v1/current-rule-registry.json`, at one exact version. | `objectId="JM-PRONG-003"`, `version="1.0.0"` — "4 prongs blocked when stone diameter > 8mm" (`backend/jewelmind/validation/engine.py::_prong_rules`). |
| `DOMAIN_STATEMENT` | A jewelry-domain claim in `docs/bible/04-jewelry-domain/` that is not itself a single Forge rule. | A statement in `043-ring-anatomy.md` about how a basket relates to a prong set. |
| `GEOMETRY_COMPONENT` | One geometry builder in `backend/jewelmind/geometry/components/`. | The prongs component, `backend/jewelmind/geometry/components/prongs.py`. |
| `GEOMETRY_RELATIONSHIP` | How two components relate geometrically, not either component alone. | Stone-to-basket fit — whether the basket opening/height accommodate the stone reference solid from `geometry/assemblies/solitaire.py`. |
| `COMPLETE_MODEL` | A full generated solitaire assembly for one specific `JewelryDefinition`, identified by its `definitionHash`. | A specific default-parameter solitaire ring generated end-to-end, reviewed as a whole. |
| `MANUFACTURING_PROFILE` | An assumption tied to one `ManufacturingSpec.method` value. | The `direct_resin_printing` assumptions behind `JM-MANUFACTURING-001`. |
| `MATERIAL_PROFILE` | An assumption tied to one `MaterialSpec.metal` value. | An assumption specific to `platinum` as opposed to `yellow_gold_18k` (`backend/jewelmind/domain/schema.py::MaterialSpec`). |
| `SETTING_BEHAVIOUR` | An assumption about how a `SettingSpec.type` behaves for stone retention, independent of a single Forge rule. | Whether current `prong` setting geometry provides adequate retention for a given stone size class — broader than `JM-PRONG-003` alone. |
| `EXPORT_WORKFLOW` | An assumption about STEP/STL export correctness or completeness. | Whether `backend/jewelmind/exporters/step_exporter.py`'s output is dimensionally correct when opened in a real CAD package. |
| `CAD_INTEROPERABILITY_WORKFLOW` | An assumption about how a JewelMind-exported artifact behaves once imported into external CAD software. | Whether a JewelMind STEP export imports cleanly into Rhino or MatrixGold without manual repair — see `ImportOutcome`. |
| `DESIGN_PROFILE` | **FUTURE / PLANNED.** A reusable, named stylistic profile. | **None exist.** JewelMind has zero registered design profiles anywhere; `DesignIntent.profile` is hardcoded `None` by `build_design_intent()`. Included now so a future design-profile feature has a real object type to target — never describe this as currently reviewable. |

## Why an explicit object type matters

A record naming `objectType: FORGE_RULE, objectId: JM-PRONG-003` says nothing about `GEOMETRY_COMPONENT` prongs, even though both concern prongs — a rule's numeric threshold and a prong's actual geometric shape are reviewed as separate objects (PROVAL-GOV-015).

## Relationship to source registries

`FORGE_RULE` objects correspond one-to-one with entries in `specs/forge/v1/current-rule-registry.json` (21 total). `GEOMETRY_COMPONENT`/`GEOMETRY_RELATIONSHIP` objects correspond to Atlas components documented in [`atlas-component-catalog.md`](atlas-component-catalog.md). This framework never invents a parallel identifier — `ValidationTarget.objectId` references the existing identifier from the appropriate source registry.

## Cross-references

- [`412-validation-object-model.md`](../15-professional-validation/412-validation-object-model.md) — full `ValidationTarget` field table and narrative.
- [`professional-validation-status-matrix.md`](professional-validation-status-matrix.md) (`JM-BIBLE-A86`) — the 21 `FORGE_RULE` objects mapped to their current status.
