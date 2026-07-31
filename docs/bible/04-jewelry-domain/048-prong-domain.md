---
id: JM-BIBLE-048
title: Prong Domain
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on:
  - JM-BIBLE-047
related_documents:
  - JM-BIBLE-049
  - JM-BIBLE-052
implementation_status: current
professional_validation: preliminary
---

# Prong Domain

## Individual prong vs. prong set

- **Individual prong:** one cylindrical solid.
- **Prong set (`ProngSet`, conceptually — implemented as one
  `GeneratedComponent` named `"prongs"`):** the compound of all
  individually-built prong solids for a given definition
  (`geometry/components/prongs.py::build_prongs`).

The code does not model a single-prong type separately from the set — all
prongs for a definition are built and returned together as one component
with a combined volume and bounding box.

## Current parameters

| Parameter | Path | Type | Notes |
|---|---|---|---|
| Count | `setting.prongCount` | int | Business rule (`JM-PRONG-001`) restricts to 4 or 6; the type itself allows any int so an invalid value produces a structured validation error rather than a parse error. |
| Diameter | `setting.prongDiameter` | float, mm | Cylinder diameter. |
| Height | `setting.prongHeight` | float, mm | Height above the embedded base — see below. |

## Requested vs. generated count

`build_prongs()` reports **both** `requestedCount` and `generatedCount`
in its metadata, and stays honest even for an unsupported count (e.g. it
would report `generatedCount: 5` for a requested count of 5, rather than
silently rounding) — geometry generation is expected to be blocked
upstream by `JM-PRONG-001` before this code path is reached with an
invalid count, but the function itself does not assume that.

## Angular distribution

Prongs are placed at evenly-spaced angles around a circle:
`angle = 2π · i / count` for `i` in `0..count-1`
(`geometry/components/prongs.py::_prong_positions`), each at
Cartesian position `(radius·cos(angle), radius·sin(angle))`.

## Relationship to stone diameter

The shared radius (`geometry/constants.py::prong_center_radius`) is:

```
girdle_radius = stone.diameter / 2
prong_radius  = setting.prongDiameter / 2
center_radius = girdle_radius − prong_radius × 0.3
```

The `× 0.3` factor is a **PRELIMINARY SOFTWARE RULE**: it pulls the
prong centers slightly inside the girdle radius so each prong body
overlaps the stone's girdle edge, approximating a grip — it is not a
professionally validated contact-geometry rule.

## Relationship to basket height

`JM-PRONG-004` requires `prongHeight > basketHeight` — an IMPLEMENTED
FACT, checked in `validation/engine.py` and tested in
`test_validation.py::test_prong_height_must_exceed_basket_height`. This
is a geometric-plausibility rule (a prong shorter than the basket it
rises from would not visually clear it), not a professionally validated
setting-height convention.

## Current supported counts

Four and six only (`JM-PRONG-001`). `JM-PRONG-003` adds a *warning*
(not an error) recommending six prongs when `stone.diameter > 8mm` with
four prongs requested — a PRELIMINARY SOFTWARE RULE about a general
tendency (larger stones often use more prongs for security), not a
validated engineering threshold for any specific stone size/weight.

## Current geometric representation

Plain vertical cylinders (`cq.Workplane(...).circle(prong_r).extrude(height)`),
embedded `EMBED_MM` (0.4mm) below `band_top_z` so they genuinely overlap
the basket/band solids when fused (see
[LAW-005](../00-foundation/004-jewelmind-constitution.md#LAW-005)). No
taper, no inward inclination, no bearing cut, no tip shaping.

## Connection to basket

Prongs and the basket support share the same `center_radius` derivation
(both call `prong_center_radius()`), and the basket's outer/inner radii
are specifically sized (`center_r ± prong_r`) so the prong footprint is
fully contained within the basket wall thickness at every angle — see
[`049-basket-and-support-domain.md`](049-basket-and-support-domain.md).

## Current limitations (explicit)

**The current prongs are not claimed to be ready for professional stone
setting.** Specifically absent:

- No bearing/seat cut — a real prong is typically cut or shaped to match
  the stone's girdle/pavilion contour at the contact point; the current
  cylinder has no such feature.
- No taper or tip shaping (a real prong often tapers and is finished
  with a rounded or faceted tip after setting).
- No inward inclination toward the stone — prongs are perfectly vertical.
- No asymmetric arrangement support — only evenly-spaced counts.
- No stone-contact-region modeling — overlap with the stone reference is
  geometric only, not a modeled physical bearing surface.

## Existing validation rules (full classification in [`054-domain-validation-classification.md`](054-domain-validation-classification.md))

| Rule ID | Check | Severity |
|---|---|---|
| `JM-PRONG-001` | count must be 4 or 6 | error |
| `JM-PRONG-002` | diameter `< 0.8mm` error; `0.8–1.0mm` warning | error/warning |
| `JM-PRONG-003` | stone diameter `> 8mm` with 4 prongs | warning |
| `JM-PRONG-004` | prong height must exceed basket height | error |

## Future concepts (PLANNED — no numeric defaults invented)

| Concept | Status |
|---|---|
| Claw shape (as distinct from a plain cylinder) | PLANNED |
| Double claw | PLANNED |
| Taper | PLANNED |
| Inward inclination | PLANNED |
| Tip geometry (rounded, pointed, flat) | PLANNED |
| Seat/bearing cut | PLANNED — requires professional input, see [`057-open-domain-questions.md`](057-open-domain-questions.md) |
| Stone contact region modeling | PLANNED |
| Asymmetric prong arrangements | VISION |
