---
id: JM-BIBLE-416
title: Review Session Model
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
  - JM-BIBLE-415
  - JM-BIBLE-425
  - JM-BIBLE-418
implementation_status: current
professional_validation: not_required
normative: false
---

# Review Session Model

`ReviewSession` (`backend/jewelmind/professional_validation/schemas.py`, mirrored in `specs/professional-validation/v1/review-session.schema.json`) is **one real sitting with one reviewer across one or more review cases**.

## Fields

| Field | Type | Notes |
|---|---|---|
| `sessionId` | `str` | Required, non-empty. |
| `date` | `str` | Required. |
| `reviewerId` | `str` | Required, non-empty. |
| `reviewType` | `str` | Free text describing what kind of session this was (e.g. "rule review", "geometry walkthrough"). Required. |
| `scope` | `ValidationScope` | Defaults to an empty scope. See [`415-validation-scope-model.md`](415-validation-scope-model.md). |
| `jewelmindVersions` | `dict[str, str]` | Version fingerprints pinned for the session (e.g. Forge rule-set version, Atlas version, JDL version). Default empty. |
| `reviewedCaseIds` | `str[]` | The `ReviewCase` IDs covered in this sitting. Default empty. |
| `evidenceIds` | `str[]` | `ValidationEvidence` IDs produced during this session. Default empty. |
| `observationIds` | `str[]` | `ReviewObservation` IDs raised during this session. Default empty. |
| `decisionIds` | `str[]` | IDs of the decisions reached during this session. Default empty. |
| `unresolvedQuestions` | `str[]` | Questions the reviewer raised but that were not resolved in this sitting. Default empty. |
| `followUpRequired` | `bool` | Whether this session requires a subsequent session before any of its findings can be considered complete. Defaults to `False`. |

## Why a session is a distinct concept

A `ReviewSession` is not the same thing as a `ReviewCase` ([`425-review-case-model.md`](425-review-case-model.md)) and not the same thing as a `ValidationRecord` ([`418-validation-decision-model.md`](418-validation-decision-model.md)):

- A **`ReviewCase`** is one reproducible unit under review — a specific JDL document at a specific `definitionHash`, pinned Forge/Atlas versions, and exported artifacts. It is the *thing looked at*.
- A **`ReviewSession`** is the *act of looking* — one reviewer, one real sitting, covering one or more `ReviewCase`s, producing zero or more `ValidationDecision`s and `ReviewObservation`s along the way. A single session might review two different `ReviewCase`s back-to-back (e.g. a round-solitaire case and an oval-solitaire case) if the reviewer's time was spent that way.
- A **`ValidationRecord`** is the durable, versioned outcome — it may optionally reference the `sessionId` it was produced in (`ValidationRecord.sessionId: str | None`), but it is the record that persists and is queried by `registry.py`, not the session itself.

This separation exists so that a single sitting's administrative facts (date, reviewer, which cases were touched, what remained unresolved) are recorded once, while the substantive outcome for each specific object under review is recorded as its own `ValidationRecord`, addressable and scopeable independently.

## `jewelmindVersions` and reproducibility

`jewelmindVersions` is a free-form `dict[str, str]` rather than a fixed set of named fields, because the specific set of version axes worth pinning for a session can vary (it might include a Forge registry version, an Atlas version, a JDL schema version, an exporter version — see the matching fields on `ValidationScope`). Recording these at the session level lets a later reader establish, for every decision made in that session, exactly which implementation the reviewer was actually looking at — this is the session-level counterpart to `ReviewCase.forgeRuleSetVersion`/`atlasVersion`, which pin the same facts at the level of one specific reproducible case.

## `unresolvedQuestions` and `followUpRequired`

Neither field forces a session to reach a conclusion. A session can legitimately end with open questions and `followUpRequired: true` — this is an honest, first-class outcome, not a failure state to be hidden or resolved artificially. No code in `backend/jewelmind/professional_validation/` requires `unresolvedQuestions` to be empty or `followUpRequired` to be `false` before a session's decisions can be recorded; an incomplete session simply produces fewer `ValidationRecord`s than a complete one would, plus a documented list of what remains open.
