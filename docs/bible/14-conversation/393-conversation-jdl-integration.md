---
id: JM-BIBLE-393
title: Conversation JDL Integration
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-CONVERSATION-README
  - JM-BIBLE-370
  - JM-BIBLE-JDL-README
related_documents:
  - JM-BIBLE-391
  - JM-BIBLE-392
implementation_status: current
professional_validation: not_required
normative: true
---

# Conversation JDL Integration

## Conversation never constructs a JDL patch itself

Grepping `backend/jewelmind/conversation/` for `SET_FIELD`, `PRESERVE_FIELD`, `RESET_FIELD_TO_SYSTEM_DEFAULT`, and `REMOVE_OPTIONAL_FIELD` — the field-operation vocabulary the original Sprint 12 brief proposed as a possible primitive set for representing a conversational JDL edit — finds no matches anywhere in the package. No such vocabulary exists in the real implementation. There is also no direct field assignment onto a `JewelryDefinition` anywhere in `conversation/`; the package never imports `jewelmind.domain.schema.JewelryDefinition` for construction, only as a type annotation on request/response fields it passes through unchanged.

Every `candidateJDL` a `ConversationProposal` ever carries is `proposal.candidateJDL` — Designer's own already-computed, already-validated field — from the same `DesignerProposal` object returned by `DesignerService.interpret()`. Conversation reads `proposal.diff` (Designer's own `FieldDiff` list) to build `technicalChanges`; it never writes to `candidateJDL` or `diff` itself.

## Why: `interactionMode` already provides the preservation guarantee

The Sprint 12 brief's proposed operation vocabulary would have existed to guarantee "preserve everything the user didn't mention." That guarantee already exists one layer down, in Designer's own `interactionMode: "CREATE" | "MODIFY"` split (`designer/service.py`, Sprint 10): a `MODIFY`-mode request is built against `request.currentJDL` and Designer's own normalizer/merge logic preserves every field the raw text didn't touch. `_handle_designer_routed()` sets `interaction_mode = "CREATE" if action == "CREATE_DESIGN_PROPOSAL" else "MODIFY"` — every conversational correction, follow-up, or clarification-driven change routes through `MODIFY`, inheriting Designer's existing preservation guarantee rather than needing a second one built on top.

## Verified live: CASE A and `preservation-vectors.json`

`backend/tests/test_conversation_engine.py::TestCaseA_TechnicalModifyPreservesUnrelatedFields` sends a first turn producing `material.metal` and `setting.prongCount`, accepts it, then sends `"Fallo in platino."` against the accepted JDL and asserts `candidate.setting.prongCount == 6` — untouched by the second, unrelated request — and `r3.turn.technicalChanges == ["material.metal"]` exactly. `specs/conversation/v1/test-vectors/preservation-vectors.json` is the same property captured as generated test-vector data across further scenarios.

## A deliberate simplification, not a hidden gap

This is a real, deliberate simplification from the original brief's proposed design, not an oversight: building a second field-operation abstraction inside `conversation/` that duplicates what `interactionMode` already guarantees would violate this Bible's own "avoid broad unrelated refactors" and DRY discipline, and would create exactly the kind of second source of truth CONV-GOV-001/002/006 exist to prevent. If a future need arises that `interactionMode`'s binary CREATE/MODIFY split genuinely cannot express — e.g. a conversational "reset this one field to its system default" request distinct from "the user didn't mention it" — that would be a legitimate reason to reconsider a dedicated operation vocabulary, but it does not exist as a requirement today, and no code path in the corpus (`test_conversation_corpus.py`) or CASE A–F exercises one.

## Cross-references

- [`391-conversation-designer-integration.md`](391-conversation-designer-integration.md) — the shared Designer call path.
- [`392-conversation-intent-integration.md`](392-conversation-intent-integration.md) — the parallel intent-side integration document.
- `docs/bible/12-designer/295-designer-to-jdl-contract.md` and the `MODIFY` interaction-mode preservation guarantee it documents.
- CONV-GOV-006, CONV-GOV-020 in [`370-conversation-governance.md`](370-conversation-governance.md).
