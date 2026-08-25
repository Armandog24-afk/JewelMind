---
id: JM-BIBLE-383
title: Correction Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-CONVERSATION-README
  - JM-BIBLE-370
  - JM-BIBLE-376
related_documents:
  - JM-BIBLE-384
  - JM-BIBLE-404
implementation_status: current
professional_validation: not_required
normative: true
---

# Correction Model

The Sprint 12 brief describes three distinct correction-related concepts. This document grounds each in real code and states plainly which are implemented and which are not.

## `CORRECT_ACTIVE_PROPOSAL` — implemented, as `MODIFY_DESIGN_PROPOSAL`

There is no `CORRECT_ACTIVE_PROPOSAL` value in the real `ConversationActionType` (the 13-value enum superseding any earlier conceptual list — see `specs/conversation/v1/conversation-action.schema.json`'s own description). A correction is represented, deliberately, as an ordinary `MODIFY_DESIGN_PROPOSAL` turn. `actions.py::classify_action()`:

```python
if has_active_proposal:
    if _matches_any(text, _ACCEPT_PHRASES):
        return "ACCEPT_PROPOSAL"
    if _matches_any(text, _REJECT_PHRASES):
        return "REJECT_PROPOSAL"
    # Any other substantive text while a proposal is open ... is treated
    # as a correction to it, never a silent second, unrelated change.
    return "MODIFY_DESIGN_PROPOSAL"
```

Any text that isn't an exact accept or reject phrase, while `session.activeProposal.status == "ACTIVE"`, classifies as `MODIFY_DESIGN_PROPOSAL` — this is what CONV-GOV-017 calls "a correction."

`_handle_designer_routed()` then explicitly supersedes the prior proposal *before* calling Designer for the new one:

```python
if session.activeProposal is not None and session.activeProposal.status == "ACTIVE":
    session.activeProposal = session.activeProposal.model_copy(update={"status": "SUPERSEDED"})
```

`session.activeProposal.status` becomes `"SUPERSEDED"` and a brand new `ConversationProposal` (with a new `proposalId`, computed fresh against `request.currentJDL`/`currentDesignIntent`) replaces it once Designer responds.

### Proof: no intermediate mutation

`backend/tests/test_conversation_engine.py::TestCaseF_CorrectionSupersedesWithoutIntermediateMutation::test_four_prongs_correction_replaces_six_prong_proposal` is the real, running proof. A first turn ("Fammi un solitario con sei griffe.") produces a proposal with `setting.prongCount == 6`. A second turn ("No, quattro griffe.") is classified `MODIFY_DESIGN_PROPOSAL` and produces a *new* proposal with `setting.prongCount == 4`. The test's final assertion — `JewelryDefinition().setting.prongCount == 6` — proves the original default definition was never mutated by the superseded six-prong proposal at any point; both proposals were candidate values sitting in `ConversationProposal.designerProposal.candidateJDL`, never applied to any stored design (CONV-GOV-005).

## `REJECT_ACTIVE_PROPOSAL` — implemented, as `REJECT_PROPOSAL`

See [`384-accept-reject-cancel-semantics.md`](384-accept-reject-cancel-semantics.md) for the full `_handle_reject()` semantics: clears `activeProposal`, sets `status="IDLE"`, touches nothing in `acceptedChangeHistory` or `summary.acceptedDecisions` (CONV-GOV-018).

## `REVERT_LAST_ACCEPTED_CHANGE` — not implemented

This is a real, plainly-stated gap, not a capability to imply exists. There is no `ConversationActionType` value for reverting an already-accepted, already-applied change, and no function anywhere in `backend/jewelmind/conversation/` reads `session.acceptedChangeHistory` in order to construct an inverse patch. `CANCEL_INTERACTION` (`_handle_cancel()`) is the closest-sounding action, but its actual effect is limited to *transient* state:

```python
def _handle_cancel(self, turn_id, request, session, now) -> ConversationTurn:
    if session.pendingClarification is not None:
        session.pendingClarification = None
    if session.activeProposal is not None:
        session.activeProposal = None
    session.status = "IDLE"
    return self._make_turn(...)
```

`_handle_cancel()` only ever clears `pendingClarification` and `activeProposal` — a not-yet-accepted question or proposal the user wants to back out of. It never reads or writes `session.acceptedChangeHistory`, and it has no access to (and no way to reconstruct) whatever `currentJDL` looked like before an earlier accepted change was applied on the frontend, because Conversation never stored that value in the first place (CONV-GOV-001/002). "Undo my last accepted change" — meaning "restore the field to what it was before I accepted the last proposal that touched it" — is not something this Sprint can do; a user who wants that must manually re-edit the field, or describe the reversal as a new, ordinary turn (e.g. "change it back to yellow gold"), which is handled as any other `MODIFY_DESIGN_PROPOSAL`, not as an undo.

This gap is tracked, not silently absorbed — see [`404-conversation-gap-analysis-and-open-questions.md`](404-conversation-gap-analysis-and-open-questions.md) and [`370-conversation-governance.md`](370-conversation-governance.md)'s "When an RFC is required" clause (a new conversational capability beyond the 13 current `ConversationActionType` values needs an RFC before implementation).
