---
id: JM-BIBLE-425
title: Review Case Model
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
  - JM-BIBLE-426
  - JM-BIBLE-442
implementation_status: current
professional_validation: not_required
normative: false
---

# Review Case Model

## Fields

`ReviewCase` (`backend/jewelmind/professional_validation/schemas.py`, mirrored by `specs/professional-validation/v1/review-case.schema.json`):

| Field | Purpose |
|---|---|
| `caseId` | Stable identifier for this reproducible review unit, e.g. `JMCASE001`. |
| `purpose` | Why this case exists — what it's meant to show a reviewer. |
| `jdlDocument` | The full `JewelryDefinition` used to generate this case's artifacts. |
| `definitionHash` | The real content hash of `jdlDocument` — see below. |
| `compilationFingerprint` | Optional — a future compiler/kernel version fingerprint (see `docs/bible/08-alchemist/174-determinism-and-version-fingerprint.md` if it exists) once one is implemented. |
| `forgeRuleSetVersion` | Which version of `specs/forge/v1/current-rule-registry.json` this case was validated against. |
| `atlasVersion` | The geometry generator version that produced this case's artifacts. |
| `exportedArtifacts` | Which artifacts exist for this case (STEP, STL, etc.). |
| `expectedQuestions` | The review questions this case is specifically meant to surface. |
| `reviewScope` | A `ValidationScope` — what this case's review would actually cover. |
| `evidenceGeneratedIds` | Evidence records produced while reviewing this case. |

## Reproducibility is the whole point

A `ReviewCase` exists to be regenerated identically. Given the same `jdlDocument`, the same `forgeRuleSetVersion`, and the same `atlasVersion`, JewelMind must produce the same `definitionHash` and the same geometry every time — this is not a new guarantee this Sprint introduces, it is `backend/jewelmind/utils/hashing.py::definition_hash()`, the exact deterministic content-hash function every generated model has used since Sprint 1's CAD-determinism guarantee (LAW-003, `docs/bible/00-foundation/004-jewelmind-constitution.md`). A `ReviewCase` is simply that existing guarantee, named and packaged for the professional-review context: a reviewer (or JewelMind itself, later) can always regenerate the exact same case and get the exact same result, which is what makes a review of it meaningful and auditable over time.

## A case is not a validation record

A `ReviewCase` describes *what was shown to a reviewer*. It carries no `decision`, no `status`, and no `reviewerId` of its own beyond what's referenced through `evidenceGeneratedIds` — a case can exist, be reviewed by zero, one, or several reviewers, and accumulate multiple, possibly disagreeing, `ValidationRecord`s that each reference it (via `ValidationRecord.sessionId`/evidence linkage) without the case itself ever becoming a validation claim.

## Cross-references

- [`442-golden-review-models.md`](442-golden-review-models.md) — the specific, stable review cases JewelMind defines for the current solitaire.
- [`426-review-package-contract.md`](426-review-package-contract.md) — what a `ReviewCase`'s artifacts actually look like when bundled for a reviewer.
- [`441-review-sampling-strategy.md`](441-review-sampling-strategy.md) — how multiple review cases together achieve behavioral coverage.
