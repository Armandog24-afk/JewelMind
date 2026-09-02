---
id: JM-BIBLE-609
title: "Measured Stone Contract"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-02
source_of_truth: true
depends_on:
  - JM-BIBLE-601
related_documents:
  - JM-BIBLE-612
implementation_status: current
professional_validation: not_required
normative: true
---

# Measured Stone Contract

## What a measured stone is

A real physical stone the user has in front of them and has measured. The source
mode exists so that a design can be built around a specific stone rather than
around a nominal size.

## What it is NOT

**A measured stone is not a scanned stone** (brief section 29). If only
length/width/depth are available, JewelMind builds an approximation and labels
it as one.

## The two reference classes

| Class | When | What it means |
|---|---|---|
| `MEASURED_DIMENSION_REFERENCE` | dimensions only | Reference geometry APPROXIMATED from the measurements |
| `MEASURED_OUTLINE_REFERENCE` | a measured outline is also supplied | Built from the supplied outline |

Both are still **reference geometry**. Neither is a model of the physical
stone's real surface, and the technical specification says so explicitly:

> Measured reference class: MEASURED_DIMENSION_REFERENCE — reference geometry
> APPROXIMATED from the supplied measurements. It is NOT a model of the
> physical stone's real surface.

That wording is deliberate and must not be softened. A user who supplies real
caliper readings could reasonably assume the resulting solid *is* their stone;
it is not, and the label is the only thing preventing that assumption.

## Never invent a measurement

`MEASURED_STONE_INSUFFICIENT_DATA` is raised when a required measurement is
absent. JewelMind never infers:

- a missing length, width or depth;
- a measurement source;
- a measurement date;
- an operator note.

`shape` is **optional** for a measured stone, on purpose: a real stone may
genuinely have no known cut, and `None` is the honest answer rather than a
guess. When a shape *is* supplied, it is the operator's judgement about what the
stone resembles, and the reference geometry is built from that judgement plus
the real measurements.

**Enforced by** `test_stone_v2.py::test_missing_measurements_are_never_invented`
and STONEV2-GOV-006.

## Provenance is preserved verbatim

```json
{
  "measurementSource": "Mitutoyo digital caliper",
  "measurementDate": "2026-08-14",
  "operatorNote": "measured across the widest girdle point"
}
```

Carried through unchanged into `StoneSourceProvenance`, into the technical
specification, and into the professional review package. A reviewer needs to
know *how* a number was obtained, and paraphrasing it would destroy exactly that.

`measurementDate` is a caller-supplied opaque string, never generated from the
clock. That is both honesty (JewelMind does not know when the stone was
measured) and determinism (provenance participates in hashing and in Golden
snapshots — see STONEV2-GOV-015).

**Verified:** two builds of the same measured stone produce byte-identical
provenance, and no `createdAt` key exists.

## Dimension provenance

A measured stone's dimensions are labelled `INPUT_MEASUREMENT`, distinct from a
parametric stone's `REQUESTED_PARAMETER`. Geometry Inspection reports both, so a
consumer can tell a number the user measured from a number the user asked for
(brief section 46).

When a measured outline is supplied, dimensions are derived from its points and
still labelled `INPUT_MEASUREMENT` — because the points themselves are
measurements.

## Setting compatibility

A measured stone uses its named shape's compatibility. A measured oval is
`EXPERIMENTAL` for prong and `EXPERIMENTAL` for bezel, exactly like a parametric
oval — the source mode does not change what a setting can grip.

## What is still missing

- **Optional girdle measurements** (brief section 28 mentioned them) are not
  modelled. Adding a girdle thickness or a crown/pavilion split would need
  either a real geometric consumer or it would be recorded data nothing uses.
- **No measurement-tolerance model.** A caliper reading has an uncertainty;
  JewelMind records the number, not its error bar. Introducing one would require
  a sourced tolerance, and inventing one is forbidden.
- **No re-measurement or reconciliation workflow.** Changing a measurement
  produces a new design, with the usual `isStale` behaviour.

## Cross-references

- [`stone-source-provenance.md`](stone-source-provenance.md)
- [`../15-professional-validation/426-review-package-contract.md`](../15-professional-validation/426-review-package-contract.md)
