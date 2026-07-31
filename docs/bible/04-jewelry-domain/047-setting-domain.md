---
id: JM-BIBLE-047
title: Setting Domain
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on:
  - JM-BIBLE-044
related_documents:
  - JM-BIBLE-048
  - JM-BIBLE-042
implementation_status: partial
professional_validation: preliminary
---

# Setting Domain

## Setting is broader than "prong setting"

`Setting` is the domain concept covering *how a stone is physically held*.
`domain/schema.py::SettingSpec.type` currently accepts only
`Literal["prong"]` — so **`Setting` and `ProngSetting` are the same thing
in code today**, but this document treats them as separate concepts
(broader category vs. current instance) so future setting types have
somewhere to attach without redefining `Setting` itself.

## Setting type, ring style, stone arrangement, and decorative treatment are related but separate

Repeating the distinction from
[`042-ring-taxonomy.md`](042-ring-taxonomy.md), specifically for setting:

- **Setting type** answers "how is the stone held" (prong, bezel,
  channel, ...).
- **Ring style** answers "what is the overall structure" (solitaire,
  halo, ...) — a halo ring could still use a prong setting for its
  center stone.
- **Stone arrangement** answers "how many stones, in what layout" (one
  center stone, a row of three, a ring of accents, ...).
- **Decorative treatment** answers "what surface technique is applied"
  (pavé being the clearest example — a decorative/setting technique for
  accent stones, not a ring style).

A future setting type must not be modeled as if it implies a specific
ring style or stone arrangement — e.g. "channel setting" does not, by
itself, mean "eternity ring"; channel setting could appear in other
layouts too.

## CURRENT: ProngSetting

- **Conceptual purpose:** hold the stone reference in position using
  discrete claw-like metal projections.
- **Required relationships:** connects to `BasketSupport` below,
  positions relative to `CenterStoneReference`'s girdle radius.
- **Components:** individual prongs (see
  [`048-prong-domain.md`](048-prong-domain.md)).
- **Professional knowledge required (not yet applied):** real prong
  setting requires bearing cuts, correct metal-to-stone contact area, and
  setter technique — none of which the current geometry represents (see
  [`048-prong-domain.md`](048-prong-domain.md) for the explicit
  limitations list).
- **Implementation status:** CURRENT.

## Future setting types (status only)

| Setting type | Conceptual purpose | Likely required relationships | Likely components | Professional knowledge required | Status |
|---|---|---|---|---|---|
| **Bezel** | Stone fully or partially encircled by a continuous metal rim. | Connects directly to band/basket-equivalent; no discrete prongs | A rim/collar component | Rim height vs. stone depth conventions, girdle contact | PLANNED |
| **Channel** | Stones held between two parallel metal walls, typically in a row. | Requires a linear/curved arrangement of stones, not a single center stone | Two rail components + stone row | Rail spacing per stone size, structural span limits | PLANNED |
| **Pavé** | Many small stones set closely together, each with tiny beads/prongs, giving a "paved" surface appearance. | A dense stone-arrangement pattern over a surface (e.g. band or basket) | Many small stone + micro-prong components | Bead/prong sizing at very small scale, structural minimums | PLANNED |
| **Micro-pavé** | Pavé at a smaller stone-size scale. | Same as pavé, smaller scale | Same as pavé | Same as pavé, more acute at smaller sizes | PLANNED |
| **Flush** (gypsy) | Stone set into a drilled recess, flush with the surrounding metal surface. | Requires a recess/counter-bore relationship with the surrounding metal | A recess-cut component | Recess depth vs. stone depth, wall thickness around recess | PLANNED |
| **Tension** | Stone held purely by spring-tension pressure from the band itself, no prongs/bezel. | Requires the band to have a load-bearing gap/notch holding the stone directly | Band-integrated notch component | Structural/spring behavior — significantly different from any current geometry approach | PLANNED |
| **Invisible** | Stones set with no visible metal between them, using a hidden rail/groove system. | Requires per-stone grooved girdles and a hidden rail structure | Rail + grooved-stone components | Groove-cutting precision, structural reliability | PLANNED |
| **Cluster** | Multiple stones grouped and set together, sharing structural support. | Requires a stone-group with a shared support component | Group support + per-stone setting | Load distribution across the group | PLANNED |
| **Halo arrangement** | A ring of small stones surrounding a center stone, each individually set (often pavé or shared-prong). | Requires the center-stone relationship plus a surrounding stone ring | Center setting + accent-ring setting | Accent stone sizing/count conventions | PLANNED |

None of these have a schema field, default, or geometry builder. See
[`056-domain-extension-strategy.md`](056-domain-extension-strategy.md)
for how a new setting type would be proposed and added.

## Do not document unvalidated manufacturing thresholds

This document intentionally does not state minimum wall thicknesses,
bead sizes, or span limits for any future setting type — those would be
manufacturing thresholds requiring professional validation, not domain
definitions. Where such a number is genuinely needed for the *current*
prong setting, it is documented (with its classification) in
[`054-domain-validation-classification.md`](054-domain-validation-classification.md)
instead.
