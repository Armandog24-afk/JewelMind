---
id: JM-BIBLE-567
title: Stone Reference Geometry Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-STONE-README
  - JM-BIBLE-560
related_documents:
  - JM-BIBLE-566
  - JM-BIBLE-572
  - JM-BIBLE-562
implementation_status: current
professional_validation: not_required
normative: true
---

# Stone Reference Geometry Contract

## STONE_REFERENCE vs FACETED_GEM_MODEL

This distinction is mandatory and must never be blurred (STONE-GOV-011/012).

**`STONE_REFERENCE` — what exists today.** Deterministic geometric reference geometry suitable for CAD construction. It approximates:

- an upper/crown-like region,
- a girdle/reference perimeter,
- a lower/pavilion region,
- a horizontal outline.

It does **not** guarantee, imply, or approximate:

- an exact facet pattern,
- optical behaviour (brilliance, dispersion, light return),
- commercial cutting proportions,
- gemological certification of any kind,
- a specific vendor's measured stone dimensions.

Every generated component sets `isGemologicalReproduction: false`, unconditionally, for every shape.

**`FACETED_GEM_MODEL` — future, not implemented.** A richer layer that would model real facet planes. It does not exist, is not scheduled, and has no code, field, or capability entry. Per STONE-GOV-012 it would be **additive**: `StoneSpec` describes *what stone is wanted*, never *how it is tessellated*, so introducing a faceted layer would change which builder runs — not the definition a caller writes. Introducing it requires an ADR.

## PARAMETRIC_REFERENCE_STONE vs MEASURED_STONE

A second future distinction, also documented only:

- **`PARAMETRIC_REFERENCE_STONE`** — what every shape is today. Geometry derived deterministically from the parameters in `StoneSpec`.
- **`MEASURED_STONE`** — future. Geometry originating from outside the parametric model: supplier-provided dimensions, a 3D scan, or imported CAD.

`MEASURED_STONE` is **not implemented**. There is no field, loader, importer, or capability entry for it. It is recorded here so the eventual distinction has a name, and because it is the natural home for a real-world requirement (a jeweller setting a specific physical stone) that the parametric model cannot serve. Introducing it requires an ADR. See [`579-open-stone-questions.md`](579-open-stone-questions.md).

## The 3-level loft

Every shape — including `round` — is built as a loft through three self-similar outlines of the same shape at three Z levels:

| Level | Z | Outline scale |
|---|---|---|
| Table | `girdle_z + depth * 0.35` | `0.56` |
| Girdle | `girdle_z` | `1.0` |
| Culet | `girdle_z − depth * 0.65` | `0.05` (round: an absolute `0.05 mm` circle) |

where `girdle_z = band_top_z(definition) + definition.setting.basketHeight`.

Non-round shapes assemble it explicitly:

```python
culet_wire  = outline_fn(half_length, half_width, _CULET_SCALE_RATIO).translate((0, 0, girdle_z - pavilion_h))
girdle_wire = outline_fn(half_length, half_width, 1.0).translate((0, 0, girdle_z))
table_wire  = outline_fn(half_length, half_width, _TABLE_TO_GIRDLE_RATIO).translate((0, 0, girdle_z + crown_h))
solid = cq.Solid.makeLoft([culet_wire, girdle_wire, table_wire], ruled=True)
```

`round` uses the equivalent pre-Sprint-18 fluent form (`.circle().workplane().circle().workplane().circle().loft(ruled=True)`), preserved byte-identically — see [`568-round-stone-contract.md`](568-round-stone-contract.md).

`ruled=True` means the surface between consecutive outlines is ruled (straight-line interpolation) rather than a smooth spline through all three. This is a deliberate robustness choice: a ruled loft over three self-similar closed wires is far less likely to produce a self-intersecting or invalid solid than a splined one, and it gives crisp crown and pavilion facet-like faces rather than a bulge.

## The reference profile constants

All of these live in `geometry/stone/builder.py` and `outline.py`, and are documented machine-readably in `specs/stone/v1/stone-reference-profile.schema.json` with `provenance: "software_reference_profile"`:

