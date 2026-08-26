---
id: JM-BIBLE-417
title: Review Evidence Model
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
  - JM-BIBLE-418
  - JM-BIBLE-440
implementation_status: current
professional_validation: not_required
normative: false
---

# Review Evidence Model

`ValidationEvidence` (`backend/jewelmind/professional_validation/schemas.py`) is one piece of evidence a reviewer produced or relied on. A `ValidationDecision`/`ValidationRecord` references evidence by `evidenceId` (`evidenceIds: list[str]`) rather than embedding it inline, so the same piece of evidence can be cited by more than one decision without duplication.

## Fields

| Field | Type | Notes |
|---|---|---|
| `evidenceId` | `str` | Required, non-empty. |
| `type` | `EvidenceType` | One of 17 values, below. Required. |
| `qualityClass` | `EvidenceQualityClass` | One of 7 values, below. Required. |
| `source` | `str` | Who/what produced this evidence. Required. |
| `date` | `str` | Required. |
| `relatedReviewCaseId` | `str \| None` | Optional link to the `ReviewCase` this evidence was produced against. |
| `description` | `str` | Required. |
| `fileOrReference` | `str \| None` | Optional pointer to a file or external reference. |
| `limitations` | `str` | Free text stating what this evidence does *not* establish. Defaults to `""`. |

## The 17 `EvidenceType` values

`LIVE_SOFTWARE_OBSERVATION`, `CAD_FILE_INSPECTION`, `STEP_IMPORT_INSPECTION`, `STL_INSPECTION`, `PHYSICAL_PRINT`, `CAST_SAMPLE`, `BENCH_WORK`, `STONE_SETTING_TEST`, `MEASUREMENT`, `REFERENCE_DOCUMENT`, `MANUFACTURER_GUIDANCE`, `PROFESSIONAL_EXPERIENCE`, `COMPARATIVE_CAD_MODEL`, `PHOTO`, `VIDEO`, `ANNOTATED_SCREENSHOT`, `WRITTEN_REVIEW`.

These range from direct physical acts (`CAST_SAMPLE`, `BENCH_WORK`, `STONE_SETTING_TEST`) through CAD/software inspection (`CAD_FILE_INSPECTION`, `STEP_IMPORT_INSPECTION`, `STL_INSPECTION`, `LIVE_SOFTWARE_OBSERVATION`) to purely documentary/experiential forms (`REFERENCE_DOCUMENT`, `MANUFACTURER_GUIDANCE`, `PROFESSIONAL_EXPERIENCE`, `WRITTEN_REVIEW`) and visual records (`PHOTO`, `VIDEO`, `ANNOTATED_SCREENSHOT`, `COMPARATIVE_CAD_MODEL`).

**Not every review must use every evidence type.** A rule review conducted purely by live software observation and professional experience, without a physical cast sample, is a legitimate, complete review for its scope — it is simply weaker evidence than one that also includes `CAST_SAMPLE`/`BENCH_WORK` evidence, and its `qualityClass` should reflect that honestly (see below).

## The 7 `EvidenceQualityClass` values

`DIRECT_PHYSICAL`, `DIRECT_CAD`, `DIRECT_WORKFLOW`, `DOCUMENTED_REFERENCE`, `PROFESSIONAL_JUDGMENT`, `SOFTWARE_ONLY`, `AI_ASSISTED`.

`qualityClass` exists as a field separate from `type` because the same `EvidenceType` can carry different evidentiary weight depending on how it was produced — a `LIVE_SOFTWARE_OBSERVATION` made by a qualified reviewer sitting with the running application is `DIRECT_WORKFLOW` or `PROFESSIONAL_JUDGMENT`; the same evidence type produced purely by an automated script or an AI agent's own inspection is `SOFTWARE_ONLY` or `AI_ASSISTED`.

## Why `qualityClass` exists: `AI_ASSISTED` and `SOFTWARE_ONLY` can never alone justify `VALIDATED`

This is the field this framework relies on to make PROVAL-GOV-007 enforceable in data, not just in prose: because `AI_ASSISTED` and `SOFTWARE_ONLY` are real, nameable values rather than being silently absorbed into a generic "evidence exists" flag, a future review/audit process can mechanically identify and exclude them from what justifies a `VALIDATED`/`VALIDATED_WITH_CONDITIONS` `ValidationRecord.status`. Full detail on this classification — including how the two are distinguished from each other and from the five physically/professionally-grounded classes — lives in [`440-evidence-quality-model.md`](440-evidence-quality-model.md); this document does not duplicate that content.

## `limitations` is not optional to consider, even though the field defaults to empty

`limitations` defaults to `""`, which is a valid value (no limitations stated) — but a reviewer or process author populating real evidence is expected to state what the evidence does *not* establish (e.g. "single sample, one alloy, one size — does not establish behavior across the full 4-15mm stone diameter range"). An empty `limitations` field on a piece of real evidence should be read as "no limitation was recorded," not as "this evidence has no limitations" — the schema cannot itself force a limitation to be written, only provide the field for one.
