---
id: JM-BIBLE-ADR-004
title: "ADR-004: Backend-authoritative validation"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on: []
related_documents:
  - JM-BIBLE-003
  - JM-BIBLE-022
implementation_status: current
---

# ADR-004: Backend-authoritative validation

## Status

Accepted.

## Context

Instant feedback while a user types requires validation logic to run in
the browser, with no network round trip. But a client can be running
stale code, be modified, or simply disagree with the server due to a bug
— something must be the final word before geometry is generated or a
file is exported.

## Decision

Implement the sixteen validation rules **twice**: once in
`shared/validation/engine.ts` (frontend, instant feedback only) and once
in `backend/jewelmind/validation/engine.py` (backend, authoritative). The
backend always re-validates before generation and export, and its
verdict wins if the two ever disagree — the frontend's validation state
is never trusted as sufficient on its own.

## Alternatives considered

- **Frontend-only validation, trusting the client.** Rejected: a client
  could bypass or misreport validation; violates
  [LAW-008](../00-foundation/004-jewelmind-constitution.md#LAW-008)
  (invalid definitions cannot generate or export).
- **Backend-only validation, with the frontend waiting for a network
  round trip on every keystroke.** Rejected: poor UX for a form with many
  interdependent numeric fields; instant feedback was judged worth the
  cost of maintaining two rule implementations.
- **A shared rule engine compiled once and used by both sides (e.g. via
  WebAssembly or a shared JSON rule format).** Considered as a way to
  avoid the two-implementation maintenance cost; not adopted for the MVP
  because introducing a rule-compilation toolchain was judged
  disproportionate to sixteen rules at this stage. Documented here as the
  natural next step if the rule count grows significantly (see
  [`000-bible-governance.md`](../00-foundation/000-bible-governance.md)'s
  update procedure).

## Positive consequences

- Instant UI feedback without sacrificing correctness — the backend is
  the safety net.
- Each engine is independently unit-tested
  (`test_validation.py` for the backend; the frontend mirror is exercised
  indirectly through component tests).

## Negative consequences

- Two implementations of the same sixteen rules must be kept in sync by
  hand — see
  [`013-functional-requirements.md`](../01-product/013-functional-requirements.md)
  and the update procedure in
  [`docs/validation-rules.md`](../../validation-rules.md).
- A rule added to one side and forgotten on the other creates a
  (currently manual-review-only) inconsistency risk.

## Risks

- Drift between the two engines would surface as the frontend showing a
  different verdict than the backend enforces at generate time — mitigated
  by the backend always winning (Product Principle 6), so drift is a UX
  annoyance, not a correctness violation.

## Review trigger

Revisit the "two engines" approach if the rule count grows large enough
that manual synchronization becomes error-prone or a source of repeated
bugs.

## Related implementation files

`backend/jewelmind/validation/engine.py`, `shared/validation/engine.ts`,
`backend/jewelmind/services/model_service.py::generate`.

## Related tests

`backend/tests/test_validation.py` (20 tests);
`backend/tests/test_api.py::test_generate_invalid_definition_returns_422`.
