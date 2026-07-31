---
id: JM-BIBLE-DOMAIN-README
title: Jewelry Domain Model — Index
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on:
  - JM-BIBLE-000
related_documents:
  - JM-BIBLE-README
  - JM-BIBLE-005
implementation_status: current
professional_validation: preliminary
---

# Jewelry Domain Model — Index

This is **Sprint 2** of the Technical Bible: **Jewelry Domain Model**. It
defines the concepts, entities, components, relationships, parameters,
and dependencies JewelMind currently understands (and does not yet
understand) about jewelry — grounded strictly in the existing code, tests,
and Sprint 1 Bible, not in outside jewelry-industry references.

**Read [`040-domain-governance.md`](040-domain-governance.md) first.** It
defines how a domain statement earns each classification used throughout
this section — most importantly, the distinction between an
**IMPLEMENTED FACT** (true of the running code) and a **PROFESSIONALLY
VALIDATED RULE** (reviewed and accepted by an identified jewelry
professional). As of this Sprint, **zero** rules in this repository carry
professional validation — see
[`058-professional-validation-register.md`](058-professional-validation-register.md).
Every numeric threshold currently in the code is, at most, a
**PRELIMINARY SOFTWARE RULE**.

## Why this section exists

Sprint 1 documented *what JewelMind is and how it is built*. This section
documents *what JewelMind currently believes a ring is* — precisely,
so that the future Jewelry Definition Language (Sprint 3) and any future
geometry module can be designed against an honest map of today's
concepts, not against assumed jewelry-industry knowledge that was never
actually reviewed by a professional.

## Reading order

1. [`040-domain-governance.md`](040-domain-governance.md) — classification
   rules for every statement in this section.
2. [`041-jewelry-product-taxonomy.md`](041-jewelry-product-taxonomy.md) —
   where "ring" sits among possible future jewelry categories.
3. [`042-ring-taxonomy.md`](042-ring-taxonomy.md) — where "solitaire" sits
   among possible future ring styles.
4. [`043-ring-anatomy.md`](043-ring-anatomy.md) — the conceptual parts of
   a ring, current or not.
5. [`044-solitaire-domain-model.md`](044-solitaire-domain-model.md) — the
   central document: the current solitaire as a domain aggregate.
6. Component documents:
   [band](045-band-domain.md),
   [stone](046-stone-domain.md),
   [setting](047-setting-domain.md),
   [prong](048-prong-domain.md),
   [basket/support](049-basket-and-support-domain.md),
   [material](050-material-domain.md),
   [manufacturing context](051-manufacturing-context.md).
7. Cross-cutting analysis:
   [parametric dependencies](052-parametric-dependency-model.md),
   [domain invariants](053-domain-invariants.md),
   [validation classification](054-domain-validation-classification.md),
   [domain-to-code mapping](055-domain-to-code-mapping.md),
   [extension strategy](056-domain-extension-strategy.md).
8. [`057-open-domain-questions.md`](057-open-domain-questions.md) and
   [`058-professional-validation-register.md`](058-professional-validation-register.md)
   — what remains unresolved, and how a real review would be recorded.

## Appendices

[`appendices/jewelry-domain-entity-catalog.md`](../appendices/jewelry-domain-entity-catalog.md),
[`jewelry-domain-parameter-catalog.md`](../appendices/jewelry-domain-parameter-catalog.md),
[`jewelry-domain-relationship-matrix.md`](../appendices/jewelry-domain-relationship-matrix.md),
[`jewelry-domain-status-matrix.md`](../appendices/jewelry-domain-status-matrix.md).

## The single most important rule in this section

**Implemented code does not make a jewelry rule professionally correct.**
A validation threshold existing in `backend/jewelmind/validation/engine.py`
means it was useful for prototype safety or consistency — it does not
mean a bench jeweler, a gemologist, or a manufacturing engineer has
reviewed and accepted it. See
[`040-domain-governance.md`](040-domain-governance.md) for the full
classification rule, and
[`054-domain-validation-classification.md`](054-domain-validation-classification.md)
for every current rule classified individually.

## Validation of this sprint

See
[`SPRINT-2-VALIDATION-REPORT.md`](SPRINT-2-VALIDATION-REPORT.md) for the
link/path/front-matter/Mermaid checks run against this section and the
findings from that pass.
