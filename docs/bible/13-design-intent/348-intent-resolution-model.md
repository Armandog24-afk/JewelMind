---
id: JM-BIBLE-348
title: Intent Resolution Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-330
related_documents:
  - JM-BIBLE-349
implementation_status: current
professional_validation: not_required
normative: true
---

# Intent Resolution Model

## Two shapes, two very different lifecycles

Design Intent's resolution machinery has two related but distinct pieces in `backend/jewelmind/design_intent/schemas.py`: the `ResolutionStatus` enum, which is real and live on every statement and relation today, and the `IntentResolution` model, which is schema-complete but never actually constructed by any code path in v1. Conflating the two is the single easiest way to misdescribe this Sprint — this document keeps them separate.

## `ResolutionStatus` — real, live, 7 values, 2 in use

```
UNRESOLVED | PRESERVED | DETERMINISTICALLY_RESOLVED | USER_RESOLVED | PROFILE_RESOLVED | UNSUPPORTED | CONFLICTING
```

Every `IntentStatement` and `IntentRelation` carries a required `resolutionStatus` field. In the current implementation only two of the seven values are ever produced, both inside `resolver.py`:

- **`PRESERVED`** — the unconditional outcome for every statement and relation that `_resolve_statements()`/`_resolve_relations()` successfully normalizes (`resolver.py:108`, `resolver.py:138`). There is no branch that evaluates whether a deterministic mapping could apply, because none are registered — see [`349-deterministic-resolution-policy.md`](349-deterministic-resolution-policy.md).
- **`CONFLICTING`** — applied after the fact, in `build_design_intent()`, by rewriting any statement/relation whose id appears in `conflicting_ids(conflicts)` via `model_copy(update={"resolutionStatus": "CONFLICTING"})` (`resolver.py:184`, `resolver.py:188`). This is the only status transition in the codebase — every statement starts `PRESERVED` and may be demoted to `CONFLICTING` in the same request if `conflicts.py::detect_conflicts()` flags it.

The remaining five values are schema-reserved for stages that do not exist yet:

| Value | What would produce it | Exists today? |
|---|---|---|
| `UNRESOLVED` | An initial state before any resolution attempt | No — `resolver.py` always assigns `PRESERVED` on success |
| `DETERMINISTICALLY_RESOLVED` | A registered deterministic mapping firing | No — zero mappings registered ([`349`](349-deterministic-resolution-policy.md)) |
| `USER_RESOLVED` | The user explicitly approving a proposed numeric resolution | No — no resolution is ever proposed to approve |
| `PROFILE_RESOLVED` | An `IntentProfile` resolving the statement | No — zero profiles registered ([`355`](355-intent-profile-model.md)) |
| `UNSUPPORTED` | A recognized-but-declared-unsupported target/concept combination | No — recognized always means `PRESERVED` |
| `CONFLICTING` | A detected conflict | **Yes** — see above |

## `IntentResolution` — schema-only, a real, named gap

`IntentResolution{intentId, status, resultingJDLChanges=[], resolutionMethod: "NONE"|"DETERMINISTIC_RULE"|"USER_CONFIRMATION"|"PROFILE"="NONE", ruleOrProfile=None, userConfirmationRequired=False, notes=""}` is a complete Pydantic model in `design_intent/schemas.py`, but no function anywhere in the backend constructs one. It exists so a future resolution stage — the one that would eventually consume an `IntentProfile` (see [`355-intent-profile-model.md`](355-intent-profile-model.md)) and set `resolutionMethod: "PROFILE"` or `"USER_CONFIRMATION"` — has a real target shape to write into, per INTENT-GOV-018, rather than requiring a schema change when that stage is finally built. Its own docstring in `schemas.py` says this plainly: "Not currently persisted anywhere."

This is a deliberate placeholder, not an oversight — it is called out again in [`362-design-intent-gap-analysis.md`](362-design-intent-gap-analysis.md) as a concrete, scoped future-sprint item rather than left implicit.

## Why this split matters

`ResolutionStatus` answers "what happened to this statement in *this* request" (preserved, or flagged as conflicting). `IntentResolution` would answer "by what method, if any, was this statement ever turned into a JDL change" — a question that, in v1, always has the same answer: never. See [`350-intent-to-jdl-boundary.md`](350-intent-to-jdl-boundary.md) for why that boundary is currently absolute.

## Cross-references

- [`330-intent-governance.md`](330-intent-governance.md) — INTENT-GOV-010, INTENT-GOV-018.
- [`349-deterministic-resolution-policy.md`](349-deterministic-resolution-policy.md) — why zero deterministic mappings is correct.
- [`346-intent-conflict-model.md`](346-intent-conflict-model.md) — how `conflicts.py` produces the ids that drive the one real status transition.
