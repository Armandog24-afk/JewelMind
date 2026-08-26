---
id: JM-BIBLE-A81
title: "Appendix: Professional Reviewer Role Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-410
related_documents:
  - JM-BIBLE-413
  - JM-BIBLE-414
implementation_status: current
professional_validation: not_required
normative: false
---

# Appendix: Professional Reviewer Role Catalog

The 8 real `ReviewerRole` values (`backend/jewelmind/professional_validation/schemas.py`), a table-only re-statement of [`413-reviewer-role-model.md`](../15-professional-validation/413-reviewer-role-model.md). A closed `Literal`; an invented role is rejected by Pydantic (`backend/tests/test_professional_validation_schemas.py::TestReviewerRole::test_an_invented_role_is_rejected`). No role is a blanket credential — `ReviewerQualification.professionalFocus` states the fit for one specific review (PROVAL-GOV-004).

| Role | One-line meaning | Typical high-relevance review areas |
|---|---|---|
| `JEWELRY_CAD_DESIGNER` | Reviews model structure/workflow as a working CAD professional. | Model topology, feature layout, solid organization, editability, workflow sensibility — independent of manufacturing process. |
| `GOLDSMITH_BENCH_JEWELER` | Reviews whether a piece can actually be worked at the bench. | General bench-work feasibility: filing, polishing, finishing, assembly order, wear/durability judgment. |
| `STONE_SETTER` | Reviews whether a stone can actually be set into the generated geometry. | Prong position, seat/bearing, stone accessibility, whether prongs can be pushed over the stone, tool access. |
| `CASTING_SPECIALIST` | Reviews casting-process-specific assumptions. | Sprue placement implications, shrinkage/wall-thickness concerns specific to `lost_wax_casting`, cleanup/finishing of as-cast geometry. |
| `RESIN_PRINTING_SPECIALIST` | Reviews resin-printing-process-specific assumptions. | Supports, minimum feature size, and orientation concerns specific to `direct_resin_printing`, distinct from casting. |
| `JEWELRY_MANUFACTURING_ENGINEER` | Reviews cross-process manufacturing feasibility. | Tolerance stack-ups and general producibility questions spanning casting and printing, not tied to one method. |
| `GEMOLOGIST` | Reviews stone-specific claims. | Dimensional/proportion assumptions about a stone shape, general stone-handling implications, independent of the metal setting. |
| `CAD_INTEROPERABILITY_SPECIALIST` | Reviews export-workflow and CAD-interoperability claims. | Whether a JewelMind STEP/STL export actually imports correctly and how editable it is in real external CAD software. |

## No single role reviews everything

A `GEMOLOGIST` accepting a stone-grading claim is not thereby qualified to accept a casting-process assumption, and a `CASTING_SPECIALIST` accepting a manufacturing profile is not thereby qualified to accept a stone-setting claim. One real person can hold more than one role's relevant experience; each capacity carries its own distinct `ReviewerQualification` record with its own `professionalFocus`.

## Real illustrative mapping: `specs/professional-validation/v1/test-vectors/qualification-vectors.json`

Three real, generated `ReviewerQualification` → `typicallyRelevantReviewAreas` vectors, quoted directly (none is a real reviewer or a real review — see [`413-reviewer-role-model.md`](../15-professional-validation/413-reviewer-role-model.md)):

| `reviewerId` | `role` | `professionalFocus` | Other fields set | `typicallyRelevantReviewAreas` |
|---|---|---|---|---|
| `q1` | `STONE_SETTER` | `"prong and bezel settings"` | none | `["setting", "prongs", "seat/bearing", "stone accessibility"]` |
| `q2` | `CASTING_SPECIALIST` | `"lost-wax casting production"` | `processes: ["lost_wax_casting"]` | `["manufacturing method: lost_wax_casting", "sprue/cleanup implications"]` |
| `q3` | `CAD_INTEROPERABILITY_SPECIALIST` | `"STEP import verification across CAD packages"` | `softwareExperience: ["Rhino", "MatrixGold"]` | `["export workflow", "STEP/STL import fidelity"]` |

These three vectors are validated as part of `backend/tests/test_professional_validation_specs.py`; they demonstrate the shape of the role-to-relevance relationship, not a completed qualification.

## Gap: 4 of 8 roles have no defined checklist yet

[`professional-review-checklist-catalog.md`](professional-review-checklist-catalog.md) (`JM-BIBLE-A83`) currently defines checklist categories only for `JEWELRY_CAD_DESIGNER`, `STONE_SETTER`, `GOLDSMITH_BENCH_JEWELER`, and `CASTING_SPECIALIST`. `RESIN_PRINTING_SPECIALIST`, `JEWELRY_MANUFACTURING_ENGINEER`, `GEMOLOGIST`, and `CAD_INTEROPERABILITY_SPECIALIST` have no role-specific checklist defined — a real, tracked gap, see [`451-validation-gap-analysis.md`](../15-professional-validation/451-validation-gap-analysis.md).

## Cross-references

- [`413-reviewer-role-model.md`](../15-professional-validation/413-reviewer-role-model.md) — narrative introduction to each role.
- [`414-reviewer-qualification-model.md`](../15-professional-validation/414-reviewer-qualification-model.md) — the full `ReviewerQualification` shape a role is embedded in.
- A new role beyond these 8 requires an RFC — see [`410-validation-governance.md`](../15-professional-validation/410-validation-governance.md), "When an RFC is required."
