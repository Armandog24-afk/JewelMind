---
id: JM-BIBLE-412
title: Validation Object Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-410
related_documents:
  - JM-BIBLE-411
  - JM-BIBLE-415
  - JM-BIBLE-419
  - JM-BIBLE-420
normative: true
implementation_status: current
professional_validation: not_required
---

# Validation Object Model

`ValidationTarget` (`backend/jewelmind/professional_validation/schemas.py`) is the shape every `ValidationRecord.target` and `ValidationEvidence`/`ReviewCase` object reference ultimately resolves to. It names the *exact thing* a review is about, at an *exact version*, so a validation statement can never drift to mean something broader than what was actually reviewed (PROVAL-GOV-002).

## `ValidationTarget` fields

| Field | Type | Notes |
|---|---|---|
| `objectType` | `ValidationObjectType` | One of the 11 values below. Required. |
| `objectId` | `str` | The stable identifier of the thing being reviewed (e.g. a Forge rule ID, a component name). Required, non-empty (enforced by `cli.py::validate_review_record_dict()`). |
| `version` | `str` | The exact version of that object at review time (e.g. a rule's `currentVersion`, a component's implementation as of a specific commit/tag). Required, non-empty. |
| `description` | `str` | Free text describing the object, for a human reader. Not itself the reviewed claim — see `ValidationDecision.statementValidated` in [`418-validation-decision-model.md`](418-validation-decision-model.md) for that. |
| `implementationReferences` | `str[]` | Real file/function paths the object corresponds to. Default empty. |
| `relatedTests` | `str[]` | Real automated test names/paths that exercise the object. Default empty — these tests prove the *software* behaves as implemented; they never substitute for review (PROVAL-GOV-006). |
| `currentValidationStatus` | `ValidationStatus` | Default `"NOT_REVIEWED"`. |

## The 11 `ValidationObjectType` values

Every value below is a real `Literal` member in `schemas.py`. Each is illustrated with a concrete JewelMind example — none of these examples is a claim that the example has been reviewed; they exist to show what a future `ValidationTarget` for that type would look like.

| Value | Meaning | JewelMind example |
|---|---|---|
| `FORGE_RULE` | One rule from `specs/forge/v1/current-rule-registry.json`, at one exact version. | `objectId="JM-PRONG-003"`, `version="1.0.0"` — "4 prongs blocked when stone diameter > 8mm" (`backend/jewelmind/validation/engine.py::_prong_rules`). |
| `DOMAIN_STATEMENT` | A jewelry-domain claim documented in `docs/bible/04-jewelry-domain/` that is not itself a single Forge rule (e.g. a general anatomical or terminology statement). | A statement in [`043-ring-anatomy.md`](../04-jewelry-domain/043-ring-anatomy.md) about how a basket relates to a prong set. |
| `GEOMETRY_COMPONENT` | One geometry builder in `backend/jewelmind/geometry/components/`. | The prongs component, `backend/jewelmind/geometry/components/prongs.py`. |
| `GEOMETRY_RELATIONSHIP` | How two components relate to each other geometrically, not either component alone. | Stone-to-basket fit — whether the basket's opening and height actually accommodate the stone reference solid produced by `geometry/assemblies/solitaire.py`. |
| `COMPLETE_MODEL` | A full generated solitaire assembly for one specific `JewelryDefinition`, identified by its `definitionHash`. | A specific default-parameter solitaire ring generated end-to-end (band + stone reference + prongs + basket), reviewed as a whole rather than component-by-component. |
| `MANUFACTURING_PROFILE` | An assumption tied to one `ManufacturingSpec.method` value. | The `direct_resin_printing` assumptions behind `JM-MANUFACTURING-001` (`backend/jewelmind/validation/engine.py::_manufacturing_rules`). |
| `MATERIAL_PROFILE` | An assumption tied to one `MaterialSpec.metal` value. | An assumption specific to `platinum` as opposed to `yellow_gold_18k` (`backend/jewelmind/domain/schema.py::MaterialSpec`). |
| `SETTING_BEHAVIOUR` | An assumption about how a `SettingSpec.type` behaves for stone retention, independent of a single Forge rule. | Whether the current `prong` setting geometry provides adequate stone-retention behavior for a given stone size class — broader than the single numeric `JM-PRONG-003` threshold. |
| `EXPORT_WORKFLOW` | An assumption about STEP/STL export correctness or completeness. | Whether `backend/jewelmind/exporters/step_exporter.py`'s output is dimensionally correct when opened in a real CAD package. |
| `CAD_INTEROPERABILITY_WORKFLOW` | An assumption about how a JewelMind-exported artifact behaves once imported into external CAD software. | Whether a JewelMind STEP export imports cleanly into Rhino or MatrixGold without manual repair — see `ImportOutcome` in `schemas.py`. |
| `DESIGN_PROFILE` | **FUTURE / PLANNED.** A reusable, named stylistic profile (in the sense `IntentProfile`, [`355-intent-profile-model.md`](../13-design-intent/355-intent-profile-model.md), gestures at). | **None exist.** JewelMind has zero registered design profiles anywhere in the codebase — `DesignIntent.profile` is hardcoded `None` by `build_design_intent()` (see [`332-intent-domain-model.md`](../13-design-intent/332-intent-domain-model.md)). This `ValidationObjectType` value is included now so a future design-profile feature has a real review-object type to target; it must never be described as something currently reviewable, because nothing of this type currently exists to review. |

## Why an explicit object type matters

A `ValidationRecord` naming `objectType: FORGE_RULE, objectId: JM-PRONG-003` says nothing about `GEOMETRY_COMPONENT` prongs, even though both concern prongs — a Forge rule's numeric threshold and a prong's actual geometric shape are reviewed as separate objects, because a reviewer accepting one is not thereby asserting anything about the other. This mirrors PROVAL-GOV-015: a validation is never broader than what it actually names.

## Relationship to Forge and Atlas

`FORGE_RULE` objects correspond one-to-one with entries in `specs/forge/v1/current-rule-registry.json` (21 total). `GEOMETRY_COMPONENT` and `GEOMETRY_RELATIONSHIP` objects correspond to Atlas components documented in [`docs/bible/appendices/atlas-component-catalog.md`](../appendices/atlas-component-catalog.md). This framework does not duplicate either registry — a `ValidationTarget.objectId` references the existing identifier from the appropriate source registry rather than inventing a parallel one.
