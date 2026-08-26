---
id: JM-BIBLE-431
title: Conditional Acceptance Model
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
  - JM-BIBLE-415
  - JM-BIBLE-418
  - JM-BIBLE-432
implementation_status: current
professional_validation: not_required
normative: true
---

# Conditional Acceptance Model

## PROVAL-GOV-010

`ValidationRecord.conditions` (`str | None`,
`backend/jewelmind/professional_validation/schemas.py`) is required to be
non-empty whenever `decision == "ACCEPTED_WITH_CONDITIONS"`. This is
PROVAL-GOV-010, and it is enforced mechanically, not just documented, by
`backend/jewelmind/professional_validation/cli.py::validate_review_record_dict()`:

```python
if record.decision in ("ACCEPTED_WITH_CONDITIONS",) and not (record.conditions or "").strip():
    errors.append("decision ACCEPTED_WITH_CONDITIONS requires non-empty conditions (PROVAL-GOV-010).")
```

Two real tests prove both directions of this check:
`backend/tests/test_professional_validation_cli.py::test_accepted_with_conditions_requires_nonempty_conditions`
proves a record with `decision: "ACCEPTED_WITH_CONDITIONS"` and no
`conditions` text is rejected by `validate_review_record_dict()` with an
error containing `"PROVAL-GOV-010"`; `test_accepted_with_conditions_and_real_conditions_is_valid`
proves the same shape with `conditions: "Lost-wax casting only, round
stones <= 8mm."` passes.

## Worked example: the real conditional-validation fixture

`specs/professional-validation/v1/examples/conditional-validation-example.json`
is the generated illustration of this pattern (`isTemplate: true` —
illustrative, not a real review). Its shape:

- `target`: `objectType: "FORGE_RULE"`, `objectId: "JM-PRONG-001"`,
  `version: "1.0.0"`, `description: "prongCount must be 4 or 6."`
- `scope`: `manufacturingMethod: "lost_wax_casting"`,
  `stoneShape: "round"` (every other scope field left `null`)
- `decision: "ACCEPTED_WITH_CONDITIONS"`, `status: "VALIDATED_WITH_CONDITIONS"`
- `conditions`: `"Accepted only for round stones under lost-wax casting;
  not evaluated for resin printing."`
- `rationale`: `"Illustrative example of a conditional acceptance shape —
  not a real review."`

This is the concrete form of the brief's own worked example, "accepted
only for X process and Y parameter range": X is `lost_wax_casting`
(structured, in `scope.manufacturingMethod`), Y is "round stones"
(structured, in `scope.stoneShape`), and the record's own free-text
`conditions` field states the same constraint again, in the words a human
reviewer would actually write.

## Structured and free-text conditions exist side by side, not one OR the other

This document states the intended relationship explicitly, because it is
easy to assume only one representation is authoritative: **a
conditionally-accepted record carries its conditions in two places at
once, and both are meant to exist together, not as alternatives.**

1. **Machine-readable, where practical** — the structured
   `ValidationScope` fields recorded alongside the decision
   (`ValidationRecord.scope`, mirroring the same 16-field model documented
   in [`415-validation-scope-model.md`](415-validation-scope-model.md)).
   These fields are what `scope.py::scope_matches()` (see below) can
   actually evaluate against a candidate context.
2. **Always human-readable** — the free-text `conditions` field on
   `ValidationRecord` itself. This exists because not every condition a
   real reviewer states is expressible in the current 16 `ValidationScope`
   fields (e.g. a bench technique preference, a comment about a specific
   alloy supplier's casting behavior) — the free-text field is where that
   nuance is preserved rather than lost when it doesn't fit the structured
   schema.

Neither field is optional in spirit when `decision ==
"ACCEPTED_WITH_CONDITIONS"`: `conditions` is mechanically required
(PROVAL-GOV-010); `scope` should, in practice, capture whatever part of the
condition the existing `ValidationScope` fields can express, precisely so a
future scope-matching check has something structured to evaluate. A record
that states a machine-checkable condition only in prose (e.g. "only for
round stones" left unset in `scope.stoneShape`) is valid per the schema, but
weaker in practice than one that also sets the matching structured field —
this is a quality expectation for reviewers filling in records, not a rule
the schema itself enforces today.

## Using a conditional record outside its conditions

The critical downstream rule: **a rule used outside its validated
conditions must be treated as returning to preliminary, or as
out-of-validated-scope — never as still covered by the conditional
acceptance.** For the worked example above, `JM-PRONG-001` reviewed and
accepted only under `manufacturingMethod: "lost_wax_casting"` and
`stoneShape: "round"` says nothing about that same rule applied to a resin-
printed, oval-shaped context (JewelMind does not currently support oval
stones, but the scope principle holds for any dimension the scope actually
constrains) — that combination remains exactly as unvalidated as if no
`ValidationRecord` existed for `JM-PRONG-001` at all.

The real mechanism that determines whether a given usage context falls
inside or outside a record's validated conditions is
`scope_matches()` (`backend/jewelmind/professional_validation/scope.py`):

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

`scope_matches()` returns `True` only when every field the record's `scope`
actually constrains matches the candidate context; an unset scope field
never narrows the match, and a candidate context that provides a
conflicting value for any constrained field fails the match. Applied to the
conditional example above: a candidate context of
`{"manufacturingMethod": "lost_wax_casting", "stoneShape": "round"}` matches
the record's scope; a candidate context of
`{"manufacturingMethod": "direct_resin_printing", "stoneShape": "round"}`
does not, because `scope.manufacturingMethod == "lost_wax_casting"` while
`context["manufacturingMethod"] == "direct_resin_printing"`. When
`scope_matches()` returns `False` for a candidate usage, that usage must be
treated by any downstream consumer as `OUT_OF_VALIDATED_SCOPE` — practically
equivalent to `NOT_REVIEWED`/`preliminary` for that specific combination,
regardless of how confidently the rule was validated for a different,
narrower combination.
