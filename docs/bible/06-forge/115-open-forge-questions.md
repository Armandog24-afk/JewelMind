---
id: JM-BIBLE-115
title: Open Forge Questions
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-101
related_documents:
  - JM-BIBLE-FORGE-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Open Forge Questions

Each question below is genuinely unresolved. No question is guessed at or silently answered by this Sprint.

| ID | Question | Impact | Provisional behavior | Priority | Owner/expertise | Decision mechanism |
|---|---|---|---|---|---|---|
| `FORGE-OQ-001` | Should material profiles override generic rules? | Would require a `MaterialRuleProfile` concept and a precedence rule for material vs. generic scope | No material rule exists today, so no override question has ever arisen in practice | Medium | Metallurgist + backend maintainer | RFC once a first material-specific rule is proposed |
| `FORGE-OQ-002` | How should conflicting expert rules be represented? | Affects the shape of [`103-professional-validation-lifecycle.md`](103-professional-validation-lifecycle.md)'s register once a second reviewer disagrees with a first | Both would be preserved as separate scoped register entries, per [`101-conflicts-precedence-and-resolution.md`](101-conflicts-precedence-and-resolution.md) — untested since no professional review has ever occurred | Low (not urgent while zero rules are validated) | Domain governance owner | Team decision once a first real disagreement occurs |
| `FORGE-OQ-003` | Should warnings ever block specific exports? | Would break the current strict severity-implies-blocking-or-not rule | Today, only `error` severity blocks anything (see [`099-severity-and-blocking-semantics.md`](099-severity-and-blocking-semantics.md)); no warning blocks any export | Medium | Backend maintainer + jewelry-domain reviewer | ADR — this would be an architecture-level change to blocking semantics |
| `FORGE-OQ-004` | Should professional profiles be customer-selectable? | Affects whether `professionalRuleProfile` (see [`097-rule-context-model.md`](097-rule-context-model.md)) is ever exposed as a user-facing setting | No profile exists to select; the field is a PLANNED placeholder only | Low | Product owner | Product decision, once a first professional profile exists |
| `FORGE-OQ-005` | How should jurisdiction-specific rules work? | Would require a `geographicScope` filter actually consulted at evaluation time, not just stored on provenance | `geographicScope` exists as a provenance field (see [`094-rule-provenance-model.md`](094-rule-provenance-model.md)) but is never read by any evaluation logic | Low | Legal/compliance + backend maintainer | RFC |
| `FORGE-OQ-006` | How should supplier-specific manufacturing profiles work? | Extends [`104-manufacturing-profile-rules.md`](104-manufacturing-profile-rules.md)'s conceptual `ManufacturingRuleProfile` with a supplier axis | No `ManufacturingRuleProfile` object exists at all yet, supplier-scoped or otherwise | Low | Manufacturing partnerships owner | RFC, after `ManufacturingRuleProfile` itself is implemented |
| `FORGE-OQ-007` | Which geometry inspection rules belong in Forge versus the geometry engine? | Affects where future checks like GAP-004/005/011 (see [`111-domain-rule-gap-analysis.md`](111-domain-rule-gap-analysis.md)) get implemented — as Forge-evaluated diagnostics, or as geometry-builder-internal assertions like the current `FORGE-GEOM-001` | Today's only example (`FORGE-GEOM-001`) lives inline in `geometry/assemblies/solitaire.py`, not in `validation/engine.py` — an inconsistency with FORGE-GOV-005's spirit, worth resolving before more inspection rules are added | Medium | Backend/CAD architecture owner | ADR |
| `FORGE-OQ-008` | How should rule evaluation performance scale as more rules are added? | `validate_definition()` is currently O(number of rules), all in-process, sub-millisecond for 16 rules; unknown at 100+ rules or with expensive geometry-inspection rules | No performance issue has been observed or measured — this is a forward-looking question, not a current problem | Low | Backend maintainer | Benchmark once the rule count grows materially |
| `FORGE-OQ-009` | Should historical rules remain executable for old JDL documents? | Affects whether a deprecated rule version can still be re-run against a document created under it, for audit/reproducibility purposes | No rule has ever been deprecated, so this has never been exercised | Low | Backend maintainer | Decide when a first rule deprecation actually occurs |
| `FORGE-OQ-010` | How should auto-fixes be audited? | Affects the concrete audit-record shape referenced in [`102-suggestions-and-auto-fix-contract.md`](102-suggestions-and-auto-fix-contract.md) requirement 4 | No auto-fix exists yet, so no audit mechanism exists to describe beyond the conceptual requirement list | Low | Backend maintainer | Design work at the time auto-fix is actually built |
| `FORGE-OQ-011` | How should Forge behave when provenance expires (e.g. a professional review's `expirationOrReviewTrigger` is reached)? | Affects whether an expired validation silently reverts a rule to `preliminary`, blocks new documents, or only flags existing ones for review | No rule has ever reached `validated` status, so no expiration has ever occurred | Low | Domain governance owner | Decide when a first professional validation record actually approaches its review trigger |

## What this document is not

Not a backlog, and not a set of recommendations disguised as questions. Each provisional behavior is exactly what the code does today (or, where nothing exists yet, an explicit statement that nothing exists), so a future decision-maker starts from the true current state.
