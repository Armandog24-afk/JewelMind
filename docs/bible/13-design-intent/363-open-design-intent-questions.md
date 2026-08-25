---
id: JM-BIBLE-363
title: Open Design Intent Questions
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-362
related_documents:
  - JM-BIBLE-DESIGN-INTENT-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Open Design Intent Questions

These are open product and policy questions raised while building Sprint 11, not decisions. None are answered by this document — each requires either a product decision, an RFC, or an ADR per [`330-intent-governance.md`](330-intent-governance.md) before being acted on.

1. **Which intent concepts deserve canonical status going forward?** The current 6 `IntentConceptCategory` values (`VISUAL_WEIGHT`, `SIMPLICITY`, `STYLE_TEMPORALITY`, `VISUAL_EMPHASIS`, `PROPORTIONAL_CHARACTER`, `STRUCTURAL_CHARACTER`) were chosen for this Sprint's scope — is this the right permanent set, or should it grow, and by what governance?
2. **Should aesthetic axes stay ordinal/categorical only, or could some become continuous later?** `IntentStatement.value` is a free string today constrained by vocabulary — a continuous "delicateness" score is a materially different model with different resolution implications.
3. **Should users see unresolved intent permanently, or should it eventually expire?** [`352-unresolved-intent-lifecycle.md`](352-unresolved-intent-lifecycle.md) documents that entries never expire or get re-attempted today — is that the right permanent behavior, or a temporary limitation?
4. **Should intent be exported with the project JSON?** [`353-intent-preservation.md`](353-intent-preservation.md) documents that it currently is not.
5. **Should JDL eventually contain an optional intent-metadata block?** This Sprint's brief explicitly says not to inject non-JDL fields into canonical JDL unless JDL itself evolves to support metadata — would that evolution happen in `specs/jdl/v1/`, and under what versioning?
6. **Should profiles belong to Forge, Designer, or a separate system?** `IntentProfile` lives in `design_intent/schemas.py` today, but its `jdlMapping` output and `professionalReview` field overlap conceptually with both Forge's rule-provenance model and Designer's proposal pipeline.
7. **How should brand-specific design language work?** A studio or brand wanting its own "delicate" to mean something numerically specific would need some form of scoped, versioned profile — see gap analysis, "Brand style profiles."
8. **How should two conflicting intents eventually be ranked or resolved,** beyond simply being flagged? `conflicts.py` detects and labels conflicts (`CONFLICTING` status); it does not yet propose a resolution or a precedence rule.
9. **Should AI ever propose technical resolutions for explicit user approval?** This is the `USER_CONFIRMATION` path named in [`350-intent-to-jdl-boundary.md`](350-intent-to-jdl-boundary.md) — conceptually allowed by policy, never implemented.
10. **How many alternative resolutions should be offered, if that path is ever built?** One canonical suggestion, or several ranked options?
11. **Should intent satisfaction eventually be measurable,** beyond the proxy corpus metrics in [`359-intent-evaluation-framework.md`](359-intent-evaluation-framework.md)? What would a ground truth for "this model actually reads as delicate" even be?
12. **Can visual rendering (Vision, Sprint 8) assist intent verification?** Could a rendered Presentation-view image ever be compared against an intent statement, even informally — and if so, by what mechanism that doesn't violate VISION-GOV-012/013 (`../10-vision/220-vision-governance.md`)?
13. **How should future reference images influence intent?** Would an uploaded reference photo produce `IntentStatement`s through some new extraction path, and how would that path be kept as disciplined about false numeric resolution as the current text path is?

## Cross-references

- [`330-intent-governance.md`](330-intent-governance.md) — the governance process any answer to these questions must go through.
- [`362-design-intent-gap-analysis.md`](362-design-intent-gap-analysis.md) — the gaps these questions are drawn from.
- `../12-designer/322-open-designer-questions.md` — the Sprint 10 sibling this document follows in structure.

Sprint 12 — Conversation Engine v1 — structured multi-turn clarification and design refinement, maintaining design state, intent state and unresolved questions without turning JewelMind into an unconstrained chatbot.
