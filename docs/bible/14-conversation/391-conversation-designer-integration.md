---
id: JM-BIBLE-391
title: Conversation-Designer Integration
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-CONVERSATION-README
  - JM-BIBLE-370
related_documents:
  - JM-BIBLE-386
  - JM-BIBLE-390
  - JM-BIBLE-DESIGNER-README
implementation_status: current
professional_validation: not_required
normative: true
---

# Conversation-Designer Integration

`backend/jewelmind/conversation/service.py`'s own module docstring states the relationship this document expands on:

> `ConversationEngine` coordinates interaction state around the existing `DesignerService` (Sprint 10) — it never duplicates Designer's technical extraction, unsupported-feature detection, field provenance, or JDL proposal construction (docs/bible/14-conversation/391-conversation-designer-integration.md).

`docs/bible/12-designer/README.md`'s own "Relationship to Sprint 12" section states the same boundary from Designer's side: "Conversation adds zero duplication of Designer's technical extraction, unsupported-feature detection, field provenance, or JDL proposal construction; it only adds turn history, reference resolution, clarification-thread lifecycle, and proposal staleness on top."

## The two real call sites

Every turn that needs Designer's technical/semantic interpretation reaches it through exactly one of two places in `service.py`, both constructing a `NaturalLanguageDesignRequest` (`backend/jewelmind/designer/schemas.py`) and calling `self._designer.interpret(...)`:

**`_handle_designer_routed()`** — the normal path for `CREATE_DESIGN_PROPOSAL`/`MODIFY_DESIGN_PROPOSAL`-classified turns:

```python
designer_result = self._designer.interpret(
    NaturalLanguageDesignRequest(
        requestId=turn_id,
        text=request.text,
        locale=request.locale,
        interactionMode=interaction_mode,
        currentJDL=request.currentJDL,
        currentDesignIntent=request.currentDesignIntent,
    )
)
```

`interaction_mode` is `"CREATE"` only when `action == "CREATE_DESIGN_PROPOSAL"`; every other case (including a correction to an active proposal) is `"MODIFY"`.

**`_handle_answer_clarification()`** — the path for a resolved clarification answer, constructing the identical request shape with one substitution: `text` becomes `combined_text = f"{thread.question} {request.text}"` (the original question prefixed to the raw answer), and `interactionMode` is fixed to `"MODIFY"`.

Both call sites hand the caller's `request.currentJDL`/`request.currentDesignIntent` straight through, unmodified. No other function in `backend/jewelmind/conversation/` calls `DesignerService.interpret()`.

## What Designer does — unchanged from Sprint 10/11

Everything downstream of `self._designer.interpret(...)` is Designer's own, unmodified pipeline: technical field extraction against the JDL capability set, unsupported-feature detection, field-provenance labeling, `_apply_patch()`-based candidate construction (preserving every field the request didn't touch — see [`386-state-preservation-policy.md`](386-state-preservation-policy.md)), `JewelryDefinition.model_validate()`, and `DesignIntent` extraction via `design_intent/`. Conversation never re-implements, shortcuts, or bypasses any of it — it receives back exactly one `DesignerResult` (specifically its `.proposal: DesignerProposal`) and interprets that structured result, never Designer's internal reasoning or raw provider output.

## What Conversation adds on top

Reading `service.py`, `state.py`, `references.py`, `clarifications.py`, and `actions.py` in full, Conversation's real additions are:

- **Turn history** — `session.turns` accumulates one `ConversationTurn` per `process_turn()` call (`_make_turn()`), recording the classified action, references, technical/intent changes, and result — never Designer's own concern, since a single Designer call has no notion of "turn."
- **Reference resolution** — `references.py::resolve_implicit_target()`/`find_preserve_target()` run on the raw text *before* Designer is ever called, deciding whether a turn needs a `REQUEST_CLARIFICATION` detour (ambiguous pronoun, CONV-GOV-010) or a `PRESERVE_TARGET` no-op (an explicit "leave X as is" with no accompanying change) instead of reaching Designer at all.
- **Clarification-thread lifecycle** — `clarifications.py`'s `open_clarification()`/`try_resolve_answer()`/`close_answered()` manage a `ClarificationThread` that Designer itself has no concept of; Designer only ever sees `proposal.clarificationQuestions` (already Sprint 10's own mechanism) or the combined question-plus-answer text on the follow-up call.
- **Proposal correction/supersession** — `_handle_designer_routed()` marks a still-`ACTIVE` `session.activeProposal` `SUPERSEDED` before requesting a new one (CONV-GOV-017); Designer has no notion of "the previous proposal" across calls, since it is stateless per request.
- **Staleness checking** — `state.is_proposal_stale()` compares a `ConversationProposal`'s `baseDefinitionHash`/`baseIntentHash` against the caller's current values before `_handle_accept()` will treat it as safe to apply (CONV-GOV-008; see [`402-stale-context-and-concurrent-editing.md`](402-stale-context-and-concurrent-editing.md)) — a concept that only exists because Conversation, unlike a single Designer call, spans multiple requests.

## Zero geometry, zero direct Forge calls

Grepping `backend/jewelmind/conversation/*.py` for `cadquery` and for any Forge rule-evaluation entry point (`validate_definition`, `evaluate_rule`, or any import from `jewelmind.validation`) finds no matches anywhere in the package. `conversation/__init__.py`'s own docstring states the same boundary in prose: "it coordinates interaction state (turns, clarifications, proposals) but owns no geometry, no jewelry rules, no JDL semantics, and no intent vocabulary — those remain Forge/JDL/Design-Intent/Designer's job." The only path by which a `candidateJDL` is ever produced is Designer's own `JewelryDefinition.model_validate()` plus whatever Forge evaluation Designer's own pipeline runs internally (unchanged since Sprint 10) — Conversation neither calls Forge directly nor could, since it never imports `jewelmind.validation` or `cadquery` at all. This is CONV-GOV-020 restated with the grep evidence behind it.

## What a `DesignerResult` looks like from Conversation's side

`_resolve_designer_proposal()` is the single function that interprets a `DesignerProposal` returned from either call site and turns it into exactly one of three outcomes: a new `REQUEST_CLARIFICATION` thread (if `proposal.clarificationQuestions` is non-empty), a `REPORT_UNSUPPORTED` turn (if `proposal.unsupportedFeatures` is non-empty and no fields were proposed), or a new `ConversationProposal` wrapping the `DesignerProposal` (`state.make_proposal()`) with `status="ACTIVE"` and the two base hashes captured at that moment. This is the one place Conversation reads into a `DesignerProposal`'s shape — it never mutates the `DesignerProposal` object itself, only wraps it.

## Cross-references

- [`386-state-preservation-policy.md`](386-state-preservation-policy.md) — the full detail of how `_apply_patch()` preserves unspecified fields, a Designer-layer guarantee this document only summarizes.
- [`390-provider-context-contract.md`](390-provider-context-contract.md) — the honest gap that `TurnContext` is never actually threaded into either real Designer call.
- [`395-studio-integration.md`](395-studio-integration.md) — how the frontend consumes the `ConversationResult` this integration produces.
- `docs/bible/12-designer/README.md`'s "Relationship to Sprint 12" section.
