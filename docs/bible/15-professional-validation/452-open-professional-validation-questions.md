---
id: JM-BIBLE-452
title: Open Professional Validation Questions
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-PROVAL-README
  - JM-BIBLE-451
related_documents: []
implementation_status: current
professional_validation: not_required
normative: false
---

# Open Professional Validation Questions

These are open product and policy questions raised while building this
final batch of Sprint 13 documents, not decisions. None are answered by
this document — each requires either a product decision, an RFC, or an
ADR per [`410-validation-governance.md`](410-validation-governance.md)'s
"When an ADR is required" / "When an RFC is required" sections before
being acted on. Mirrors the format of
[`13-design-intent/363-open-design-intent-questions.md`](../13-design-intent/363-open-design-intent-questions.md).

1. **How many reviewers should validate a critical rule?** A single
   `ValidationRecord` per rule is structurally sufficient today
   (`ValidationTarget` doesn't require a minimum reviewer count), but is
   one qualified opinion ever enough for a rule whose failure could cause
   a real manufacturing defect, versus a rule that only affects
   cosmetic proportion?
2. **When is one specialist sufficient?** Related to question 1 — does
   sufficiency depend on the rule's `FindingSeverity` potential, its
   `ValidationObjectType`, or something else entirely?
3. **Which rules need bench testing rather than CAD review?** Some of the
   16 currently `preliminary` Forge rules could plausibly be confirmed by
   CAD inspection alone; others (wall thickness for casting integrity,
   prong grip adequacy) may need physical bench or cast-sample evidence
   (`EvidenceType.PHYSICAL_PRINT`/`CAST_SAMPLE`/`BENCH_WORK`) to be
   credible at all. No triage of which rule needs which evidence tier
   exists yet.
4. **Should casting rules be workshop-specific?** `ValidationScope.geographicOrWorkshopConstraints`
   exists as a field, but no policy states whether a casting-related
   validation should default to broad applicability or default to
   narrow, single-workshop scope absent explicit evidence of
   generalizability.
5. **How should supplier-specific profiles work?** If a specific alloy
   supplier's material behaves differently from another under the same
   nominal alloy name, does that need its own `MATERIAL_PROFILE`
   `ValidationObjectType` instance, or does `ValidationScope.alloy` alone
   suffice?
6. **How should reviewer disagreement affect Forge?** `DisagreementRecord`
   preserves two conflicting records side by side (PROVAL-GOV-012), but
   no policy states what a Forge rule's `professionalValidationStatus`
   should read as while a real, unresolved disagreement exists for it —
   does it stay `preliminary`, or does a new intermediate status make
   sense?
7. **Should validations be public to customers?** No publication
   mechanism exists today (verified,
   [`448-validation-security-and-privacy.md`](448-validation-security-and-privacy.md)).
   If one is ever built, would a customer see "this specific rule/geometry
   was validated by a named reviewer," or only an aggregate "professionally
   reviewed" claim — and does the latter risk overstating what a narrow,
   scoped record actually covers (PROVAL-GOV-015 through 018)?
8. **Should validation evidence be cryptographically signed later?** No
   signing mechanism exists today (verified,
   [`451-validation-gap-analysis.md`](451-validation-gap-analysis.md)). If
   validation records or review packages are ever exposed outside a
   trusted internal process, is tamper-evidence necessary, and if so,
   whose key signs what?
9. **Which validations need expiration?** `expirationOrReviewTrigger` is
   real but always reviewer-stated, never system-imposed
   (PROVAL-GOV-014). Should some `ValidationObjectType`s (e.g.
   `CAD_INTEROPERABILITY_WORKFLOW`, likely to be invalidated by a CAD
   application's own version updates) get a *recommended default*
   trigger pattern, without violating the "never an arbitrary annual
   expiration unless a reviewer states one" rule?
10. **How should physical production failures feed back into
    validation?** The `contradictory_field_evidence` expiration trigger
    names this scenario, but no intake mechanism exists (gap table,
    [`451-validation-gap-analysis.md`](451-validation-gap-analysis.md)).
    Would this be a manual report a reviewer files, or would it need its
    own structured schema?
11. **When can JewelMind describe something as "professionally
    reviewed"?** Is a single `VALIDATED_WITH_CONDITIONS` record on one
    narrow scope enough to use that phrase anywhere in product
    communication, or does it require a minimum coverage threshold across
    the object's realistic scope range (echoing question 1's "how many
    reviewers" concern, but about breadth of scope rather than reviewer
    count)?
12. **What minimum evidence is required before using
    "manufacturing-ready" language?** CLAUDE.md and this Sprint's
    generated review-package README already forbid claiming
    manufacturing readiness today — this question is about what would
    ever be *sufficient* to lift that restriction for a specific,
    narrowly-scoped design, not whether the restriction currently
    applies (it does, unconditionally, right now).
13. **Should that phrase be avoided entirely?** A stronger position than
    question 12: should "manufacturing-ready" (or close synonyms) simply
    never appear in JewelMind's product language, in favor of a
    permanently scoped phrasing like "validated for lost-wax casting of
    14k yellow gold solitaires in the 5-8mm stone range as of
    2026-08-26, by reviewer R"?
14. **How should commercial liability boundaries be communicated?** If a
    professionally validated design is later manufactured and a defect
    occurs, what does a `VALIDATED` record actually represent
    contractually or legally — a reviewer's professional opinion at a
    point in time, or something with stronger implied guarantees? This
    question is explicitly not answered here.

## Do not answer legal questions without qualified legal review

Questions 11 through 14 in particular touch potential legal and
commercial liability exposure. Nothing in this Sprint, this document, or
any other file under `docs/bible/15-professional-validation/` should be
read as legal advice or as a resolved liability position. Any decision
that would change what JewelMind claims publicly about validation,
manufacturing readiness, or liability must go through qualified legal
review before being acted on — no coding agent, including the one that
wrote this document, is authorized to resolve these questions on the
product's behalf.

## Cross-references

- [`410-validation-governance.md`](410-validation-governance.md) — the RFC/ADR process any answer to these questions must go through.
- [`451-validation-gap-analysis.md`](451-validation-gap-analysis.md) — the gaps several of these questions are drawn from.
- `../13-design-intent/363-open-design-intent-questions.md` — the Sprint 11 sibling this document follows in structure.
