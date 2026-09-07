---
id: JM-BIBLE-HALO-BOUNDARY
title: "Halo execution boundary"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-07
source_of_truth: true
depends_on:
  - JM-BIBLE-HALO-README
implementation_status: partial
professional_validation: not_required
normative: true
---

# Halo execution boundary

What executes, what does not, and why the line sits where it does.

## Executes today

| Capability | Evidence |
| --- | --- |
| Declare a halo in JDL | round-trips; validates against `specs/jdl/v1/jdl.schema.json` |
| Compose it onto a solitaire, a family or an explicit arrangement | `halo/compile.py`; `family/effective.py` is the single resolution point |
| Resolve every halo stone to a placement | the existing arrangement resolver, unchanged |
| Build a stone solid per halo stone | `geometry/stone/instance.py`; one valid solid each |
| Apply per-ring and per-stone scale | measured: a 0.25 scale gives 0.25³ of the volume |
| Place a **hidden** halo below the centre | measured: the built solid's bounding box moves by exactly `zOffsetMm` |
| Two independently parameterized rings | measured: distinct radii and distinct volumes per ring |
| Elliptical and partial-arc rings | `radiusYMm`, `sweepDeg` |
| Halo around a **multi-stone** centre | `centerMemberId: null`; the toi-et-moi pair sits inside the ring |
| Mixed gem identities, per ring and per stone | the real Sprint 21 registry |
| Name and inspect each halo stone | `stone_reference.<instanceId>`, required by Inspection |
| Structural validation | `JM-HALO-001`…`005` |
| Keep halo-free designs identical | metal volume unchanged; 44/44 pre-existing Goldens, zero updates |

## Does not execute

### Halo setting metal — PLANNED

**The one real limitation, and the reason every variant is `PARTIAL` rather than
`CURRENT`.** A halo design builds every halo stone and **one** setting: the
centre stone's. The halo stones are placed, sized, offset and rendered, and
nothing holds them.

This was not implemented because doing it honestly requires deciding *how* a
halo is held — a shared bezel rail, a row of shared prongs, cut-down bead
setting — and each is real setter geometry with real professional consequences.
Sprint 23 built the contract a future strategy will use (explicit prong
positions carrying `servesStoneInstanceIds`), and `SETTING-GOV` requires an RFC
before a halo setting family is added. **That RFC is the next step, and this
sprint deliberately did not bypass it.**

The limitation is reported through four independent channels, so it cannot be
mistaken for support:

1. `halo/capability.py` — every variant has `settingGeometry: false`, and
   `halo_variants_with_setting_geometry()` returns `()`;
2. `JM-HALO-005` — an information-severity finding on every haloed design;
3. every test vector records `settingCoverage: "PRIMARY_ONLY"`;
4. every new Golden case records `HALO_METAL_ABSENT` in `knownLimitations`.

### An outline-following halo — PLANNED

A halo whose stones follow the centre stone's own girdle outline — a cushion or
emerald halo — needs an outline-offset walk that does not exist. `radiusYMm`
gives an **ellipse**, and an ellipse is what it is called: describing one as a
cushion halo would misdescribe where every corner stone sits.

### Mixed halo stone shapes — PARTIAL

A ring's `stoneRef` may name a stone specification other than `primary`, and
that reference is preserved and reported (`JM-HALO-004`). It does not resolve,
because JDL carries exactly one `stone`, so such a ring's stones produce no
geometry. A **compass halo** alternating round and marquise stones therefore
cannot be built, and is reserved rather than approximated.

### More than two rings — PLANNED

`MAX_HALO_RINGS` is 2, set to what is tested rather than to what the arithmetic
would tolerate. A triple halo is a bound change plus a Golden case, not a
redesign.

### A halo radius that hugs a multi-stone group — PLANNED

`centerMemberId: null` encircles a multi-stone centre, which is real. What does
not exist is a ring whose radius follows the *combined outline* of that group:
the ring is a circle or an ellipse, and no group-outline offset capability
exists.

### Designer halo language — PLANNED

Designer proposes flat scalar JDL paths only. Neither `family` nor `halo` is in
its allow-list, because a provider proposing a nested structure could not be
diffed field by field or shown with real field provenance. Adding halo alone
would advertise a capability families do not have.

### Studio halo configuration — PLANNED

No Studio control exposes a halo, for the same reason no Studio control exposes
a family: the shared TypeScript types and the validation mirror exist so a
future panel is a UI change rather than a contract change, and a panel that
existed for halos but not families would advertise more than the product has.
The frontend never advertises an unsupported variant: `HaloVariant` mirrors
exactly the three the backend compiles.

### Vision — works, and deliberately unchanged

A halo stone reaches the viewer as a real backend-generated STL like any other
component, and is classified as a stone by the `geometryRole` field the preview
manifest already computes from `geometry/roles.py` — which recognizes the
`stone_reference.` prefix. No frontend code was added, and none was needed: a
parallel visual-only halo representation is exactly what VISION-GOV-001/002
forbid, because it could diverge from the CAD geometry.

`frontend/src/vision/types.ts::ComponentName` still lists the four historical
names. It is a declared type, not a key into the manifest — the viewer iterates
the real manifest entries — so it neither filters nor drops a halo stone. It was
left alone rather than widened to a template literal type that would suggest the
frontend knows the naming contract; the backend owns that contract.

### Any professional halo rule — PLANNED

No minimum spacing, no centre-to-halo proportion, no settable radius, no
pavilion-clearance check for a hidden halo. Each needs sourced professional
evidence this project does not have. The active professional-validation registry
holds **zero** records, and every halo capability is `NOT_REVIEWED`.

## What Sprint 24's boundary said, and what changed

Sprint 24 recorded a setting strategy for accents as its one unmet dependency.
That is still unmet, and it is the same dependency: halo metal and accent metal
are the same missing capability seen from two directions. Nothing in this sprint
narrowed it, and nothing in this sprint pretended to.

| Sprint 24 dependency | Status after Sprint 25 |
| --- | --- |
| A per-instance transform on the stone builder | **done** (Sprint 24) — reused unchanged |
| Instance-aware Geometry Inspection | **done** (Sprint 24) — reused unchanged |
| Instance overrides applied to geometry | **done** (Sprint 24) — reused unchanged |
| A vertical offset reaching the solid | **done** — required by the hidden halo |
| A setting strategy for accent/halo stones (RFC) | **not done**, and deliberately |
