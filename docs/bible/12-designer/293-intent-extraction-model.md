---
id: JM-BIBLE-293
title: Intent Extraction Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-292
related_documents:
  - JM-BIBLE-294
implementation_status: current
professional_validation: not_required
normative: true
---

# Intent Extraction Model

## Two kinds of extractable content

Every raw provider response (`RawDesignerResponse`) separates what it found into two fundamentally different buckets:

1. **Mappable intent** — a value for one of the 19 known JDL field paths (see [`295-designer-to-jdl-contract.md`](295-designer-to-jdl-contract.md)), carried as `proposedCanonicalValues`.
2. **Non-mappable descriptive intent** — language that describes a feeling, style, or quality with no deterministic mapping to a CAD parameter today, carried verbatim as `unresolvedDescriptors` and surfaced to the user as `DesignerProposal.unresolvedIntent`.

There is no third bucket. A provider is instructed (`prompts.py::SYSTEM_CONTRACT`) to "preserve non-technical descriptive language (e.g. 'delicate', 'bold', 'elegant') in unresolvedDescriptors verbatim — never convert it into a numeric dimension."

## Real corpus examples

`backend/tests/test_designer_corpus.py` includes cases where a request like *"Voglio un anello delicato ed elegante"* (Italian) or an English equivalent produces zero `proposedCanonicalValues` for the aesthetic words and instead reports them via `unresolvedDescriptors`, asserted with the `has_unresolved(text)` helper. "Delicate" and "elegante" are real words that appear in the corpus specifically because they have no honest mapping — there is no rule anywhere in this codebase that says "delicate" means a 1.4mm band, and CLAUDE.md and DESIGNER-GOV-006/298's defaulting policy both forbid inventing one.

## Why this split matters

If Designer silently dropped unmappable language, a user could reasonably believe their described intent was captured when it wasn't. Surfacing it as `unresolvedIntent` — rendered in the DesignerPanel's "Not yet mapped to a technical parameter" section — is the honest alternative: the user sees exactly what was and wasn't turned into a parameter.

## Multi-field extraction

A single request routinely produces several `proposedCanonicalValues` entries at once (the corpus's `MULTI_FIELD` category exercises this) — e.g. a metal, a prong count, and a band profile from one sentence. Each is tagged independently with its own provenance and confidence; there is no cross-field dependency logic (no rule that changing `material.metal` implies anything about `band.width`).

## The boundary with Sprint 11

A future **Design Intent Model** (already scoped for Sprint 11) is meant to give some of this descriptive language a formal semantic representation — without ever converting it into an arbitrary CAD dimension. Until that lands, `unresolvedDescriptors`/`unresolvedIntent` is the entire treatment: text is preserved, never approximated. See [`321-designer-gap-analysis.md`](321-designer-gap-analysis.md).

See [`294-design-proposal-model.md`](294-design-proposal-model.md) for how both buckets are assembled into the full proposal shape.
