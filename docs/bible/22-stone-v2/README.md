---
id: JM-BIBLE-STONEV2-README
title: "Stone System v2 — Extended Cuts, Custom & Measured Stones"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-02
source_of_truth: true
depends_on:
  - JM-BIBLE-STONE-README
  - JM-BIBLE-SETTING-README
  - JM-BIBLE-ATLAS-README
related_documents:
  - JM-BIBLE-600
implementation_status: current
professional_validation: not_required
normative: true
---

# Stone System v2 — Extended Cuts, Custom & Measured Stones

Sprint 20. The machine-readable half lives at
[`specs/stone/v2/`](../../../specs/stone/v2/README.md).

## What this sprint changed

Stone System v1 (Sprint 18) made stone geometry **category-neutral** and
supported seven named cuts. It was still bounded by a finite enum: a stone that
did not correspond to a built-in cut could not be modelled at all.

Stone System v2 removes that bound. **The point of this sprint is not the
fourteen new cuts — it is that JewelMind no longer depends on being able to
enumerate every stone in existence.**

Three escape hatches make that true:

| Escape hatch | What it accepts |
|---|---|
| `CUSTOM_OUTLINE` | Any validated closed 2D outline |
| `MEASURED` | Real measurements of a real physical stone |
| `IMPORTED_CAD` | An external STEP/BREP/STL asset |

## The two independent axes

Everything else follows from one decision:

```
stone.shape    →  the OUTLINE      (21 named cuts + custom + imported)
stone.profile  →  the 3D PROFILE   (FACETED / CABOCHON / SPHERICAL)
```

An oval cabochon is `shape=oval` + `profile=CABOCHON_REFERENCE`. There is no
`OVAL_CABOCHON` member, and there never will be: compound members multiply, two
axes do not. See [`stone-profile-v2.md`](stone-profile-v2.md).

## Where to start

| Question | Document |
|---|---|
| What are the rules I must not break? | [`stone-v2-governance.md`](stone-v2-governance.md) |
| How do the four source modes fit together? | [`stone-source-architecture.md`](stone-source-architecture.md) |
| Which cuts exist, and in what families? | [`extended-shape-taxonomy.md`](extended-shape-taxonomy.md) |
| How is geometry reused across cuts? | [`shape-family-architecture.md`](shape-family-architecture.md) |
| How is each new cut actually built? | [`extended-native-shapes.md`](extended-native-shapes.md) |
| How does outline × profile work? | [`stone-profile-v2.md`](stone-profile-v2.md) |
| What is a custom outline, exactly? | [`custom-outline-contract.md`](custom-outline-contract.md) |
| What gets rejected, and why? | [`custom-outline-validation.md`](custom-outline-validation.md) |
| How is a measured stone represented? | [`measured-stone-contract.md`](measured-stone-contract.md) |
| How is an imported asset handled? | [`imported-stone-contract.md`](imported-stone-contract.md) |
| What normalization is applied on import? | [`import-normalization.md`](import-normalization.md) |
| How do cabochons and pearls work? | [`cabochon-and-pearl.md`](cabochon-and-pearl.md) |
| How is provenance recorded? | [`stone-source-provenance.md`](stone-source-provenance.md) |
| Which stones can be set, and how? | [`stone-setting-compatibility-v2.md`](stone-setting-compatibility-v2.md) |
| What does inspection report? | [`stone-inspection-v2.md`](stone-inspection-v2.md) |
| How is regression protected? | [`stone-v2-golden-strategy.md`](stone-v2-golden-strategy.md) |
| What is CURRENT vs PLANNED? | [`stone-v2-capability-model.md`](stone-v2-capability-model.md) |
| Do Stone v1 documents still work? | [`current-stone-v1-migration.md`](current-stone-v1-migration.md) |
| Where does the code live, and what is missing? | [`code-mapping-and-gaps.md`](code-mapping-and-gaps.md) |
| What is still undecided? | [`open-stone-v2-questions.md`](open-stone-v2-questions.md) |
| What was actually verified this sprint? | [`SPRINT-20-VALIDATION-REPORT.md`](SPRINT-20-VALIDATION-REPORT.md) |

## Current state, stated plainly

**21 native cuts generate real, deterministic CAD geometry:** the seven from
Stone v1 (round, oval, pear, emerald, cushion, princess, marquise) plus heart,
radiant, asscher, trillion, baguette, tapered_baguette, triangle, trapezoid,
lozenge, hexagon, kite, shield, half_moon and pearl.

**Three profiles exist:** `FACETED_REFERENCE` (all outline shapes),
`CABOCHON_REFERENCE` (round, oval, heart, half_moon, and any custom outline),
`SPHERICAL_REFERENCE` (pearl).

**All four source modes are implemented.** `IMPORTED_CAD` is `PARTIAL`: B-Rep
and mesh import, unit normalization, inspection and Vision all work, but
setting compatibility is decided per asset from real geometry rather than
granted.

**Nothing is professionally validated.** Every shape, profile and source is
`NOT_REVIEWED`. See
[`../15-professional-validation/README.md`](../15-professional-validation/README.md).

## What this system explicitly does NOT claim

- **No gemological accuracy.** A `StoneReference` is deterministic CAD
  reference geometry. No shape models a real facet arrangement, and
  `isGemologicalReproduction` is always `false`.
- **No commercial cut proportions.** Every ratio — the radiant and asscher
  corner clips, the trillion bulge, the heart lobe radius, the cabochon dome
  fractions — is a documented SOFTWARE REFERENCE CONSTRUCTION parameter,
  verified only to produce robust geometry.
- **No invented measurements.** A measured stone with a missing measurement is
  an error. A dimension-only reference is labelled
  `MEASURED_DIMENSION_REFERENCE` and is not a model of the physical stone's
  surface.
- **No guessed units.** An imported asset's unit is declared by the caller.
- **No equivalent diameter.** An 8 × 6 stone is never collapsed to a single
  diameter to satisfy a round-only rule.
- **Shape is never gem species.** `emerald` is a clipped-corner outline; the
  rhombus is `lozenge`, never `diamond`. Gem identity is Sprint 21.

## Cross-references

- [`../20-stone/README.md`](../20-stone/README.md) — Stone System v1, still
  accurate for the seven original shapes and for the shared coordinate contract.
- [`../21-setting/README.md`](../21-setting/README.md) — the Setting System,
  which Sprint 20 made genuinely shape-agnostic.
- [`../18-ring-architecture/520-jewelry-category-architecture.md`](../18-ring-architecture/520-jewelry-category-architecture.md)
  — why Stone belongs to no jewelry category.
