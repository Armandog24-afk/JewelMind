---
id: JM-BIBLE-DESIGN-INTENT-README
title: Design Intent Model v1 — Index
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-JDL-README
  - JM-BIBLE-FORGE-README
  - JM-BIBLE-DESIGNER-README
related_documents:
  - JM-BIBLE-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Design Intent Model v1 — Index

This is **Sprint 11** of the Technical Bible: **Design Intent Model v1**. Design Intent is the formal semantic layer between natural aesthetic language ("delicate", "minimal", "classic", "bold") and JewelMind's deterministic `JewelryDefinition`. Where Designer v1 (Sprint 10) already interpreted *explicit, technical* requests ("rose gold", "six prongs", "2.4 mm band"), Design Intent handles the *subjective* remainder — and its single governing rule is that subjective language may be structured, stored, reviewed, and compared **without ever being numerically resolved**. Like Sprints 8–10, this Sprint ships real code: a new backend package (`backend/jewelmind/design_intent/`), a real extension to Designer's structured-output contract, and a real Studio UI section separating "JewelMind understood" (technical) from "Design intent" (aesthetic).

**Read this README, then [`330-intent-governance.md`](330-intent-governance.md), before changing anything in `backend/jewelmind/design_intent/` or the design-intent parts of `frontend/src/components/DesignerPanel.tsx`.**

## Where Design Intent sits

Design Intent sits between Designer and JDL, and — like Designer — has zero authority to bypass either:

```
USER LANGUAGE
  ↓
DESIGNER
  ↓
DESIGN INTENT MODEL       (this Sprint — structured, preserved, never auto-resolved to a number)
  ↓
INTENT RESOLUTION
  ↓
JDL PROPOSAL
  ↓
JDL VALIDATION
  ↓
FORGE
  ↓
USER ACCEPTANCE
  ↓
ALCHEMIST
  ↓
ATLAS
```

Design Intent is not geometry, not JDL, not a manufacturing rule, and not an LLM response format — it is a JewelMind-owned semantic model. See [`290-designer-governance.md`](../12-designer/290-designer-governance.md) for the sibling Designer rules this Sprint's `330-intent-governance.md` extends.

## The core principle

> Subjective intent may be structured without being numerically resolved.

`band.width = 1.6mm` is never a valid response to "vorrei una fascia delicata" unless the user explicitly supplied `1.6mm`, an accepted deterministic profile defines that exact mapping (none exist in v1 — see [`349-deterministic-resolution-policy.md`](349-deterministic-resolution-policy.md)), or the user explicitly approves a proposed numerical resolution. The valid response is a structured `IntentStatement`: `target: BAND, concept: VISUAL_WEIGHT, value: DELICATE, provenance: AI_NORMALIZED`.

## Reading order

1. [`330-intent-governance.md`](330-intent-governance.md) — 18 non-negotiable rules (INTENT-GOV-001 through 018).
2. [`331-design-intent-architecture.md`](331-design-intent-architecture.md), [`332-intent-domain-model.md`](332-intent-domain-model.md).
3. Vocabulary: [`333-intent-vocabulary.md`](333-intent-vocabulary.md), [`334-intent-target-model.md`](334-intent-target-model.md), [`335-aesthetic-descriptor-model.md`](335-aesthetic-descriptor-model.md).
4. Semantic axes: [`336-relative-proportion-intent.md`](336-relative-proportion-intent.md), [`337-visual-weight-model.md`](337-visual-weight-model.md), [`338-style-continuum-model.md`](338-style-continuum-model.md), [`339-emphasis-and-hierarchy-model.md`](339-emphasis-and-hierarchy-model.md), [`340-symmetry-and-balance-model.md`](340-symmetry-and-balance-model.md), [`341-simplicity-and-complexity-model.md`](341-simplicity-and-complexity-model.md), [`342-classic-contemporary-model.md`](342-classic-contemporary-model.md).
5. Statement metadata: [`343-intent-strength-and-priority.md`](343-intent-strength-and-priority.md), [`344-intent-provenance.md`](344-intent-provenance.md), [`345-intent-confidence.md`](345-intent-confidence.md).
6. Uncertainty: [`346-intent-conflict-model.md`](346-intent-conflict-model.md), [`347-intent-compatibility-model.md`](347-intent-compatibility-model.md).
7. Resolution: [`348-intent-resolution-model.md`](348-intent-resolution-model.md), [`349-deterministic-resolution-policy.md`](349-deterministic-resolution-policy.md), [`350-intent-to-jdl-boundary.md`](350-intent-to-jdl-boundary.md), [`351-intent-to-forge-boundary.md`](351-intent-to-forge-boundary.md), [`352-unresolved-intent-lifecycle.md`](352-unresolved-intent-lifecycle.md).
8. Lifecycle: [`353-intent-preservation.md`](353-intent-preservation.md), [`354-intent-diff-model.md`](354-intent-diff-model.md), [`355-intent-profile-model.md`](355-intent-profile-model.md).
9. Integration: [`356-designer-intent-extraction.md`](356-designer-intent-extraction.md), [`357-studio-intent-review.md`](357-studio-intent-review.md), [`358-intent-diagnostics.md`](358-intent-diagnostics.md).
10. Quality: [`359-intent-evaluation-framework.md`](359-intent-evaluation-framework.md), [`360-intent-test-corpus.md`](360-intent-test-corpus.md), [`361-current-code-mapping.md`](361-current-code-mapping.md).
11. [`362-design-intent-gap-analysis.md`](362-design-intent-gap-analysis.md), [`363-open-design-intent-questions.md`](363-open-design-intent-questions.md).

