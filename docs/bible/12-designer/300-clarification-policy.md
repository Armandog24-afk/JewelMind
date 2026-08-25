---
id: JM-BIBLE-300
title: Clarification Policy
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-299
related_documents:
  - JM-BIBLE-301
implementation_status: current
professional_validation: not_required
normative: true
---

# Clarification Policy

## When a `ClarificationQuestion` is warranted

Three real conditions in `service.py::_build_proposal()` produce one:

1. **A term is ambiguous among known values** — `normalize_enum_token()` returns `is_ambiguous=True` (the deterministic metal backstop) or the provider reports a `RawAmbiguity` for a known field. The question always lists the real candidate values as `options` (e.g. every currently-supported metal for a bare "gold").
2. **A provider proactively identifies missing information with no sanctioned default** — `RawClarification{field, question, options}`, folded in as-is with `ambiguityLevel` set to `HIGH_IMPACT_AMBIGUITY` if it has options, `UNSUPPORTED_AMBIGUITY` if not.
3. **An unsupported feature has no clarification path** — notably, `detectedUnsupportedFeatures` does **not** generate a `ClarificationQuestion` in current code; it only ever becomes an `UnsupportedFeature` entry. A clarification is reserved for genuine ambiguity among *supported* options, not for negotiating around something JewelMind simply doesn't build yet.

## One batch, not sequential micro-questions

Designer is a single, stateless request/response cycle (see [`292-natural-language-input-contract.md`](292-natural-language-input-contract.md)) — there is no mechanism for it to ask one question, wait, and ask a follow-up informed by the answer within the same interpretation. In practice this means every `interpret()` call surfaces **all** clarifications that request's raw response produced, at once, in `DesignerProposal.clarificationQuestions`. `DesignerPanel.tsx` renders every one of them together under "A few questions," each with its own option buttons.

This is a deliberate simplification, not an oversight: batching every question the pipeline found in one pass is strictly better than an artificial one-at-a-time conversation Designer's stateless architecture doesn't actually support.

## How an answer is "submitted"

There is no structured answer format. Clicking a clarification's option button (`DesignerPanel.tsx::handleClarify()`) appends the option text to the existing free-text field and immediately fires a brand-new `POST /api/designer/interpret` with the combined text — the same deterministic pipeline reprocesses the whole thing from scratch. `FieldProvenance.CLARIFICATION_RESPONSE` exists in the schema for a value that arrives this way, but nothing in `service.py` currently assigns it distinctly from `AI_INTERPRETATION` — a clarified answer, once re-submitted, is processed exactly like any other proposed value, with `AI_INTERPRETATION` provenance. This is a real gap between the provenance enum's intent and the current implementation; see [`303-field-provenance-model.md`](303-field-provenance-model.md) and [`321-designer-gap-analysis.md`](321-designer-gap-analysis.md).

## `NEEDS_CLARIFICATION` blocks Apply

Any non-empty `clarificationQuestions` list forces `proposalStatus: "NEEDS_CLARIFICATION"`, and `DesignerPanel.tsx`'s "Apply proposal" button is disabled specifically when `proposal.proposalStatus === 'NEEDS_CLARIFICATION'` — a user cannot accidentally apply a proposal while an open question remains.

See [`301-unsupported-request-handling.md`](301-unsupported-request-handling.md) for the sibling case of a feature with no supported value at all.
