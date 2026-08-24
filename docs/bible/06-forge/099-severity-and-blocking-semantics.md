---
id: JM-BIBLE-099
title: Severity and Blocking Semantics
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-098
related_documents:
  - JM-BIBLE-A16
implementation_status: partial
professional_validation: not_required
normative: true
---

# Severity and Blocking Semantics

## Severity

`INFORMATION`, `WARNING`, `ERROR`, `FATAL`. The current implementation's `Severity` type (`backend/jewelmind/validation/rules.py`) only defines `information | warning | error` (lowercase) — **`FATAL` does not exist as a rule severity today.** The closest current equivalent to "fatal" is a structural rejection at FORGE-0 (Pydantic construction failure), which never becomes a `ValidationResult` at all — it is an entirely different failure path (`REQUEST_VALIDATION_ERROR`). This document adds `FATAL` to the conceptual model for that FORGE-0 case, without claiming the current `Severity` literal type includes it.

## Blocking scope, separate from severity

`NONE`, `GENERATION`, `PREVIEW`, `STEP_EXPORT`, `STL_EXPORT`, `ALL_EXPORTS`, `WORKFLOW`.

**Blocking scope is a new conceptual axis this Sprint introduces; the current implementation does not track it per-rule.** Today, exactly one blocking mechanism exists: `has_errors(results)` (true iff any result has `severity == "error"`), which gates both generation (`ModelService.generate()`) and, transitively, every export (since export requires a previously-generated `ModelRecord`, and generation was already blocked). There is no current rule whose `error` severity blocks generation but not export, or blocks STEP but not STL — **every current `error` result has the same practical blocking scope: `GENERATION` (and transitively `ALL_EXPORTS`, since export always requires a prior successful generation).**

## Do not assume every ERROR means the same future blocking scope

This is worth stating explicitly because it is a natural but incorrect assumption: nothing about `severity: ERROR` *semantically* requires it to always block `ALL_EXPORTS`. A future rule could plausibly be `ERROR` for `STEP_EXPORT` (e.g. a manufacturing-precision concern specific to CNC/CAD interchange) while still permitting `PREVIEW` and `STL_EXPORT` to proceed. This distinction has no current example — it is recorded here so a future rule author does not have to guess whether blocking scope narrower than "everything" is architecturally supported (conceptually, yes; not implemented, no).

## Current runtime behavior, mapped

| Rule severity | Current blocking behavior |
|---|---|
| `error` | Blocks `ModelService.generate()` via `ValidationBlockedError` (422) → transitively blocks all exports, since none can proceed without a generated model |
| `warning` | Never blocks anything; returned for informational display only |
| `information` | Never blocks anything; used only by `JM-RING-003`'s smaller-discrepancy case |
| (structural failure) | Blocks before any `ValidationResult` exists — `REQUEST_VALIDATION_ERROR`, 422, from FastAPI/Pydantic |

## Worked examples

- `JM-BAND-001` (`error`) → conceptual `blockingScope: [GENERATION, ALL_EXPORTS]`.
- `JM-BAND-003` (`warning`) → conceptual `blockingScope: [NONE]`.
- `FORGE-GEOM-001` (`warning`, post-generation) → conceptual `blockingScope: [NONE]` — the compound fallback is a degraded-but-valid result, not a failure (LAW-005).
- `FORGE-EXPORT-001` (effectively `error`-equivalent via `ModelNotFoundError`/`ValidationBlockedError`) → conceptual `blockingScope: [STEP_EXPORT, STL_EXPORT]` for that specific export call, `ALL_EXPORTS` in practice since both exporters share the same precondition.
