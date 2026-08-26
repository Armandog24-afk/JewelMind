---
id: JM-BIBLE-440
title: Evidence Quality Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-410
related_documents:
  - JM-BIBLE-417
implementation_status: current
professional_validation: not_required
normative: true
---

# Evidence Quality Model

## The 7 real quality classes

`EvidenceQualityClass` (`backend/jewelmind/professional_validation/schemas.py`), each with a concrete jewelry-review example:

| Class | Example |
|---|---|
| `DIRECT_PHYSICAL` | A goldsmith holds a real cast sample and inspects it by hand. |
| `DIRECT_CAD` | A CAD designer opens the real STEP file in Rhino and inspects the solids directly. |
| `DIRECT_WORKFLOW` | A caster runs the actual casting-preparation workflow (spruing, investment) against the real geometry. |
| `DOCUMENTED_REFERENCE` | A cited industry reference document or published standard. |
| `PROFESSIONAL_JUDGMENT` | A reviewer's stated professional opinion, grounded in stated years of experience, without a specific document or physical artifact. |
| `SOFTWARE_ONLY` | A JewelMind automated test or Forge diagnostic result, with no human review involved. |
| `AI_ASSISTED` | Any output produced or summarized by an AI system, including an LLM's assessment of the geometry. |

## The hard rule (PROVAL-GOV-007)

`AI_ASSISTED` and `SOFTWARE_ONLY` evidence can **never alone** justify a `VALIDATED` or `VALIDATED_WITH_CONDITIONS` status. `specs/professional-validation/v1/validation-evidence.schema.json` documents this directly in its own field description for `qualityClass`. This exists specifically so a real reviewer's decision can be traced back to at least one piece of evidence that required an actual human professional's direct involvement — `DIRECT_PHYSICAL`, `DIRECT_CAD`, `DIRECT_WORKFLOW`, `DOCUMENTED_REFERENCE`, or `PROFESSIONAL_JUDGMENT`.

## No fake numerical evidence scores

`ValidationEvidence` (`backend/jewelmind/professional_validation/schemas.py`) has no numeric confidence, score, or percentage field of any kind — verified by reading the full model definition. Evidence quality is a **qualitative class**, one of the 7 above, never a manufactured "87% confidence" number that would imply a precision this framework has no basis for.

## Cross-references

- [`410-validation-governance.md`](410-validation-governance.md) — PROVAL-GOV-007.
- [`417-review-evidence-model.md`](417-review-evidence-model.md) — the full `ValidationEvidence` model this quality class is one field of.
- `specs/professional-validation/v1/validation-evidence.schema.json` — the real schema.
