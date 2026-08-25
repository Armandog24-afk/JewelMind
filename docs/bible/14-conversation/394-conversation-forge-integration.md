---
id: JM-BIBLE-394
title: Conversation Forge Integration
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-CONVERSATION-README
  - JM-BIBLE-370
  - JM-BIBLE-FORGE-README
related_documents:
  - JM-BIBLE-391
  - JM-BIBLE-393
implementation_status: current
professional_validation: not_required
normative: true
---

# Conversation Forge Integration

## Conversation performs zero Forge calls of its own

Grepping `backend/jewelmind/conversation/` for any import of `jewelmind.validation` (Forge's package), `cadquery`, or any function resembling rule evaluation finds no matches — `__init__.py`'s own module docstring states the boundary directly: "it owns no geometry, no jewelry rules, no JDL semantics, and no intent vocabulary — those remain Forge/JDL/Design-Intent/Designer's job." This is not merely a stated intention; it is verifiably true of the real code: no file under `backend/jewelmind/conversation/` imports `jewelmind.validation.engine`, `jewelmind.validation.rules`, or `cadquery`.

## Every candidate proposal is still Forge-validated — by Designer, unchanged

Every `ConversationProposal.designerProposal` is a real `DesignerProposal` (`backend/jewelmind/designer/schemas.py`), and that type's `validation: list[ValidationResult]` and `forgeEvaluation: ForgeEvaluationSummary | None` fields are populated exactly as they always have been by `DesignerService.interpret()` — Designer's own `_build_proposal()` still runs `JewelryDefinition.model_validate()` and the real Forge rule engine (`jewelmind.validation.engine.validate_definition()`) before returning a proposal, regardless of whether the caller is the single-turn `/api/designer/interpret` route or Conversation's `/api/conversation/turn` route. `_handle_designer_routed()` and `_handle_answer_clarification()` both call `self._designer.interpret(...)` and pass the raw `DesignerResult.proposal` straight through to `state.make_proposal()` — Conversation reads `proposal.validation`/`proposal.forgeEvaluation` (indirectly, via `technical_changes = [d.path for d in proposal.diff if d.changed]`, which only exists because Designer already computed a validated diff) but never recomputes, overrides, or bypasses either.

## No Forge bypass exists

There is no code path in `conversation/` that constructs a `candidateJDL` and returns it to the caller without having gone through `DesignerService.interpret()` first — `ACCEPT_PROPOSAL` (`_handle_accept()`) only ever operates on `session.activeProposal`, which can only have been set by `_resolve_designer_proposal()` from a real `designer_result.proposal`. There is no "quick accept" or "skip validation" action among the 13 `ConversationActionType` values, and no conversational action mutates `candidateJDL`, `diff`, `validation`, or `forgeEvaluation` after Designer produces them.

## Cross-references

- [`391-conversation-designer-integration.md`](391-conversation-designer-integration.md) — the shared call path this document's finding depends on.
- `docs/bible/06-forge/README.md` and `docs/bible/12-designer/` — Forge's own validation pipeline, unchanged by this Sprint.
- CONV-GOV-020 in [`370-conversation-governance.md`](370-conversation-governance.md) — the rule this document is direct evidence for.
