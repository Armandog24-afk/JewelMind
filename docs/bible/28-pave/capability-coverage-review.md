---
id: JM-BIBLE-PAVE-RESEARCH
title: "Pavé capability coverage review"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-08
source_of_truth: false
depends_on:
  - JM-BIBLE-PAVE-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Pavé capability coverage review

The Sprint 26 brief (§32) asks whether the subsystem's **architecture** covers
what contemporary professional jewelry CAD treats as pavé and microsetting —
specifically to avoid an architectural omission, not to assemble a feature list.

This document records that check. It is deliberately **not** a competitor
comparison: JewelMind has no measured access to another product's internals, and
a claim about what another tool does would be exactly the unsourced assertion
this project refuses elsewhere. What follows is a check of the CONCEPT against
the primitives this subsystem exposes.

## The primitives a pavé subsystem needs

| Primitive | Present? | Where |
| --- | --- | --- |
| A host surface, referenced deterministically | yes | `PaveHost` + `ResolvedHostSurface` |
| A lattice over that surface's own parameters | yes | `surface_lattices()` |
| A pitch in millimetres, independent of the surface's curvature | yes | `pitchMm`/`stoneSpacingMm`, converted at the surface radius |
| Rows, and a row offset | yes | `rowCount`, `rowOffsetFraction`, `STAGGERED` |
| A stone size independent of the centre stone | yes | `stoneScale` |
| Stone orientation following the surface normal | yes | `tiltDeg`/`tiltAzimuthDeg` (ADR-011) |
| Retention as a separate, named concept | yes | `PaveRetentionStrategy` |
| Shared retention between neighbours | yes | `SHARED_BEAD`, with `servesPlacementIds` |
| A recess in the host metal | yes | `PaveSeat` → `setting/seat.py` |
| An escape hatch for hand placement | yes | `EXPLICIT` + `explicitPlacements` |
| Containment against the surface's edge | yes | `containment`, and a reported clip count |
| Per-stone identity that survives editing | yes | `<paveId>.r<row>.c<column>` |

The architectural conclusion: **no primitive is missing**. Every deferred
capability below is a matter of scope — another host surface, another retention
solid, more than one field — and none of them requires a new kind of thing in
the model.

## Deferred, and why

| Concept | Status | Why it is scope rather than architecture |
| --- | --- | --- |
| Pavé on a shank's flat sides | PLANNED | needs a band profile that reports a side surface; the lattice would be the same |
| Pavé on a basket wall or prong flank | PLANNED | needs a parameterization of a swept surface; the lattice would be the same |
| Pavé following a stone's own outline (cushion/emerald halo pavé) | PLANNED | needs an outline-offset walk, already recorded as absent for halos in Sprint 25 |
| Channel and bar setting | PLANNED | needs the support rails Sprint 23 recorded as PLANNED; the retention registry already accommodates a new strategy |
| Shared prongs between two stones | PLANNED | Sprint 23's own reserved capability |
| Thread / bright-cut setting | PLANNED | needs a swept cut along the lattice; a per-stone cut does not express it |
| Grain work | PLANNED | a cut-and-pushed surface treatment, not a placed solid; representing it as a sphere would be a bead with another name |
| Graduated stone sizes along a row | PLANNED | the lattice is uniform; a per-cell scale ramp is a parameter, not a new primitive |
| Several fields in one design | PLANNED | needs a rule for what happens where two fields meet |
| Cutter / burr geometry for a setter | PLANNED | manufacturing tooling, and Sprint 23 already recorded it as needing sourced professional geometry |

## What the review deliberately did NOT produce

**No spacing conventions, no bead-size conventions, no density conventions.** A
review of what other software *offers* cannot establish what a setter *requires*,
and a number copied from a screenshot would enter this project as an invented
professional threshold with a citation that does not support it. §16 of the brief
is explicit, and this document adds no number to the codebase.

**No claim that a graduated or outline-following field is "coming".** Each
deferred item above is a capability-registry entry with a stated reason, checked
by a test, rather than a roadmap promise.

## The one architectural decision the review did drive

A pavé is **not** a region fill. Sprint 24's capability row described `pave` as
needing "a region-fill capability the arrangement engine does not have", and
that framing would have led to a different, worse model — a filled area whose
stone count is an output nobody can address individually.

The concept as practised is a **lattice of individually identifiable stones**,
each of which a setter places, adjusts and can lose. That is why every cell is a
real `StoneInstanceDef` with a derived id, why `servesPlacementIds` names the
stones a shared bead touches, and why `clippedCells` is reported rather than
absorbed. The capability row was corrected accordingly.
