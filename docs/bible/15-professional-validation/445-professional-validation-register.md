---
id: JM-BIBLE-445
title: Professional Validation Register
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
  - JM-BIBLE-058
  - JM-BIBLE-412
  - JM-BIBLE-432
  - JM-BIBLE-434
implementation_status: current
professional_validation: not_required
normative: true
---

# Professional Validation Register

This document is the authoritative, current statement of JewelMind's
professional-validation register. It **formalizes** — and does not
contradict — [`04-jewelry-domain/058-professional-validation-register.md`](../04-jewelry-domain/058-professional-validation-register.md)
(Sprint 2), which already established the register's fields and stated
plainly that it was empty. That document's content is preserved
unmodified; this document is the machine-readable, code-backed successor
it points forward to, per the README's "Relationship to prior sprints"
section.

## The machine-readable register

The single active register is:

```
specs/professional-validation/v1/current-validation-registry.json
```

Its real, complete content, as of this writing, is:

```json
{
  "registryVersion": "1.0.0",
  "description": "The single active professional-validation registry. Every entry in 'records' must be a real ValidationRecord backed by a real, identifiable reviewer and real evidence — see docs/bible/15-professional-validation/445-professional-validation-register.md. Example and template records live in examples/ and must never appear here.",
  "records": []
}
```

`records` is an empty array. There is no reviewer name, no review date, no
evidence reference, and no decision anywhere in this file.

## Zero validated entries, verified live

This is not a claim taken on faith — it is checked by real, named,
passing tests every time the backend test suite runs:

| Test | What it proves |
|---|---|
| `backend/tests/test_professional_validation_registry.py::TestZeroValidationDefault::test_the_real_active_registry_file_exists` | The file above exists on disk. |
| `...::test_the_real_active_registry_has_zero_records` | `records` is empty. |
| `...::test_count_validated_on_the_real_registry_is_zero` | `registry.py::count_validated(load_active_registry())` returns `0` against the real file, not a fixture. |
| `...::test_no_object_id_is_reported_as_validated` | `registry.py::validated_object_ids(load_active_registry())` returns an empty list — no `objectId` anywhere is reported as validated. |
| `...TestNoFakeValidatedRule::test_a_template_record_in_the_registry_file_is_rejected` | If a record with `isTemplate=True` were ever placed in the active registry (e.g. an accidental copy-paste from `examples/`), `load_active_registry()` raises `TemplateRecordInRegistryError` rather than silently counting it. |
| `...::test_examples_directory_is_never_the_registry_path` | The 5 example/template `ValidationRecord` fixtures under `specs/professional-validation/v1/examples/` live at a structurally different path from the active registry and are never loaded by `load_active_registry()`. |

These tests are part of the same 675-backend-test suite CLAUDE.md requires
to pass before any change is declared complete — `count_validated()`
returning `0` is exercised on every CI run, not asserted once and left to
drift.

## Consequently: every Forge rule remains preliminary or not-required

`specs/forge/v1/current-rule-registry.json` (registryVersion `1.0.0`)
defines 21 rules. As verified directly against that file: 16 carry
`professionalValidationStatus: preliminary` (jewelry-domain thresholds —
see [`06-forge/README.md`](../06-forge/README.md)) and 5 carry
`professionalValidationStatus: not_required` (schema/system/geometry-
inspection/export rules). None carries `validated`. This is the direct,
mechanical consequence of the empty active registry above — `registry.py`
has no other code path that could mark a Forge rule validated.

## PENDING items: a real future possibility, not a current one

The register's data model (`ValidationStatus` in `schemas.py`) includes
values such as `REVIEW_PLANNED` and `UNDER_REVIEW` that could describe a
record whose review has started but not concluded — a genuinely useful,
honest intermediate state for a future real review-in-progress. Holding
such a record would still never count toward `count_validated()`, which
only ever sums `VALIDATED` and `VALIDATED_WITH_CONDITIONS`
(`registry.py::_VALIDATED_STATUSES`).

**As of this writing, the active registry holds none of these either.**
It is not merely short of `VALIDATED` records — it contains zero records
of any status, including `NOT_REVIEWED`, `REVIEW_PLANNED`, or
`UNDER_REVIEW`. There is no in-flight review, no scheduled reviewer, and
no partially-completed record anywhere in this codebase. Stating
otherwise, even informally, would misrepresent the current state of the
product.

## Rules restated from `058` and `410`, still in force

- **Conflicting reviews are preserved, not merged** — a future
  `DisagreementRecord` names both conflicting `recordIds` explicitly; see
  [`430-professional-disagreement-model.md`](430-professional-disagreement-model.md)
  and PROVAL-GOV-012.
- **A code rule's existence never implies a register entry** — a
  threshold appearing in `backend/jewelmind/validation/engine.py` is
  never assumed to have a corresponding validated record simply because
  it exists and passes its own automated tests (PROVAL-GOV-006).
- **This register is the single active source** for "is object X at
  version Y currently professionally validated" — no other file,
  document, or code path in JewelMind may answer that question
  differently.

## How this document stays honest going forward

The moment a real `ValidationRecord` is added to
`specs/professional-validation/v1/current-validation-registry.json`, this
document's "Zero validated entries" section becomes stale and must be
updated in the same change that adds the record — per the Bible's
fundamental rule against silently letting documentation and code
contradict each other. Until that happens, every sentence above remains
literally, currently true.

## Cross-references

- [`04-jewelry-domain/058-professional-validation-register.md`](../04-jewelry-domain/058-professional-validation-register.md) — the Sprint 2 predecessor this document formalizes.
- [`06-forge/103-professional-validation-lifecycle.md`](../06-forge/103-professional-validation-lifecycle.md) — the Sprint 4 Forge-side statement of the same fact.
- [`412-validation-object-model.md`](412-validation-object-model.md) — the `ValidationRecord`/`ValidationStatus` shapes referenced above.
- [`449-validation-evaluation-framework.md`](449-validation-evaluation-framework.md) — how this register's emptiness propagates into every derived metric.
