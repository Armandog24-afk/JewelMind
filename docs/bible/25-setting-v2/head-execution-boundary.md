---
id: JM-BIBLE-SETTINGV2-BOUNDARY
title: "Setting v2 execution boundary"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-03
source_of_truth: true
depends_on:
  - JM-BIBLE-SETTINGV2-README
implementation_status: partial
professional_validation: not_required
normative: true
---

# Setting v2 execution boundary

What executes, what does not, and why each line was drawn where it is.

## Executes today

| Capability | Evidence |
| --- | --- |
| 4 prong styles as real solids | `prong_styles.py`; each one valid, connected, spanning the requested height |
| 4 head architectures as real solids | `head.py`; each one connected, same vertical extent |
| Explicit prong positions | `positionSource="EXPLICIT"`, used verbatim |
| Per-group style overrides | `ProngGroupSpec.style`, applied per prong index |
| Setting → stone-instance mapping | `stoneInstanceAssignments`, by ID and sorted |
| Reference seat relief | a boolean cut of the real stone out of head and prongs |
| Structural validation | `JM-SETTING-005`…`007`, mirrored completely in the frontend |
| Legacy preservation | default metal volume unchanged; 39/39 Goldens, zero updates |

## Does not execute, and why

### TRELLIS head — PLANNED

Interwoven curved rails need a swept solid along a 3D spline. The current
pipeline builds solids of revolution, cone frusta and lofts reliably; a swept
trellis is not verifiable here yet. A "simplified trellis" built from four bent
prongs would be a **different structure wearing the name**, so no builder
exists and `TRELLIS` is not a `HeadArchitecture` member — a caller naming it is
refused by the model, not silently given a basket.

Three further architectures are reserved for reasons that are not about
difficulty:

- **`cathedral`** is defined by how the *shank* rises to meet the head. That is
  shank geometry, so it belongs to a Shank milestone, not here.
- **`compass_point`** positions prongs at the stone's own anchors. The anchors
  exist (Stone v2); anchor-driven placement does not.
- **`double_gallery`** needs two stacked galleries, i.e. a second head per
  setting, which the one-head-per-setting contract does not express.

### Support rails — PLANNED

A rail joins two or more heads, so it requires multi-head geometry. One setting
builds one head today.

### Shared prong geometry — PARTIAL

A prong serving two stones is fully **representable** (an explicit position
carrying `servesStoneInstanceIds`) and its assignment is **reported**. It is not
**generatable against two stones**, because the pipeline emits one stone
component per model — the Stone Arrangement execution boundary from Sprint 22.
Nothing here works around that: the mapping is real and the second stone is not.

### Bearing and cutter geometry — PLANNED

A bearing is a cut shoulder inside a seat, sized by a setter. A cutter is
manufacturing tooling, not part of the jewelry model. Neither has sourced
professional geometry behind it, so neither is invented. `seatSupport` moved
from `PLANNED` to `PARTIAL` because relief is real; `bearingSupport` and
`cutterSupport` remain `PLANNED` and must stay so.

### Instance-aware prong placement — PLANNED

Placing prongs by consuming a stone's anchors, or laying out a shared prong
automatically between two resolved instances. Both wait on the same
multi-stone geometry dependency.

## What was deliberately not done

- **No fake trellis.** Bending four prongs and calling it a trellis would
  report a structure the model does not contain.
- **No renamed head component.** Emitting `martini_head` instead of
  `basket_support` would have broken the role map, the inspection
  required-component set, every manifest and all 39 Goldens, to express what
  `headArchitecture` already reports.
- **No unified prong builder.** Producing `ROUND_PRONG` as a degenerate taper
  would have been tidier and would have moved every existing design's geometry.
- **No seat by default.** Relief changes prong and head volumes, so it is
  opt-in.
- **No professional threshold.** Not one rule judges prong thickness, wall
  castability or whether a seat would hold.

## Dependency order for what comes next

1. A per-instance stone transform (Sprint 22's first dependency) — without it,
   shared prongs and multi-head layouts have nothing to grip.
2. Instance-aware Geometry Inspection, so additional stones and heads are
   inspected as themselves.
3. Anchor-driven placement, which needs (1) only for multi-stone cases and can
   land earlier for single stones.
4. A swept-geometry capability in Atlas, after which `TRELLIS` becomes
   answerable.

`shared_prong_geometry` must not be relabelled `CURRENT` before (1) and (2),
and `trellis_head` must not be relabelled before (4).
