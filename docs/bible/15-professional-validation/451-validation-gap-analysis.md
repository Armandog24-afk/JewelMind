---
id: JM-BIBLE-451
title: Validation Gap Analysis
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-410
  - JM-BIBLE-450
related_documents:
  - JM-BIBLE-452
implementation_status: current
professional_validation: not_required
normative: false
---

# Validation Gap Analysis

This document catalogues gaps observed while building this Sprint's final
document batch, without implementing any of them — mirroring
[`14-conversation/404-conversation-gap-analysis-and-open-questions.md`](../14-conversation/404-conversation-gap-analysis-and-open-questions.md)'s
gap-analysis structure. Every entry was verified against real code, not
assumed. None of these gaps is committed to a future Sprint by this
document alone.

## Gap table

| Gap | Current state | Risk | Business impact | Priority | Prerequisite | Target sprint |
|---|---|---|---|---|---|---|
| No real external reviewers yet | Active registry has zero records of any status (verified, [`445-professional-validation-register.md`](445-professional-validation-register.md)) | Every jewelry-domain rule and geometry component remains unvalidated indefinitely until this changes | High — this is the entire point of the framework; nothing else here substitutes for it | High | A real recruited reviewer, a completed review session, a real `ValidationRecord` | Unscheduled — depends on business development outside this codebase |
| No physical prototype evidence | `EvidenceType` includes `PHYSICAL_PRINT`/`CAST_SAMPLE`/`BENCH_WORK`/`STONE_SETTING_TEST`, none ever instantiated in real evidence | Software-only evidence (`SOFTWARE_ONLY`/`AI_ASSISTED`) can never alone justify `VALIDATED` (PROVAL-GOV-007); without physical evidence, no record can reach unconditional `VALIDATED` for a manufacturing-sensitive claim | Medium-High for casting/setting-specific rules | A real reviewer with bench/casting access | Unscheduled |
| No external CAD import evidence | `ImportOutcome` values never recorded (metric 10, [`449-validation-evaluation-framework.md`](449-validation-evaluation-framework.md)) | FOUNDRY-GOV-014's "no untested workflow called validated" rule has nothing to point to yet | Medium — affects credibility of the STEP export path specifically | Medium | A reviewer with a target CAD application to test against | Unscheduled |
| Incomplete version fingerprints | `ValidationTarget.version` is a free `str`; no single canonical "current version" resolver exists across Forge rule version, Atlas geometry-algorithm version, and JDL schema version simultaneously | A record could be written against an ambiguous or informally-stated version, weakening `classify_version_impact()`'s ability to compare it later | Medium | A defined multi-axis version-fingerprint format (echoes ALCHEMIST-GOV-009's not-yet-implemented `compilationHash`) | Unscheduled — coupled to Alchemist's own fingerprint work |
| No production-failure feedback loop | `contradictory_field_evidence` exists as a named expiration trigger ([`433-validation-expiration-and-revalidation.md`](433-validation-expiration-and-revalidation.md)) but no code path captures or surfaces a real production failure | A real-world failure could occur without ever reaching a `ValidationRecord`'s revalidation trigger | Medium-High once any record exists | A structured production-issue intake mechanism (does not exist) | Unscheduled |
| No reviewer portal | The only reviewer-facing surface is a downloaded ZIP and hand-written `ValidationRecord` JSON validated by the `validate-review-record` CLI | Every review is a manual, offline, asynchronous process; no in-app review submission exists | Low-Medium — a CLI-and-JSON workflow is a legitimate v1 choice, not obviously broken | Low | A decision to build a submission UI/API | Unscheduled |
| No database (confirmed) | The active registry is one JSON file, loaded fresh from disk on every read (`registry.py::load_active_registry()`); confirmed no SQL/NoSQL dependency exists anywhere in `backend/jewelmind/professional_validation/` or its imports | A file-based registry does not scale to concurrent writers or a large record count gracefully | Low today (record count is 0) | Would grow with real usage | Would need an ADR per PROVAL-GOV/410's "moving the active registry to a database" trigger | Unscheduled |
| No attachment storage | `ValidationEvidence.fileOrReference` is a plain string field; no upload endpoint, blob store, or file-retention policy exists for evidence attachments (photos, videos, annotated screenshots) | A real evidence photo/video has nowhere to actually live in this system today | Medium once real evidence exists | An evidence-storage mechanism and its own privacy review (see [`448-validation-security-and-privacy.md`](448-validation-security-and-privacy.md)) | Unscheduled |
| No signed validation record | Confirmed by direct search: no `signature`/`hmac`/cryptographic-signing code exists anywhere in `backend/jewelmind/professional_validation/` | A `ValidationRecord` JSON file could be edited after the fact with no tamper-evidence | Low today (no records exist to tamper with); grows with real usage and any external-facing claim of validation | Low-Medium | A defined signing scheme and key-management decision (a real architectural choice, not implied by anything current) | Unscheduled — open question 8 in [`452-open-professional-validation-questions.md`](452-open-professional-validation-questions.md) |
| No automated revalidation queue | `434-implementation-change-impact.md` states this flow "has never executed for a real record" and "there is also no automated code ... that runs this flow against a real code diff" | A future MAJOR change to a validated object would not automatically surface for revalidation without a human remembering to check | Medium once real validated records exist | **A real building block exists**: `versioning.py::classify_version_impact(validated_version, current_version)` is tested and correct (6 tests) — nothing yet calls it against an actual code diff or CI event | Wiring `classify_version_impact()` into a real change-detection trigger, e.g. a CI check or a pre-merge hook | Unscheduled |
| No validated material/manufacturing/setting profiles | `ValidationObjectType` includes `MANUFACTURING_PROFILE`, `MATERIAL_PROFILE`, `SETTING_BEHAVIOUR`; zero records of any of these three types exist | Manufacturing-method and material-selection remain purely metadata/context (per `052-parametric-dependency-model.md`) with no professional confirmation that this scope limitation itself is acceptable | Medium | Real reviewer sessions specifically scoped to these object types | Unscheduled |

