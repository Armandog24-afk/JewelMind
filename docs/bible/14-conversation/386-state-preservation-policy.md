---
id: JM-BIBLE-386
title: State Preservation Policy
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
  - JM-BIBLE-385
  - JM-BIBLE-391
implementation_status: current
professional_validation: not_required
normative: true
---

# State Preservation Policy

This document is CONV-GOV-006 stated in full. It is the single most safety-critical behavioral guarantee of Sprint 12: **a multi-turn correction must never silently discard a field the user never mentioned.** Without it, "leave the stone as is and change only the material" could — through nothing more than an implementation accident — reset the stone to some default instead of leaving it untouched, and nobody would notice until a manufacturing-review step caught it far too late.

## Conversation never authors its own JDL patch

There is no function anywhere in `backend/jewelmind/conversation/` that constructs a dict of field-path-to-value pairs and applies it to a `JewelryDefinition`. A grep for `model_copy(update=` or dict-based patch construction targeting `JewelryDefinition` in `backend/jewelmind/conversation/*.py` finds none — the only `JewelryDefinition`-shaped values conversation code ever touches are the ones it receives unmodified as `request.currentJDL`/`accepted_proposal.designerProposal.candidateJDL`, both computed elsewhere.

## The real preservation boundary: `DesignerService.interpret()`

Every `MODIFY_DESIGN_PROPOSAL`-routed turn — whether from a fresh correction (`_handle_designer_routed()`) or a resolved clarification answer (`_handle_answer_clarification()`) — calls the exact same function:

```python
self._designer.interpret(NaturalLanguageDesignRequest(
    ..., interactionMode="MODIFY", currentJDL=request.currentJDL,
    currentDesignIntent=request.currentDesignIntent))
```

Field preservation is implemented entirely inside Designer (`backend/jewelmind/designer/service.py`), not inside Conversation, and this boundary is precise, not approximate:

```python
base = (
    JewelryDefinition()
    if request.interactionMode == "CREATE"
    else (request.currentJDL or JewelryDefinition())
)
...
candidate = _apply_patch(base, patch) if patch or request.interactionMode == "CREATE" else base
```

```python
def _apply_patch(base: JewelryDefinition, patch: dict[str, Any]) -> JewelryDefinition | None:
    data = base.model_dump(mode="python")
    for path, value in patch.items():
        section, field_name = path.split(".", 1)
        data.setdefault(section, {})[field_name] = value
    try:
        return JewelryDefinition.model_validate(data)
    except ValidationError:
        return None
```

On `MODIFY`, `base` is the caller's full current definition — not a fresh default. `_apply_patch()` dumps that base to a nested dict and overwrites *only* the specific `section.field` keys present in `patch` (the fields Designer's own field-resolution pipeline actually recognized from the request text); every other key in the dict is left exactly as `base` had it, then the whole thing is re-validated through `JewelryDefinition.model_validate()`. A field the user's turn never mentioned is never a key in `patch`, so it is never touched — preservation here is a direct, structural consequence of `_apply_patch()`'s own logic, not a separate "preserve unspecified fields" step that could be forgotten. `docs/bible/12-designer/298-defaulting-policy.md` states this identically: "an unspecified field simply keeps its current value, because `_apply_patch()` only overwrites paths present in the accepted patch dict."

Conversation's contribution to this guarantee is entirely upstream and entirely negative: it never intercepts, filters, or reconstructs `request.currentJDL` before handing it to Designer, and it never post-processes `candidateJDL` afterward. It passes the caller's `currentJDL` straight through, unmodified, exactly once per call.

## Real generated proof: `specs/conversation/v1/test-vectors/preservation-vectors.json`

Two real, generated vectors:

| `sourceText` | `changedFields` | `unchangedFieldSample` |
|---|---|---|
| "Lascia la pietra così e cambia solo il materiale." | `["material.metal"]` | `["project.name", "project.units", "jewelry.category", "jewelry.style", "ring.sizeSystem"]` |
| "Only change the band width to 3mm." | `["band.width"]` | `["project.name", "project.units", "jewelry.category", "jewelry.style", "ring.sizeSystem"]` |

Both requests, despite naming completely different fields, leave the identical sample of unrelated fields untouched — because preservation doesn't depend on which field was mentioned; it's a property of `_apply_patch()` working off the full base dict every single time.

## Real automated regression proof: CASE A and CASE D

`backend/tests/test_conversation_engine.py`:

- **`TestCaseA_TechnicalModifyPreservesUnrelatedFields`** — a three-turn sequence: create a solitaire in rose gold with six prongs, accept it, then a second, independent turn ("Fallo in platino.") changes only the material. The test asserts `candidate.material.metal == "platinum"` **and** `candidate.setting.prongCount == 6` — the prong count set two turns earlier, through an entirely different proposal that had already been accepted and cleared, survives untouched into the new candidate — plus `r3.turn.technicalChanges == ["material.metal"]`, confirming the diff itself reports exactly one changed field, not an accidental reset of the rest.
- **`TestCaseD_PreserveStoneWhileChangingMaterial`** — a single turn ("Lascia la pietra così e cambia solo il materiale.") asserts `candidate.stone.diameter == default.stone.diameter` and `candidate.stone.depth == default.stone.depth` (both compared against a fresh `JewelryDefinition()`'s own defaults) alongside `candidate.material.metal == "platinum"` — proving the explicit "leave the stone as is" instruction and the implicit preservation mechanism produce the same, correct outcome: the stone fields are simply never part of `patch` at all, so `_apply_patch()` never has the option to touch them, whether or not the user says "leave it" out loud.

## The layer boundary, stated precisely

Field preservation is a Designer-layer guarantee (DESIGNER-GOV rule, reused, not reimplemented) that Conversation depends on and never weakens, duplicates, or works around. If a future change to `_apply_patch()` or Designer's `MODIFY` handling ever altered this guarantee, Conversation would inherit that change automatically and silently — which is exactly the intended coupling: there is meant to be exactly one place in the whole system responsible for "what happens to a field the user didn't mention," and Conversation's job is to never introduce a second one.
