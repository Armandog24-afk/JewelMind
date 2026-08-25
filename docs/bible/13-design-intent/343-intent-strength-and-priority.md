---
id: JM-BIBLE-343
title: Intent Strength And Priority
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-332
related_documents:
  - JM-BIBLE-344
implementation_status: current
professional_validation: not_required
normative: true
---

# Intent Strength And Priority

## `IntentStrength`

`Literal["OPTIONAL", "PREFERRED", "IMPORTANT", "REQUIRED"]` (`backend/jewelmind/design_intent/schemas.py`), default `"PREFERRED"`, present on both `IntentStatement` and `IntentRelation`.

## `_normalize_strength()`'s real, narrow contract

`resolver.py::_normalize_strength(raw)`:

```python
def _normalize_strength(raw: str | None) -> IntentStrength:
    if raw is None:
        return "PREFERRED"
    token = raw.strip().upper()
    return token if token in _STRENGTH_VALUES else "PREFERRED"
```

Strength is never inferred from adjective intensity, punctuation, or emphasis language. If the raw strength string is `None`, or anything other than an exact case-insensitive match for one of the 4 literal values, the statement silently falls back to `"PREFERRED"`. A request phrased with strong emphasis ("it absolutely must be delicate") does not, on its own, become `REQUIRED` — a provider would have to explicitly emit the token `"REQUIRED"` as the raw strength for that to happen, and current prompts do not instruct it to infer strength from emphasis wording; they only pass through whatever value the provider supplies verbatim.

## `priority: int` — modeled, not used

`IntentStatement.priority` defaults to `0` and exists in the schema, but no real logic in `backend/jewelmind/design_intent/` or `backend/jewelmind/designer/` reads it. It is not used to order statements in `DesignIntent.statements`, not used by `conflicts.py` to break ties, and not surfaced distinctly in the Studio review UI. This is an honest, currently-inert field — present for a plausible future ordering mechanism, not yet wired to any behavior.

## Strength does influence conflict classification — the one real exception

`conflicts.py::_value_conflicts()` does read `strength`, in exactly one place: when two statements on the same `(target, concept)` are at maximum continuum distance (opposite ends), the conflict is classified `PRIORITY_CONFLICT` instead of `EXPLICIT_CONTRADICTION` if — and only if — *both* statements have `strength == "REQUIRED"`. See [`346-intent-conflict-model.md`](346-intent-conflict-model.md) for the full algorithm. Outside this one classification branch, strength has no other effect on any computed outcome.

## Strength is never geometric magnitude

Restating INTENT-GOV-008 explicitly for this doc: `IntentStrength` describes how firmly the user holds a preference for review purposes — it never scales a dimension, never multiplies a tolerance, and is not read by any Forge rule. A `REQUIRED` statement about `VISUAL_WEIGHT: BOLD` still resolves to `PRESERVED`, identically to an `OPTIONAL` one, as far as JDL is concerned.