## A finding worth flagging beyond the gap table: `432-validation-versioning.md` predates real code

[`432-validation-versioning.md`](432-validation-versioning.md) (already
written, not modified by this batch) states directly: *"There is
currently no running code in `backend/jewelmind/professional_validation/`
that computes one of these three outcomes automatically from a
diff."* This was true when `432` was written. It is **no longer true**:
`versioning.py::classify_version_impact()` now exists and is exactly the
function `432` describes as absent, tested by
`test_professional_validation_versioning.py`. Per the Bible's fundamental
rule ("report contradictions between code and the Bible explicitly ...
never silently change the meaning of the product to make a contradiction
disappear"), this document reports the contradiction rather than editing
`432` — this batch's scope is files 444-452 only. `432` should be updated
in a follow-up change to state that `classify_version_impact()` exists
and is tested, while preserving its own, still-accurate point that
nothing yet *invokes* that function against a real code diff or CI event
(the gap-table row above, "no automated revalidation queue," captures
that remaining true gap precisely).

## A second finding: `docs/professional-review/` is empty

The README's "Professional review templates" section states that
`docs/professional-review/` "holds the actual forms a real reviewer would
fill in." The directory exists on disk but currently contains **no
files** — no `README.md`, no reviewer-onboarding template, no
role-specific review form. This is either being populated by a
concurrently-running agent in this same Sprint or is a real, currently
unfilled gap; this document cannot determine which from the code alone
and reports it rather than assuming either.

## Cross-references

- [`450-current-code-mapping.md`](450-current-code-mapping.md) — the real-file inventory these gaps were found while writing.
- [`432-validation-versioning.md`](432-validation-versioning.md), [`434-implementation-change-impact.md`](434-implementation-change-impact.md) — the documents whose "not yet implemented" framing this document updates with the real `versioning.py` discovery.
- `../14-conversation/403-current-code-mapping.md`, `../14-conversation/404-conversation-gap-analysis-and-open-questions.md` — the Sprint 12 siblings this document follows in structure.
