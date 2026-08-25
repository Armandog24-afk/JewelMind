---
id: JM-BIBLE-292
title: Natural Language Input Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-291
related_documents:
  - JM-BIBLE-293
implementation_status: current
professional_validation: not_required
normative: true
---

# Natural Language Input Contract

## `NaturalLanguageDesignRequest`, field by field

`backend/jewelmind/designer/schemas.py::NaturalLanguageDesignRequest` (`extra="forbid"` via the shared `DesignerModel` base — an unknown field is a 422, never silently ignored):

| Field | Type | Constraint | Purpose |
|---|---|---|---|
| `requestId` | `str` | 1–100 chars | Caller-supplied correlation id; not validated for uniqueness server-side. |
| `text` | `str` | 1–2000 chars | The user's natural-language description or change request. |
| `locale` | `"it" \| "en" \| None` | optional | A hint only — see [`297-supported-language-scope.md`](297-supported-language-scope.md); normalization does not depend on it being set correctly. |
| `interactionMode` | `"CREATE" \| "MODIFY"` | required, default `"CREATE"` | Whether this describes a new design or a change to an existing one. |
| `currentJDL` | `JewelryDefinition \| None` | optional | The full current design, required in practice for a meaningful `MODIFY`. |

## Why this is stateless

Designer holds no server-side session, no conversation history, and no per-user memory. Every field the interpretation needs — including the entire current design for a `MODIFY` — travels in the request body every time. `frontend/src/components/DesignerPanel.tsx` reflects this directly: `interpretDesignRequest()` is called with `currentJDL: mode === 'MODIFY' ? currentDefinition : null` on every submit, including the follow-up call `handleClarify()` triggers when a user clicks a clarification option — that follow-up is a brand-new `POST /api/designer/interpret`, not a continuation of a prior one.

This has a real consequence: a `ClarificationQuestion` answer is not "remembered" as a structured answer. Clicking a clarification option button appends the option text to the free-text field and re-submits the whole thing, letting the same deterministic pipeline reprocess it as ordinary input. There is no separate wire format for "this text answers question X."

## CREATE vs. MODIFY, exactly as resolved

`DesignerService.interpret()`:

```python
base = (
    JewelryDefinition()
    if request.interactionMode == "CREATE"
    else (request.currentJDL or JewelryDefinition())
)
```

A `MODIFY` request with no `currentJDL` silently falls back to schema defaults rather than erroring — this is a deliberate simplification, not a validated design decision; see `DESIGNER-OQ` candidates in [`322-open-designer-questions.md`](322-open-designer-questions.md) for whether that should instead be a hard error.

## What text is not

`text` is never treated as a command to the backend, a script, or an instruction to Designer's own behavior beyond "interpret this as a jewelry description." See [`313-designer-security-model.md`](313-designer-security-model.md) for how the same instruction-source-boundary discipline used everywhere else in JewelMind applies to this field specifically.

See [`293-intent-extraction-model.md`](293-intent-extraction-model.md) for what `text` is actually parsed into.
