---
id: JM-BIBLE-316
title: Designer Observability
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-315
related_documents:
  - JM-BIBLE-317
implementation_status: current
professional_validation: not_required
normative: true
---

# Designer Observability

## A PLANNED taxonomy of 10 conceptual events

A future, richer observability layer for Designer would plausibly want distinct structured log events for each meaningful transition in the pipeline:

1. `DESIGNER_REQUEST_STARTED`
2. `PROVIDER_CALLED`
3. `PROVIDER_FAILED`
4. `STRUCTURED_OUTPUT_RECEIVED`
5. `PROPOSAL_VALIDATED`
6. `CLARIFICATION_REQUIRED`
7. `UNSUPPORTED_FEATURE_DETECTED`
8. `PROPOSAL_READY`
9. `PROPOSAL_ACCEPTED`
10. `PROPOSAL_REJECTED`

This list names the real transition points already visible in `service.py::interpret()`/`_build_proposal()` and `DesignerPanel.tsx::handleApply()`/`handleCancel()` — each one corresponds to an actual branch or call site in the current implementation.

## None of these are currently emitted — stated plainly

This is a named taxonomy, not a shipped feature. `POST /api/designer/interpret` receives no distinct structured logging beyond what every other route in the application already gets: the generic `request` log line emitted by `backend/jewelmind/api/app.py`'s `request_id_and_timing` middleware (`method`, `path`, `status`, `durationMs`, `requestId`), and, on a raised `AppError`, the generic `app_error` log line (`code`, `message`, `requestId`). Neither of these distinguishes `DESIGNER_PROVIDER_UNAVAILABLE` from `DESIGNER_SECURITY_REJECTED` in any way beyond the shared `code` field every route's errors already carry, and neither logs anything about which in-band diagnostic codes a successful `200` response contained, how many `ProposedField`s it produced, or whether the user went on to accept or reject the proposal.

## Why this gap is named rather than quietly filled

Fabricating partial observability — emitting a few of the ten events without the others, or logging something that looks like `PROPOSAL_ACCEPTED` when `applyDesignerProposal()` is purely a frontend store action with no backend round trip at all — would create a misleading picture of what JewelMind can actually tell you happened. `applyDesignerProposal()` in particular has no backend correlate: acceptance and rejection are entirely client-side state transitions today, so a backend `PROPOSAL_ACCEPTED`/`PROPOSAL_REJECTED` event would require a new API call that does not currently exist. Naming the full taxonomy as PLANNED, with zero of it emitted, keeps the gap between intended and actual observability honest and traceable in one place. See [`321-designer-gap-analysis.md`](321-designer-gap-analysis.md).

See [`317-designer-cost-and-latency-model.md`](317-designer-cost-and-latency-model.md) for the closely related gap in real usage measurement.
