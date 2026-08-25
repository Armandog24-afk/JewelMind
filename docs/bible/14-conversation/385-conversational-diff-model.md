---
id: JM-BIBLE-385
title: Conversational Diff Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-CONVERSATION-README
  - JM-BIBLE-370
  - JM-BIBLE-374
related_documents:
  - JM-BIBLE-311
  - JM-BIBLE-386
implementation_status: current
professional_validation: not_required
normative: true
---

# Conversational Diff Model

CONV-GOV-019 cites this document: "Every accepted change is auditable as a structured diff." Both diff-derived fields on `ConversationTurn` — `technicalChanges` and `intentChanges` — are computed purely from `DesignerProposal` fields that Designer itself already produces deterministically. Nothing here is LLM-generated diff text, and nothing is authored by the conversation layer itself.

## `technicalChanges: list[str]`

```python
technical_changes = [d.path for d in proposal.diff if d.changed]
```

(`_resolve_designer_proposal()`, and identically in `_handle_accept()` off `accepted_proposal.designerProposal.diff`). `proposal.diff` is a `list[FieldDiff]` — `FieldDiff{path: str, previousValue, proposedValue, changed: bool}` (`backend/jewelmind/designer/schemas.py`) — Designer's own deterministic, unconditional-since-Sprint-11 diff computation (`normalizer.compute_diff(request.currentJDL, candidate)`, documented in full in [`311-proposal-diff-model.md`](../12-designer/311-proposal-diff-model.md)). Conversation only filters the list down to entries where `changed` is `True` and takes their `path` — it performs no comparison of its own.

## `intentChanges: list[str]`

```python
intent_changes = [f"{s.target}.{s.concept}" for s in proposal.designIntent.statements]
```

`proposal.designIntent.statements` is a `list[IntentStatement]` (`backend/jewelmind/design_intent/schemas.py`), each carrying a real `target: IntentTarget` and `concept: IntentConceptCategory` — again produced entirely inside Designer's `_build_proposal()` call to `build_design_intent()` (Sprint 11's own resolver, see `docs/bible/13-design-intent/331-design-intent-architecture.md`), unrelated to any conversation-specific logic. Note this list is not filtered by "changed" the way `technicalChanges` is — `DesignIntent.statements` doesn't carry a boolean changed flag the way `FieldDiff` does (an `IntentStatement`'s own `resolutionStatus` distinguishes `PRESERVED` from `CONFLICTING`, not "changed from previous"); every statement the resolver returns for this request is included.

## A real example

`specs/conversation/v1/examples/preserve-unspecified-values.json` (CASE D — "Lascia la pietra così e cambia solo il materiale."):

```json
"technicalChanges": ["material.metal"],
"intentChanges": []
```

with the underlying `proposal.diff` showing 22 entries total (the full field set of `JewelryDefinition`), exactly one (`material.metal`, `previousValue: "yellow_gold_18k"`, `proposedValue: "platinum"`, `changed: true`) marked `changed`; every other entry (`project.name`, `ring.size`, `stone.diameter`, `setting.prongCount`, and so on) is present with `changed: false`, `previousValue == proposedValue`. `intentChanges` is empty because this particular request produced no `IntentStatement`s — a purely technical request.

## Why full-diff auditability matters here

`_handle_accept()`'s `session.acceptedChangeHistory`/`session.summary.acceptedDecisions` are built from exactly this same `technical_changes` list, computed off `accepted_proposal.designerProposal.diff` at accept-time. This is the mechanism behind CONV-GOV-019: an audit trail of accepted changes is always a list of real dotted JDL paths that genuinely changed, traced back through `ConversationProposal.designerProposal.diff` to Designer's own deterministic comparison — never a paraphrase of `turn.sourceText`, and never anything the conversation layer invented on its own.