## Appendices

[`intent-vocabulary-catalog.md`](../appendices/intent-vocabulary-catalog.md), [`intent-target-catalog.md`](../appendices/intent-target-catalog.md), [`intent-relation-catalog.md`](../appendices/intent-relation-catalog.md), [`intent-resolution-catalog.md`](../appendices/intent-resolution-catalog.md), [`intent-conflict-catalog.md`](../appendices/intent-conflict-catalog.md), [`intent-diagnostic-catalog.md`](../appendices/intent-diagnostic-catalog.md), [`intent-test-case-catalog.md`](../appendices/intent-test-case-catalog.md), [`intent-code-mapping.md`](../appendices/intent-code-mapping.md), [`intent-test-matrix.md`](../appendices/intent-test-matrix.md) (`JM-BIBLE-A64` through `A72`, continuing directly from Sprint 10's last appendix, `A63`).

## Machine-readable specification

[`specs/design-intent/v1/`](../../../specs/design-intent/v1/README.md) holds 7 JSON Schemas, a `vocabulary.json` controlled-vocabulary source of truth, 7 examples, and 6 test-vector files, all generated by running the real `build_design_intent()` pipeline — never hand-invented.

## The single most important finding of this Sprint

**Zero automatic subjective-to-numeric mappings exist in v1, and that is the deliberately correct answer, not an unfinished feature.** `docs/bible/13-design-intent/349-deterministic-resolution-policy.md`'s policy requires an intent-to-JDL mapping to be explicit, deterministic, versioned, and reviewed before it can run automatically — no such mapping is registered anywhere in `backend/jewelmind/design_intent/`. Every recognized aesthetic statement resolves to `resolutionStatus: PRESERVED`, verified live by [`specs/design-intent/v1/test-vectors/deterministic-resolution-vectors.json`](../../../specs/design-intent/v1/test-vectors/deterministic-resolution-vectors.json) — a real generated artifact, not a claim. This was also verified negatively: `backend/tests/test_designer_intent_integration.py::TestNoArbitraryNumericMapping` proves that "make the band delicate" never changes `band.width`, and "make it bolder" never increases `band.width`, `stone.diameter`, or `setting.prongDiameter`.

## Relationship to Sprint 10

Design Intent extends Designer's structured-output contract with two new fields (`designIntentStatements`, `designIntentRelations` on `RawDesignerResponse`) and one new proposal field (`designIntent` on `DesignerProposal`) — every Sprint 10 guarantee (JDL/Forge validation, provider abstraction, `FakeDesignerProvider`-only CI, the 108 pre-existing backend tests) is unchanged. See [`356-designer-intent-extraction.md`](356-designer-intent-extraction.md).

## Relationship to Sprint 12

[`14-conversation/`](../14-conversation/README.md) (Sprint 12) routes multi-turn review of Design Intent's own statements through Conversation Engine, via the same Designer pipeline this Sprint already extended — a `ConversationProposal`'s `designerProposal.designIntent` field is the exact, unmodified `DesignIntent` Designer's `build_design_intent()` already produces. Conversation adds zero duplication of Design Intent's own normalization, conflict-detection, or resolution logic: it only adds the `MODIFY_INTENT` action label (assigned when a resolved proposal has intent statements but no changed technical fields) and the guarantee, restated as CONV-GOV-011, that an intent-only accepted change can never mark geometry stale. See [`14-conversation/392-conversation-intent-integration.md`](../14-conversation/392-conversation-intent-integration.md).

## Validation of this sprint

See [`SPRINT-11-VALIDATION-REPORT.md`](SPRINT-11-VALIDATION-REPORT.md) for the checks run against this section and the findings from that pass.
