---
id: JM-BIBLE-A08
title: "Appendix: Jewelry Domain Status Matrix"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on: []
related_documents:
  - JM-BIBLE-A05
  - JM-BIBLE-006
implementation_status: current
professional_validation: not_required
---

# Appendix: Jewelry Domain Status Matrix

CURRENT, PARTIAL, PLANNED, VISION, and UNKNOWN concepts across the entire
Sprint 2 domain model, in one place.

## CURRENT

Ring, Solitaire style, Band (flat + comfort-fit profiles), Center stone
reference (round only), Prong setting (4 or 6 prongs), Basket support
(hollow cylindrical wall), Material metadata (5 metals, cosmetic),
Manufacturing context (2 methods, 1 validation rule), Preview
configuration, Validation engine (16 rules), Generated model identity
(hash-based), STEP/STL/JSON/specification export, EU/French ring sizing.

## PARTIAL

- **Head** (setting + basket combined) — the *behavior* exists (they are
  built and connected together) but there is no named `Head` concept in
  code.
- **Girdle relationship** — prongs are radially positioned relative to
  the stone's girdle radius, but there is no true seat/bearing geometry.

## PLANNED

Wedding band, Signet/chevalier, Halo, Hidden halo, Trilogy, Toi et Moi,
Eternity, Half-eternity, Cluster, Bypass, Split shank, Cathedral (ring
styles — [`042`](../04-jewelry-domain/042-ring-taxonomy.md)); Bezel,
Channel, Pavé, Micro-pavé, Flush, Tension, Invisible, Cluster setting,
Halo arrangement (setting types —
[`047`](../04-jewelry-domain/047-setting-domain.md)); Oval, Princess,
Emerald, Cushion, Pear, Marquise, Radiant, Asscher, Heart (stone shapes —
[`046`](../04-jewelry-domain/046-stone-domain.md)); Claw shape, double
claw, taper, inclination, tip geometry, seat/bearing cut (prong
refinements — [`048`](../04-jewelry-domain/048-prong-domain.md)); Band
taper, shoulder width, outer contour, edge radius, split shank, cathedral
rise (band refinements —
[`045`](../04-jewelry-domain/045-band-domain.md)); Gallery, Bridge,
Shoulders (ring anatomy —
[`043`](../04-jewelry-domain/043-ring-anatomy.md)); Material density,
estimated weight, alloy variation, casting shrinkage context, structural
rule profiles, finishing allowances (material —
[`050`](../04-jewelry-domain/050-material-domain.md)); Print orientation,
support placement, casting shrinkage, sprue strategy, polishing
allowance, tolerances, cleanup access, minimum feature behavior
(manufacturing — [`051`](../04-jewelry-domain/051-manufacturing-context.md));
non-EU sizing systems (sizing —
[`057`](../04-jewelry-domain/057-open-domain-questions.md), JM-DQ-012).

## VISION

Earring, Pendant, Necklace, Bracelet, Bangle, Brooch, Charm, Cufflink
(jewelry categories —
[`041`](../04-jewelry-domain/041-jewelry-product-taxonomy.md));
Asymmetric band profile, internal relief (band —
[`045`](../04-jewelry-domain/045-band-domain.md)); Engraving, decorative
elements (anatomy — [`043`](../04-jewelry-domain/043-ring-anatomy.md));
Asymmetric prong arrangements (prongs —
[`048`](../04-jewelry-domain/048-prong-domain.md)); Cost calculation
(material — [`050`](../04-jewelry-domain/050-material-domain.md));
Stone-setting sequence, hollowing, drainage, assembly strategy
(manufacturing — [`051`](../04-jewelry-domain/051-manufacturing-context.md)).

## UNKNOWN

Every item in
[`057-open-domain-questions.md`](../04-jewelry-domain/057-open-domain-questions.md)
is, by definition, UNKNOWN until resolved — notably: whether "signet" and
"chevalier" are fully synonymous (JM-DQ-001); whether the current
comfort-fit flare/prong-overlap/basket-wall approximations are adequate
for any real design (JM-DQ-004, JM-DQ-005, JM-DQ-008); every numeric
threshold's professional correctness (JM-DQ-003, JM-DQ-006, JM-DQ-007,
JM-DQ-010, JM-DQ-011); which additional sizing systems to support
(JM-DQ-012); whether preview tolerances should vary by manufacturing
method (JM-DQ-013); STEP export expectations for downstream tooling
(JM-DQ-014); and what a formal professional-review workflow should look
like (JM-DQ-015).

## Cross-check against implementation

This matrix was produced by inspecting
`backend/jewelmind/domain/schema.py`,
`backend/jewelmind/geometry/components/*.py`,
`backend/jewelmind/validation/engine.py`, and
`frontend/src/components/ConfigurationPanel.tsx` directly — nothing
listed as CURRENT above lacks a corresponding code reference in
[`jewelry-domain-entity-catalog.md`](jewelry-domain-entity-catalog.md) or
[`jewelry-domain-parameter-catalog.md`](jewelry-domain-parameter-catalog.md).
