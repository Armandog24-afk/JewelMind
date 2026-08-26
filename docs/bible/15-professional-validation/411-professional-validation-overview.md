---
id: JM-BIBLE-411
title: Professional Validation Overview
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-410
related_documents:
  - JM-BIBLE-412
  - JM-BIBLE-058
  - JM-BIBLE-103
implementation_status: current
professional_validation: not_required
normative: false
---

# Professional Validation Overview

This document restates, in narrative form, the conceptual model that [`README.md`](README.md) and [`410-validation-governance.md`](410-validation-governance.md) already establish as binding. It adds no new rule of its own — every claim here traces back to a PROVAL-GOV rule or a real file already cited in those two documents.

## The fundamental principle, restated

> Professional validation is versioned evidence. It is never a generic label.

A sentence like *"the band width rule is professionally validated"* is not a valid statement in this framework, under any circumstance, because it names no object version, no reviewer, no scope, no evidence, and no date. The only valid form is the one [`README.md`](README.md) already gives: *"Forge rule JM-XYZ version 1.2.0 was reviewed on YYYY-MM-DD by reviewer R under lost-wax casting scope for a specified alloy/process context and accepted with conditions C."* Every document from [`412-validation-object-model.md`](412-validation-object-model.md) through [`418-validation-decision-model.md`](418-validation-decision-model.md) exists to define one part of that sentence precisely enough that it can be represented as data (`ValidationRecord`, `backend/jewelmind/professional_validation/schemas.py`) rather than prose.

## The three-layer distinction

This Sprint's single most important structural rule, stated in full here because it governs every document that follows it in the reading order:

1. **AUTOMATED VALIDATION** — the JDL/Forge/Atlas checks that already run inside JewelMind today: `backend/jewelmind/domain/schema.py` structural validation, `backend/jewelmind/validation/engine.py` Forge rules (21 rules, `specs/forge/v1/current-rule-registry.json`), and Atlas geometry inspection. These run automatically, on every request, and answer *"does this JDL document pass JewelMind's own preliminary software rules?"* They involve no human reviewer.

2. **PROFESSIONAL VALIDATION** — the subject of this Sprint. A real, identifiable jewelry professional reviews a specific, versioned object (a Forge rule, a geometry component, a manufacturing assumption, and so on) under a defined scope, produces evidence, and records a decision (`ValidationRecord`, [`418-validation-decision-model.md`](418-validation-decision-model.md)). It answers *"has a qualified human professional actually looked at this specific claim, and what did they conclude?"* — a question automated validation cannot answer about itself.

3. **CASE-SPECIFIC MANUFACTURING APPROVAL** — the final human decision to actually produce one specific physical piece from one specific generated model. This is outside JewelMind's scope entirely; it belongs to whoever is responsible for a real production run, using their own judgment about that specific case, on that specific day, with that specific customer or workshop. A `ValidationRecord` with `status: VALIDATED` never substitutes for this — see PROVAL-GOV-020 and [`421-manufacturing-validation-process.md`](421-manufacturing-validation-process.md).

**These three layers must never be merged** — not in `backend/jewelmind/`, not in `frontend/src/`, not in any Bible document, and not in any user-facing copy. A passing Forge rule (layer 1) is not evidence of layer 2. A `VALIDATED` `ValidationRecord` (layer 2) is not layer 3's sign-off for an actual order. Conflating any two of these is exactly the failure mode CLAUDE.md's "Never claim manufacturing readiness" rule and PROVAL-GOV-020 both exist to prevent.

## Claude Code is not a jewelry professional reviewer

Restated from [`README.md`](README.md) because it is easy to forget mid-implementation: nothing about writing this framework's code, its tests, or this Bible section constitutes an act of professional validation. An AI agent's assessment that a rule "looks reasonable" is not admissible as `ValidationEvidence` under any `EvidenceType` this framework defines, and can never move a `ValidationRecord.status` toward `VALIDATED` (PROVAL-GOV-005/006/007).

## What this framework answers

The Professional Validation Framework exists to give a structured, versioned answer to each of the following questions — every one of them was previously either unanswered or answered only informally in [`058-professional-validation-register.md`](../04-jewelry-domain/058-professional-validation-register.md) and [`103-professional-validation-lifecycle.md`](../06-forge/103-professional-validation-lifecycle.md):

1. What kinds of things in JewelMind need professional validation at all? — [`412-validation-object-model.md`](412-validation-object-model.md).
2. Which type of expert is the right reviewer for a given object? — [`413-reviewer-role-model.md`](413-reviewer-role-model.md).
3. What does it mean for a specific person to be qualified to review a specific thing? — [`414-reviewer-qualification-model.md`](414-reviewer-qualification-model.md).
4. What evidence is actually captured during a review, and how is its quality classified? — [`417-review-evidence-model.md`](417-review-evidence-model.md), [`440-evidence-quality-model.md`](440-evidence-quality-model.md).
5. How is a Forge rule reviewed, specifically? — [`419-rule-validation-process.md`](419-rule-validation-process.md).
6. How is a geometry component or relationship reviewed? — [`420-geometry-validation-process.md`](420-geometry-validation-process.md).
7. How is a manufacturing-context assumption reviewed? — [`421-manufacturing-validation-process.md`](421-manufacturing-validation-process.md).
8. What does "validated" actually mean, precisely, as opposed to "reviewed" or "accepted"? — [`418-validation-decision-model.md`](418-validation-decision-model.md), `ValidationStatus` in `schemas.py`.
9. How is a validation scoped so it does not silently overreach? — [`415-validation-scope-model.md`](415-validation-scope-model.md).
10. How are disagreements between two qualified reviewers handled? — [`430-professional-disagreement-model.md`](430-professional-disagreement-model.md).
11. How are conditional approvals recorded, so the conditions are never lost? — [`431-conditional-acceptance-model.md`](431-conditional-acceptance-model.md).
12. When does a validation expire or require re-review? — [`433-validation-expiration-and-revalidation.md`](433-validation-expiration-and-revalidation.md).
13. What happens to a validation when the underlying implementation changes? — [`434-implementation-change-impact.md`](434-implementation-change-impact.md).
14. How do professional findings get turned into actual software changes, without skipping engineering review? — [`435-validation-to-forge-workflow.md`](435-validation-to-forge-workflow.md).
15. How do we prevent a reviewer's raw feedback from being copied directly into code without independent verification? — the same workflow, plus PROVAL-GOV-008/009.
16. How can JewelMind generate a repeatable, self-contained package for a real reviewer to work from? — [`426-review-package-contract.md`](426-review-package-contract.md), [`446-review-package-generation.md`](446-review-package-generation.md).
17. How is the full history of a review preserved for audit, including rejected and superseded records? — [`438-professional-review-audit-trail.md`](438-professional-review-audit-trail.md).

## What this Sprint does not do

It does not validate anything. `specs/professional-validation/v1/current-validation-registry.json` contains zero records, verified by `backend/tests/test_professional_validation_registry.py::TestZeroValidationDefault`. Every one of the 21 rules in `specs/forge/v1/current-rule-registry.json` keeps its pre-Sprint-13 `professionalValidationStatus` — 16 `preliminary`, 5 `not_required` — unchanged by anything written in this section. This Sprint builds the container; it does not fill it.