| Constant | Value | Scope | Meaning |
|---|---|---|---|
| `_CROWN_FRACTION` | `0.35` | all shapes | Fraction of `depth` above the girdle. |
| `_PAVILION_FRACTION` | `0.65` | all shapes | Fraction of `depth` below the girdle. |
| `_TABLE_TO_GIRDLE_RATIO` | `0.56` | all shapes | Outline scale at the table level. |
| `_CULET_RADIUS_MM` | `0.05` | round only | Absolute culet circle radius. |
| `_CULET_SCALE_RATIO` | `0.05` | non-round | Proportional, self-similar culet scale. |
| `_EMERALD_CORNER_CLIP_RATIO` | `0.18` | emerald | Diagonal corner clip, as a fraction of `min(half_width, half_length)`. |
| `_CUSHION_CORNER_RATIO` | `0.25` | cushion | Corner arc radius, as a fraction of `min(half_width, half_length)`. |

**Every one of these is a software reference construction parameter.** None is derived from a gemological standard, an industry table, or a professional source, and none may ever be described as one (STONE-GOV-011). They were chosen to produce robust, deterministic, visually plausible reference geometry and verified only against that criterion.

The crown/pavilion/table trio is deliberately **shared across all 7 shapes**, including round, so every shape has a visually consistent silhouette and so a shape change never alters the depth split. Only the two corner-treatment constants are shape-specific, because only two shapes have corners to treat.

### Why round keeps an absolute culet and the others use a ratio

Round's `_CULET_RADIUS_MM = 0.05` is an absolute value inherited unchanged from the pre-Sprint-18 builder; changing it would change round's geometry and break every existing Golden baseline (STONE-GOV-016).

Non-round shapes cannot use an absolute culet, because "an 0.05 mm emerald outline" is not well defined — the shape has two independent half-extents and corner treatments that scale with them. `_CULET_SCALE_RATIO = 0.05` instead scales the shape's own girdle outline down by 5%, producing a small, self-similar closed wire. This is a real **geometry-engine accommodation**, documented as such: a genuinely degenerate culet (a single point, or a zero-area wire) is exactly the kind of input that makes OpenCascade lofts fail or produce invalid solids.

## Robustness over apparent complexity

The brief's guidance was explicit, and the implementation follows it: *"simplicity and robustness are more important than fake faceting. A clean parametric reference solid is preferable to visually complex but unstable gemstone geometry."*

Concretely, this meant declining to model real facet planes. A brilliant cut has 57–58 facets; an emerald cut has stepped facets on crown and pavilion. Modelling them would have meant either dozens of hand-placed planar cuts per shape (fragile, shape-specific, and slow) or a many-level loft (visually busier but still not gemologically correct, and much more likely to produce invalid solids at extreme proportions).

The three-level ruled loft instead produces, for all 7 shapes:

- exactly one solid,
- passing `isValid()`,
- a finite positive volume,
- a bounding box matching the requested dimensions,
- a clean STEP roundtrip,
- correct behaviour under rotation.

That is what a *reference* solid is for. The visual gap versus a real gemstone is a known, accepted, documented limitation — not a defect to be patched with plausible-looking but unverifiable faceting.

## Real generated results

| Shape | Dimensions | Volume (mm³) |
|---|---|---|
| `round` | d = 6.5 | 58.221419 |
| `oval` | 8 × 6 | 67.350 |
| `pear` | 9 × 6 | 57.413477 |
| `emerald` | 8 × 6 | 84.711 |
| `cushion` | 7 × 7 | 86.365 |
| `princess` | 6.5 × 6.5 | 75.480 |
| `marquise` | 10 × 5 | 62.430 |

All at `depth = 4.0`. Full generated records, including bounding boxes and metadata, are in `specs/stone/v1/examples/`, re-verified live by `test_stone_schemas.py::test_example_reproduces_live`.

The volume ordering is a useful sanity signal in itself: the angular shapes (princess, cushion, emerald) enclose more volume than the smooth ones at comparable extents, and pear — with one pointed end — encloses less than oval at a *greater* length. Both follow directly from the outline areas.

## Cross-references

- [`566-stone-outline-contract.md`](566-stone-outline-contract.md) — the 2D half of this contract.
- [`572-stone-generation-pipeline.md`](572-stone-generation-pipeline.md) — the pipeline and the recorded construction investigation.
- [`574-stone-inspection-contract.md`](574-stone-inspection-contract.md) — how a reference solid is measured after the fact.
