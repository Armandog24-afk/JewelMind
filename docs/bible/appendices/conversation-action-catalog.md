---
id: JM-BIBLE-A73
title: "Appendix: Conversation Action Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-CONVERSATION-README
  - JM-BIBLE-370
related_documents:
  - JM-BIBLE-CONVERSATION-README
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Conversation Action Catalog

The 13 `ConversationActionType` values (`backend/jewelmind/conversation/schemas.py`). "Where classified" names the real function/file that actually assigns the value to a turn — several of the 13 are never assigned by `classify_action()` itself (`backend/jewelmind/conversation/actions.py`) but by `ConversationEngine` in `service.py` after routing to Designer. Trigger phrases are quoted verbatim from the real frozensets/tuples in `actions.py`, not paraphrased.

| Action | Meaning | Where classified (function/file) | Example trigger |
|---|---|---|---|
| `CANCEL_INTERACTION` | Unconditionally clears any pending clarification/active proposal — the safety-valve "undo," wins even over an open clarification or proposal. | `classify_action()` (`actions.py`), `_UNDO_MARKERS` branch — checked first, before every other branch | `"undo"`, `"annulla l'ultima"`, `"revert"` |
| `ANSWER_CLARIFICATION` | The turn is offered as a candidate answer to the one currently `OPEN` `ClarificationThread`. | `classify_action()` (`actions.py`), `has_clarification` branch — takes priority over accept/reject phrasing per CONV-GOV-007 | Any text while a thread is open, e.g. `"2.8 mm"` |
| `ACCEPT_PROPOSAL` | The active proposal is confirmed for the caller to apply. | `classify_action()` (`actions.py`), `_ACCEPT_PHRASES` branch (only reachable when `has_active_proposal`) | `"ok"`, `"okay"`, `"va bene"`, `"perfetto"`, `"accetta"`, `"apply"`, `"applica"`, `"yes"`, `"si"`, `"sì"`, `"d'accordo"`, `"accept"`, `"conferma"`, `"confirm"` |
| `REJECT_PROPOSAL` | The active proposal is discarded without mutating anything. | `classify_action()` (`actions.py`), `_REJECT_PHRASES` branch (only reachable when `has_active_proposal`) | `"no"`, `"annulla"`, `"cancel"`, `"lascia perdere"`, `"non farlo"`, `"rifiuta"`, `"reject"`, `"no grazie"` |
| `MODIFY_DESIGN_PROPOSAL` | A correction to the active proposal, or (with no proposal/clarification pending) an ordinary new design request routed to Designer with `interactionMode="MODIFY"`. | `classify_action()` (`actions.py`) — either the `has_active_proposal` fallback (any non-accept/reject text) or the final default-return line | Any substantive text, e.g. `"No, quattro griffe."`, `"Fallo in platino."` |
| `CREATE_DESIGN_PROPOSAL` | Starts a fresh design from scratch, routed to Designer with `interactionMode="CREATE"`. | `classify_action()` (`actions.py`), `_START_OVER_MARKERS` branch | `"start over"`, `"from scratch"`, `"ricomincia"`, `"da zero"`, `"ricominciamo"` |
| `PRESERVE_TARGET` | A short "leave/keep X as is" phrase naming an explicit target — resolved without ever calling Designer. | `classify_action()` (`actions.py`), short-message + `find_preserve_target()` branch; also re-derived directly inside `ConversationEngine._handle_designer_routed()` (`service.py`) as its own early-exit check | `"leave the stone as is"`, `"lascia la pietra così"` (must be <= 6 words and name an explicit target) |
| `NO_CHANGE` | An acknowledgment when nothing is pending — a genuine no-op. | `classify_action()` (`actions.py`), `_NOOP_PHRASES` branch (only reachable when neither a clarification nor an active proposal is pending) | `"ok"`, `"okay"`, `"va bene"`, `"perfetto"`, `"lascia tutto così"`, `"fine"`, `"alright"`, `"good"`, `"lascia perdere"`, `"never mind"`, `"nevermind"` |
| `REQUEST_CLARIFICATION` | A new `ClarificationThread` is opened — either because a reference was ambiguous, or because Designer itself returned `clarificationQuestions`. | `ConversationEngine._handle_designer_routed()` and `ConversationEngine._resolve_designer_proposal()` (`service.py`) — never `classify_action()` | N/A — an outcome of routing, not a phrase match |
| `REPORT_UNSUPPORTED` | Designer detected a feature the schema/geometry doesn't support, and no technical fields were proposed alongside it. | `ConversationEngine._resolve_designer_proposal()` (`service.py`) — never `classify_action()` | N/A — an outcome of Designer's response, not a phrase match |
| `MODIFY_INTENT` | Overrides the routed action label when a resolved proposal has design-intent statements but zero technical `diff` entries. | `ConversationEngine._resolve_designer_proposal()` (`service.py`): `"MODIFY_INTENT" if not technical_changes and intent_changes else action` | N/A — a post-hoc relabeling of a `MODIFY_DESIGN_PROPOSAL`/`CREATE_DESIGN_PROPOSAL`-routed turn, e.g. `"Fallo più minimal."` |
| `ADD_INTENT` | Schema-defined outcome for adding a new intent statement independent of a technical proposal. | **Unreachable.** Confirmed by grep: no assignment to this literal exists anywhere in `backend/jewelmind/conversation/`. | N/A |
| `REMOVE_INTENT` | Schema-defined outcome for removing an existing intent statement. | **Unreachable.** Confirmed by grep: no assignment to this literal exists anywhere in `backend/jewelmind/conversation/`. | N/A |

## Notes grounded in the real code

- `ADD_INTENT` and `REMOVE_INTENT` are real `Literal` members of `ConversationActionType` and appear in the machine-readable schema (`specs/conversation/v1/conversation-action.schema.json`), but `classify_action()` never returns either, and no handler in `service.py` ever assigns either as `interpretedAction`. Every intent-only change today is represented as `MODIFY_INTENT` — the generic override in `ConversationEngine._resolve_designer_proposal()` that fires whenever a resolved proposal has `designIntent.statements` but no changed technical `diff` entries, regardless of whether the underlying change is conceptually an add, a modify, or a remove. There is no code path in this Sprint that distinguishes "add a new intent statement" from "change an existing one" at the action-classification level.
- `REQUEST_CLARIFICATION` and `REPORT_UNSUPPORTED` are both real, reachable outcomes, but neither is a `classify_action()` return value — they are consequences of what `DesignerService.interpret()` returns (a clarification question, or an unsupported-feature-only response) once a turn has already been routed to Designer as `MODIFY_DESIGN_PROPOSAL`/`CREATE_DESIGN_PROPOSAL`.
