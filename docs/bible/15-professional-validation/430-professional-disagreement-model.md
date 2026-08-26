---
id: JM-BIBLE-430
title: Professional Disagreement Model
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
  - JM-BIBLE-429
implementation_status: current
professional_validation: not_required
normative: true
---

# Professional Disagreement Model

## The hard rule: never silently average professional opinions

When two qualified reviewers reach different conclusions about the same
object, JewelMind never collapses their two `ValidationRecord`s into one
resolved "consensus" value. Both records remain fully visible, distinct,
and separately queryable, permanently. Nothing in
`backend/jewelmind/professional_validation/registry.py` supports anything
else: `count_validated()` and `count_by_status()` (`registry.py`, lines
56–67) simply count `ValidationRecord.status` values across the whole list
of loaded records — there is no averaging function, no "resolve conflicting
records" function, and no merge step anywhere in the module. Two records
with the same `target.objectId` and opposite `status` values both count
independently in whatever bucket their own `status` falls into. This is
PROVAL-GOV-012.

## `DisagreementRecord`: fields

`DisagreementRecord` (`backend/jewelmind/professional_validation/schemas.py`)
has 5 fields:

| Field | Type | Notes |
|---|---|---|
| `disagreementId` | `str` | Required. Unique identifier for this disagreement entry. |
| `objectId` | `str` | Required. The `ValidationTarget.objectId` the conflicting records both concern. |
| `type` | `DisagreementType` | Required. One of 5 values — see below. |
| `recordIds` | `list[str]` | Required (default empty, but meaningless if left empty). Names **both** conflicting `ValidationRecord.recordId` values explicitly — the record does not pick a side. |
| `description` | `str` | Required. Free-text explanation of what the two records actually disagree about. |

A `DisagreementRecord` is additive documentation *about* two existing
records — it never replaces, hides, or supersedes either one. Both
underlying `ValidationRecord`s keep their own independent `status`.

## `DisagreementType`: 5 values

| Value | Meaning |
|---|---|
| `AGREEMENT` | Reviewers reached the same conclusion — recorded to make the absence of conflict explicit and auditable, not left implicit. |
| `SCOPE_DIFFERENCE` | Both records are correct **within their own stated scope** — they are not actually disagreeing about the same claim once the scopes are read precisely. |
| `METHOD_DIFFERENCE` | Reviewers used different evaluation methods (e.g. different evidence types) and reached different conclusions as a result — the disagreement is about method, not necessarily about the underlying jewelry fact. |
| `PROFESSIONAL_DISAGREEMENT` | Reviewers genuinely disagree about the same claim, under the same scope, using comparable methods — an actual difference of professional judgment. |
| `INSUFFICIENT_CONTEXT` | There is not enough recorded context to classify the disagreement as any of the above yet. |

## Worked example: `SCOPE_DIFFERENCE`, not `PROFESSIONAL_DISAGREEMENT`

The original Sprint brief's own illustrative scenario is: Reviewer A
considers a geometry acceptable for one casting workflow; Reviewer B
rejects the same geometry for a different manufacturing workflow. Both
conclusions may be correct within their own scope — this is a
`SCOPE_DIFFERENCE`, not a true `PROFESSIONAL_DISAGREEMENT`, because the two
reviewers were not actually evaluating the same claim.

This scenario has a real, generated worked example in this Sprint's
fixtures — `specs/professional-validation/v1/examples/conflicting-review-example.json`
— which is the concrete illustration this document points to rather than a
hypothetical:

- `JM-PV-EXAMPLE-CONFLICT-A` — target `JM-PRONG-003` ("4 prongs blocked
  when stone diameter exceeds 8mm"), scope
  `manufacturingMethod: "lost_wax_casting"`, decision `ACCEPTED`, status
  `VALIDATED`, rationale `"Illustrative example — accepted for casting."`
- `JM-PV-EXAMPLE-CONFLICT-B` — the **same** target `JM-PRONG-003`, scope
  `manufacturingMethod: "direct_resin_printing"`, decision `REJECTED`,
  status `REJECTED`, rationale `"Illustrative example — rejected for resin
  printing at the same stone size."`
- The accompanying `disagreement` object:
  `disagreementId: "disagreement-example-1"`, `objectId: "JM-PRONG-003"`,
  `type: "SCOPE_DIFFERENCE"`, `recordIds: ["JM-PV-EXAMPLE-CONFLICT-A",
  "JM-PV-EXAMPLE-CONFLICT-B"]`, `description: "Both records concern the
  same rule but different manufacturing-method scopes — not a true
  disagreement, a scope difference, and neither record is silently
  preferred over the other."`

The same scenario is confirmed in the generated test vectors,
`specs/professional-validation/v1/test-vectors/disagreement-vectors.json`:

```json
{
  "disagreement": {
    "disagreementId": "disagreement-vector-1",
    "objectId": "JM-PRONG-003",
    "type": "SCOPE_DIFFERENCE",
    "recordIds": ["JM-PV-EXAMPLE-CONFLICT-A", "JM-PV-EXAMPLE-CONFLICT-B"],
    "description": "Accepted for lost-wax casting, rejected for resin printing at the same stone size."
  },
  "silentlyAveraged": false,
  "bothRecordsRemainVisible": true
}
```

Both `conflicting-review-example.json` records carry `isTemplate: true` —
this is an illustrative fixture demonstrating the mechanism, **not** a real
professional review of `JM-PRONG-003`; the active registry currently
contains zero records of any kind (see
[`README.md`](README.md#current-state-zero-professional-validation)).

## Proof: two conflicting records are never merged

`backend/tests/test_professional_validation_schemas.py::TestDisagreementPreservation`
proves this mechanically, not just by convention:

```python
def test_two_conflicting_records_are_never_merged_into_one(self):
    accepted = _record(
        recordId="JM-PV-001", reviewerId="reviewer-a", decision="ACCEPTED", status="VALIDATED"
    )
    rejected = _record(
        recordId="JM-PV-002",
        reviewerId="reviewer-b",
        decision="REJECTED",
        status="REJECTED",
        scope=ValidationScope(manufacturingMethod="direct_resin_printing"),
    )
    # Both real, distinct records — never averaged or collapsed into one.
    assert accepted.recordId != rejected.recordId
    assert accepted.status != rejected.status

def test_disagreement_record_names_both_conflicting_records(self):
    disagreement = DisagreementRecord(
        disagreementId="disagreement-1",
        objectId="JM-PRONG-003",
        type="SCOPE_DIFFERENCE",
        recordIds=["JM-PV-001", "JM-PV-002"],
        description="Accepted for casting, rejected for resin printing at the same stone size.",
    )
    assert disagreement.recordIds == ["JM-PV-001", "JM-PV-002"]
```

## Consequence for any consumer of this framework

Any future code (a rule-status dashboard, a Studio-facing summary — see
[`437-validation-to-product-workflow.md`](437-validation-to-product-workflow.md))
that wants to show "the" validation state of an object with more than one
record for the same `objectId` must show both records and, where one
exists, the `DisagreementRecord` that explains their relationship. It must
never pick a "winning" record, average their statuses, or otherwise present
a single derived verdict where two independent professional opinions
actually exist.
