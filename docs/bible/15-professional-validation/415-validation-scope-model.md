---
id: JM-BIBLE-415
title: Validation Scope Model
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
  - JM-BIBLE-412
  - JM-BIBLE-418
  - JM-BIBLE-441
normative: true
implementation_status: current
professional_validation: not_required
---

# Validation Scope Model

`ValidationScope` (`backend/jewelmind/professional_validation/schemas.py`) states exactly what a validation decision covers. Every field is optional — a scope only states what it actually constrains (PROVAL-GOV-003).

## The 16 fields

All 16 fields are `str | None`, defaulting to `None`:

| Field | Constrains |
|---|---|
| `jewelryCategory` | e.g. `"ring"` (`JewelryCategory` in `domain/schema.py`). |
| `ringStyle` | e.g. `"solitaire"` (`JewelryStyle`). |
| `component` | A specific geometry component (e.g. `"prongs"`). |
| `material` | A material family. |
| `alloy` | A specific alloy, narrower than `material`. |
| `manufacturingMethod` | e.g. `"lost_wax_casting"` \| `"direct_resin_printing"` (`ManufacturingMethod`). |
| `stoneShape` | e.g. `"round"` (`StoneShape`). |
| `stoneDimensionRangeMm` | A stated dimension range, e.g. `"6-8mm"` — free text, never an implicit unbounded range. |
| `settingType` | e.g. `"prong"` (`SettingType`). |
| `sizeRange` | A stated ring-size range. |
| `cadApplication` | The external CAD package a workflow claim is scoped to. |
| `exporterVersion` | The exact exporter version reviewed. |
| `forgeRuleVersion` | The exact Forge rule-set/registry version reviewed. |
| `atlasVersion` | The exact Atlas geometry-core version reviewed. |
| `jdlVersion` | The exact JDL schema version reviewed. |
| `geographicOrWorkshopConstraints` | Regional or workshop-specific practice constraints, echoing `058-professional-validation-register.md`'s existing "geographic or process scope" field. |

Every field is a plain string (or `None`) — none is a numeric range type, a regex, or an expression. A scope is a fact about what was reviewed, not executable logic; this mirrors the JDL rule against embedding expressions in data (`docs/bible/05-jdl/062-design-goals-and-non-goals.md`).

## `scope_matches()` — the matching rule, precisely

`backend/jewelmind/professional_validation/scope.py::scope_matches(scope, context)` is the one real function that decides whether a candidate context falls inside a recorded scope. Its full logic, reproduced here because it is short and load-bearing:

```python
def scope_matches(scope: ValidationScope, context: dict[str, str]) -> bool:
    for field in _SCOPE_FIELDS:
        constraint = getattr(scope, field)
        if constraint is None:
            continue
        if context.get(field) != constraint:
            return False
    return True
```

Two rules fall out of this directly:

1. **A scope field left `None` never narrows the match.** If `scope.stoneShape` is unset, the record makes no claim about stone shape either way — any `stoneShape` in the candidate context is compatible with that scope, for that field.
2. **Every field the scope *does* set must match the candidate context exactly.** If `scope.manufacturingMethod == "lost_wax_casting"`, a context with `manufacturingMethod == "direct_resin_printing"` fails the match — and so does a context that omits `manufacturingMethod` entirely (`context.get(field)` returns `None`, which is never equal to a real constraint string).

An entirely empty `ValidationScope()` matches any context — the maximally broad (and maximally unhelpful, in practice) case, because it constrains nothing.

## The worked example

Per the Sprint 13 brief, stated here verbatim because it is the concrete case every other rule in this document exists to enforce:

> A record valid for round solitaire + lost-wax casting must not automatically validate oval halo + resin printing.

Concretely: a `ValidationScope(stoneShape="round", manufacturingMethod="lost_wax_casting")` does not match `context={"stoneShape": "oval", "manufacturingMethod": "direct_resin_printing"}`. This is not a hypothetical — it is the second-to-last vector in `specs/professional-validation/v1/test-vectors/scope-vectors.json`:

```json
{
  "scope": { "manufacturingMethod": "lost_wax_casting", "stoneShape": "round", "...": null },
  "context": { "stoneShape": "oval", "manufacturingMethod": "direct_resin_printing" },
  "matches": false
}
```

and it is proven live against the real function by `backend/tests/test_professional_validation_scope.py::test_round_lost_wax_scope_does_not_cover_oval_resin_context`.

## The 5 real tests in `test_professional_validation_scope.py`

| Test | Proves |
|---|---|
| `test_empty_scope_matches_any_context` | An unset scope matches anything — the honest "claims nothing" case, not an implicit "applies everywhere" claim about the *evidence* (PROVAL-GOV-003 distinguishes "claims nothing" data-shape honesty from any assumption that unscoped evidence is broadly applicable). |
| `test_matching_context_is_covered` | A scope whose set fields exactly match the context returns `True`. |
| `test_round_lost_wax_scope_does_not_cover_oval_resin_context` | The worked example above — PROVAL-GOV-016/017 enforced live. |
| `test_a_scope_field_left_unset_never_narrows_the_match` | A scope constraining only `manufacturingMethod` still matches a context with any `stoneShape`. |
| `test_context_missing_a_constrained_field_does_not_match` | A scope constraining `manufacturingMethod`, tested against a context that never mentions `manufacturingMethod` at all, returns `False` — a missing context field is never treated as an implicit match. |

## What this scope model does not do

`scope_matches()` performs exact string equality on each set field — it has no notion of a numeric range check (e.g. it cannot itself parse `stoneDimensionRangeMm: "6-8mm"` and check whether a candidate `7.2` falls inside it) and no notion of partial/fuzzy matching. A scope naming `stoneDimensionRangeMm: "6-8mm"` is compared as an opaque string against whatever string the caller supplies as context — any numeric range interpretation is the caller's responsibility, not this function's. This is a real, current limitation, not a hidden one; see [`441-review-sampling-strategy.md`](441-review-sampling-strategy.md) for why breadth of reviewed examples (not implicit numeric interpolation) is how this framework expects range coverage to actually be established.
