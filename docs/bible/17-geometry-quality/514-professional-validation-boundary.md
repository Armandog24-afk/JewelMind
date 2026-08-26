---
id: JM-BIBLE-514
title: Professional Validation Boundary
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-QUALITY-README
  - JM-BIBLE-500
related_documents:
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-442
implementation_status: current
professional_validation: not_required
normative: true
---

# Professional Validation Boundary

Golden status (this Sprint) and Professional Validation status (Sprint 13, [`15-professional-validation/`](../15-professional-validation/README.md)) are **fully independent axes**. Neither implies, upgrades, downgrades, or substitutes for the other (QUALITY-GOV-001).

## The expected combination for essentially every current case

`Golden status: STABLE` + `Professional Validation status: NOT_REVIEWED` is **valid and expected** for essentially every one of the 9 cases in [`goldens/solitaire-v1/`](../../../goldens/solitaire-v1/) today. A Golden Model being `STABLE` means only that its recorded `GeometrySnapshot` currently matches what the real pipeline (re)produces — a software regression fact, verified by `verify_golden()`. It says nothing about whether a real, named jewelry professional has ever looked at that geometry. Per Sprint 13's own registry discipline, [`15-professional-validation/current-validation-registry.json`](../../../specs/professional-validation/v1/current-validation-registry.json) stays at zero real `ValidationRecord` entries until real review actually happens (PROVAL-GOV rules in [`410-validation-governance.md`](../15-professional-validation/410-validation-governance.md)) — so the `NOT_REVIEWED`/absent-record side of this pairing is not a gap this Sprint introduced; it is the correct, honest current state of every JewelMind geometry, Golden or not.

## No code conflates the two axes

Nothing in `backend/jewelmind/geometry_quality/` imports from or writes to `backend/jewelmind/professional_validation/`, and nothing in `professional_validation/` imports from `geometry_quality/` — verified directly by reading both packages' source. `backend/tests/test_geometry_quality_schemas.py::TestNoProfessionalClaim` further enforces this at the data level: every accepted golden and the manifest itself is scanned for prohibited claim strings (`manufacturing_ready`, `production_approved`, `professionally_validated`, `industry_standard`, and hyphenated variants) and must contain none of them.

## A future `goldenModelId` reference: not present today

The brief for this Sprint suggested a future professionally-reviewed model could reference a `goldenModelId` for reproducibility. This was checked directly against the real Sprint 13 schemas in `backend/jewelmind/professional_validation/schemas.py`:

- `ReviewCase` (line 210) carries `caseId`, `purpose`, `jdlDocument`, `definitionHash`, `compilationFingerprint`, `forgeRuleSetVersion`, `atlasVersion`, `exportedArtifacts`, `expectedQuestions`, `reviewScope`, `evidenceGeneratedIds` — no `goldenModelId` field.
- `ReviewPackageManifest` (line 279) carries `packageId`, `caseId`, `generatedAt`, `sourceDefinitionHash`, `jdlVersion`, `compilerVersion`, `forgeVersion`, `atlasVersion`, `includedFiles`, `checksums`, `missingOptionalFiles`, `knownLimitations` — likewise no `goldenModelId` field.

A repository-wide search for `goldenModelId`/`golden_model_id`/`goldenId` inside `backend/jewelmind/professional_validation/` returns no matches. **This field does not exist anywhere in the professional validation package today.** This document records it honestly as a **documented future integration point**, not an implemented one: `ReviewCase.definitionHash` already gives a reviewed case the same identity concept a Golden case uses (`GoldenModel.definitionHash`), so a future `goldenModelId: str | None` field on `ReviewCase` — cross-referencing a real entry in `goldenIds` from a suite's `manifest.json` — would be a small, additive schema change if a professional reviewer is ever asked to review a case that happens to also be a Golden case. No such change is proposed or scheduled by this document; see question 3 in [`517-open-geometry-quality-questions.md`](517-open-geometry-quality-questions.md).

## `442-golden-review-models.md` already anticipated this Sprint

[`15-professional-validation/442-golden-review-models.md`](../15-professional-validation/442-golden-review-models.md) — a Sprint 13 document — already contains a section titled "Naming note added in Sprint 15 — do not confuse with `GoldenModel` (Geometry Quality)" that:

- Correctly identifies that Sprint 15 introduced an unrelated, differently-scoped `GoldenModel` type at [`501-golden-model-contract.md`](501-golden-model-contract.md), with real materialized fixtures under `goldens/solitaire-v1/`.
- States plainly that a "golden review model" (Sprint 13's own concept — a reproducible starting point for a *human professional review session*, still unmaterialized as of Sprint 13, with zero files under `examples/professional-review/solitaire/`) and a Geometry Quality `GoldenModel` (an *automated software regression baseline*, compared on every code change) share only the word "golden."
- Already links forward to this exact document (`514-professional-validation-boundary.md`) by its planned filename.

This document was verified against that file directly: no edit to `442-golden-review-models.md` was needed — it already anticipated and correctly framed this boundary before this document existed. `442`'s own fixture set (`default-six-prong`, `four-prong`, `flat-band`, `comfort-fit-band`, `low-boundary-stone`, `high-boundary-stone`, `invalid-four-prong-large-stone`) remains unmaterialized and was not built or reused by this Sprint — Sprint 15 did not repurpose `goldens/solitaire-v1/` for professional-review purposes, and this document does not change that.

## Cross-references

- [`15-professional-validation/README.md`](../15-professional-validation/README.md) — the authoritative Professional Validation Framework.
- [`15-professional-validation/442-golden-review-models.md`](../15-professional-validation/442-golden-review-models.md) — the Sprint 13 sibling concept, already cross-linked both ways.
- [`517-open-geometry-quality-questions.md`](517-open-geometry-quality-questions.md) — the open `goldenModelId` question.
