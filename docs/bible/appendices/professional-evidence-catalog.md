---
id: JM-BIBLE-A89
title: "Appendix: Professional Evidence Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-410
related_documents:
  - JM-BIBLE-417
  - JM-BIBLE-440
implementation_status: current
professional_validation: not_required
normative: false
---

# Appendix: Professional Evidence Catalog

Two tables from `backend/jewelmind/professional_validation/schemas.py`, a table-only re-statement of [`417-review-evidence-model.md`](../15-professional-validation/417-review-evidence-model.md) and [`440-evidence-quality-model.md`](../15-professional-validation/440-evidence-quality-model.md). `ValidationEvidence` has no numeric confidence/score field of any kind — quality is always one of the 7 qualitative classes below, never a manufactured percentage.

## The 17 `EvidenceType` values

| Value | One-line meaning |
|---|---|
| `LIVE_SOFTWARE_OBSERVATION` | A reviewer directly observing JewelMind's running application (Studio, generated model, viewer). |
| `CAD_FILE_INSPECTION` | A reviewer opening and inspecting an exported CAD file (STEP/STL) in their own CAD application. |
| `STEP_IMPORT_INSPECTION` | A reviewer specifically verifying a STEP file's import behavior/fidelity in an external CAD package. |
| `STL_INSPECTION` | A reviewer specifically verifying a tessellated STL file's mesh/geometry. |
| `PHYSICAL_PRINT` | A physical resin/wax print produced from the exported geometry and inspected by hand. |
| `CAST_SAMPLE` | A real cast metal sample produced from the exported geometry and inspected by hand. |
| `BENCH_WORK` | Actual bench work performed on a physical sample (filing, polishing, finishing). |
| `STONE_SETTING_TEST` | An actual attempt to set a real or reference stone into the physical/printed geometry. |
| `MEASUREMENT` | A direct dimensional measurement taken from a physical sample or CAD model. |
| `REFERENCE_DOCUMENT` | A cited industry reference document or published standard. |
| `MANUFACTURER_GUIDANCE` | Guidance from a materials/process manufacturer (e.g. a resin supplier's minimum-feature-size specification). |
| `PROFESSIONAL_EXPERIENCE` | A reviewer's stated professional experience, without a specific document or physical artifact attached. |
| `COMPARATIVE_CAD_MODEL` | A comparison against another CAD model (e.g. a known-good reference design). |
| `PHOTO` | A photograph of a physical sample, print, or cast piece. |
| `VIDEO` | A video record of a physical sample, process, or setting attempt. |
| `ANNOTATED_SCREENSHOT` | A screenshot of the CAD/viewer software with a reviewer's annotations. |
| `WRITTEN_REVIEW` | A reviewer's own written review document or notes. |

These range from direct physical acts (`CAST_SAMPLE`, `BENCH_WORK`, `STONE_SETTING_TEST`) through CAD/software inspection (`CAD_FILE_INSPECTION`, `STEP_IMPORT_INSPECTION`, `STL_INSPECTION`, `LIVE_SOFTWARE_OBSERVATION`) to documentary/experiential forms (`REFERENCE_DOCUMENT`, `MANUFACTURER_GUIDANCE`, `PROFESSIONAL_EXPERIENCE`, `WRITTEN_REVIEW`) and visual records (`PHOTO`, `VIDEO`, `ANNOTATED_SCREENSHOT`, `COMPARATIVE_CAD_MODEL`). Not every review must use every type — a review conducted purely by `LIVE_SOFTWARE_OBSERVATION` and `PROFESSIONAL_EXPERIENCE` is legitimate and complete for its scope, simply weaker evidence than one that also includes `CAST_SAMPLE`/`BENCH_WORK`, and its `qualityClass` should reflect that honestly.

## The 7 `EvidenceQualityClass` values

| Class | Meaning |
|---|---|
| `DIRECT_PHYSICAL` | Direct inspection of a real physical artifact (a cast sample, a print) by a qualified reviewer. |
| `DIRECT_CAD` | Direct inspection of the real CAD file by a qualified reviewer in their own software. |
| `DIRECT_WORKFLOW` | A qualified reviewer directly running a real process/workflow (e.g. spruing and investment) against the real geometry. |
| `DOCUMENTED_REFERENCE` | A cited, external, documented reference or standard. |
| `PROFESSIONAL_JUDGMENT` | A reviewer's stated professional opinion, grounded in stated experience, without a specific document or physical artifact. |
| `SOFTWARE_ONLY` | A JewelMind automated test or Forge diagnostic result, with no human review involved. |
| `AI_ASSISTED` | Any output produced or summarized by an AI system, including an LLM's assessment of the geometry. |

## The hard rule (PROVAL-GOV-007)

**`AI_ASSISTED` and `SOFTWARE_ONLY` evidence can never alone justify a `VALIDATED` or `VALIDATED_WITH_CONDITIONS` status.** `specs/professional-validation/v1/validation-evidence.schema.json` documents this directly in its own field description for `qualityClass`. A `ValidationRecord.status` of `VALIDATED`/`VALIDATED_WITH_CONDITIONS` must be traceable back to at least one piece of evidence that required an actual human professional's direct involvement — `DIRECT_PHYSICAL`, `DIRECT_CAD`, `DIRECT_WORKFLOW`, `DOCUMENTED_REFERENCE`, or `PROFESSIONAL_JUDGMENT`.

`qualityClass` exists as a field separate from `type` because the same `EvidenceType` can carry different evidentiary weight depending on how it was produced — a `LIVE_SOFTWARE_OBSERVATION` made by a qualified reviewer sitting with the running application is `DIRECT_WORKFLOW`/`PROFESSIONAL_JUDGMENT`; the same evidence type produced purely by an automated script or an AI agent's own inspection is `SOFTWARE_ONLY`/`AI_ASSISTED`.

## Cross-references

- [`417-review-evidence-model.md`](../15-professional-validation/417-review-evidence-model.md) — full `ValidationEvidence` field table.
- [`440-evidence-quality-model.md`](../15-professional-validation/440-evidence-quality-model.md) — PROVAL-GOV-007 in full detail.
