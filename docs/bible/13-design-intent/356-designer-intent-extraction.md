---
id: JM-BIBLE-356
title: Designer Intent Extraction
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-355
related_documents:
  - JM-BIBLE-357
implementation_status: current
professional_validation: not_required
normative: true
---

# Designer Intent Extraction

## How Sprint 10's Designer was extended

Design Intent does not replace any of Sprint 10's Designer pipeline (`../12-designer/README.md`) — it extends its structured-output contract with new fields that flow through the same request/response cycle.

### `RawDesignerResponse` gained two fields

- `designIntentStatements: list[RawIntentStatement]` — each a provider-facing raw shape: `target`, `concept`, `value`, `strength`, `sourceText`.
- `designIntentRelations: list[RawIntentRelation]` — each: `subject`, `predicate`, `object`, `strength`, `sourceText`.

These are the raw, unvalidated shapes a Designer provider (real or `FakeDesignerProvider`) emits; they are converted into `design_intent.resolver.RawStatementInput`/`RawRelationInput` before normalization.

### `NaturalLanguageDesignRequest` gained `currentDesignIntent`

`currentDesignIntent: DesignIntent | None = None` — parallel to the existing `currentJDL`, used as the `previous` argument to `build_design_intent()` for MODIFY-mode merging (see [`352-unresolved-intent-lifecycle.md`](352-unresolved-intent-lifecycle.md), [`353-intent-preservation.md`](353-intent-preservation.md)).

### `DesignerProposal` gained a required `designIntent` field

`designIntent: DesignIntent` — always present on every proposal, never optional, so the frontend never has to special-case its absence.

### `service.py::_build_proposal()` wiring

Calls `build_design_intent()`, passing the provider's raw statements/relations (converted to `RawStatementInput`/`RawRelationInput`) and `request.currentDesignIntent` as `previous`. Designer's pre-existing Sprint 10 `unresolvedDescriptors` field (top-level free-text the provider couldn't classify at all, distinct from Design Intent's own unresolved concept) is additionally fed into `build_design_intent()`'s `raw_unresolved_descriptors` parameter — so it ends up duplicated into `DesignIntent.unresolvedDescriptors` as well. The old `DesignerProposal.unresolvedIntent` field (Sprint 10) is kept unchanged, purely for backward compatibility, and is not deprecated by this Sprint.

### The prompt's technical/aesthetic split

`designer/prompts.py`'s `SYSTEM_CONTRACT` gained an explicit "PART 1 — TECHNICAL FIELDS" / "PART 2 — AESTHETIC DESIGN INTENT" split, plus `build_intent_vocabulary_block()` (embeds the real target/concept/continuum/predicate vocabulary as prompt context) and `build_current_intent_block()` (shows previously-preserved intent to the provider in MODIFY mode, for context only). The merge itself remains 100% deterministic Python inside `resolver.py` — the LLM never performs the MODIFY-mode merge; it only sees prior intent as context for producing a better next set of raw statements.

## The worked example from the brief

"Fammi un solitario delicato in oro rosa con sei griffe." produces two structurally separate outputs from the same request:

- **Technical** (`proposedFields`): `material=rose_gold_18k`, `prongCount=6`.
- **Design Intent** (`designIntent.statements`): `target=RING, concept=VISUAL_WEIGHT, value=DELICATE`.

Critically: this does **not** create a smaller band automatically. "Delicate" produces only the `VISUAL_WEIGHT` statement above — it never writes to `band.width` or any other dimension. This exact prohibition is what `backend/tests/test_designer_intent_integration.py::TestNoArbitraryNumericMapping` proves directly, including the specific "delicate never touches `band.width`" and "bolder never increases `band.width`/`stone.diameter`/`setting.prongDiameter`" cases named in this Sprint's own brief, and is reinforced by the corpus's dedicated `NO_ARBITRARY_NUMERIC_MAPPING` category (10 cases — see [`360-intent-test-corpus.md`](360-intent-test-corpus.md)).

## Cross-references

- [`330-intent-governance.md`](330-intent-governance.md) — INTENT-GOV-001, INTENT-GOV-003, INTENT-GOV-016, INTENT-GOV-017.
- `../12-designer/README.md`, `../12-designer/303-field-provenance-model.md` — the Sprint 10 pipeline this extends.
- [`350-intent-to-jdl-boundary.md`](350-intent-to-jdl-boundary.md) — why the two channels stay structurally disjoint.
- [`357-studio-intent-review.md`](357-studio-intent-review.md) — how this reaches the user.
