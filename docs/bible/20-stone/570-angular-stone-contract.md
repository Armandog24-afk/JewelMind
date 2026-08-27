---
id: JM-BIBLE-570
title: Angular Stone Contract
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
  - JM-BIBLE-567
  - JM-BIBLE-572
implementation_status: current
professional_validation: not_required
normative: true
---

# Angular Stone Contract

Covers the three shapes with straight edges: **emerald** and **princess** (`RECTILINEAR_ANGULAR`), and **cushion** (`ROUNDED_RECTILINEAR`). All three are bilaterally symmetric on both horizontal axes.

## EMERALD

| Property | Value |
|---|---|
| Symmetry class | `RECTILINEAR_ANGULAR` |
| Required dimensions | `length`, `width`, `depth` |
| Current setting compatibility | `EXPERIMENTAL` |

### Construction

An 8-point polyline: a rectangle with all four corners clipped diagonally.

```python
clip = _EMERALD_CORNER_CLIP_RATIO * min(hw, hl)      # 0.18
points = [
    (hw - clip, hl), (hw, hl - clip), (hw, -hl + clip), (hw - clip, -hl),
    (-hw + clip, -hl), (-hw, -hl + clip), (-hw, hl - clip), (-hw + clip, hl),
]
return cq.Workplane("XY").polyline(points).close().val()
```

`_EMERALD_CORNER_CLIP_RATIO = 0.18` is a **software reference construction parameter** (`provenance: software_reference_profile`), not a gemological or industry corner ratio. The brief was explicit on this point:

> *"Do NOT expose arbitrary 'industry standard corner ratio'."*

The ratio is deliberately expressed against `min(half_width, half_length)` rather than each axis independently, which guarantees two things: the clip scales sensibly for strongly elongated emeralds, and it can never exceed the shape's own smaller half-extent (which would produce a self-intersecting outline).

### What this is and is not

The characteristic emerald-cut silhouette is a clipped-corner rectangle, and that is what this reproduces. It is **not** an emerald cut: a real emerald cut is defined by its *stepped* crown and pavilion facets, which this three-level loft does not model at all. The name denotes the outline. `isGemologicalReproduction` is `false`.

### Real generated result

`emerald`, 8.0 × 6.0 mm, depth 4.0 → **84.711 mm³**, one valid solid.

## PRINCESS

| Property | Value |
|---|---|
| Symmetry class | `RECTILINEAR_ANGULAR` |
| Required dimensions | `length`, `width`, `depth` |
| Current setting compatibility | `EXPERIMENTAL` |

### Construction

```python
def princess_outline(half_length, half_width, scale):
    return cq.Workplane("XY").rect(2 * half_width * scale, 2 * half_length * scale).val()
```

A plain rectangle. No corner treatment, no bevel, no clip.

### Rectangular princess IS supported

The brief asked for an explicit position on this:

> *"Use length, width, depth with a square default constraint only if current semantic definition requires it. If rectangular princess is unsupported: state that clearly."*

**It is supported.** No constraint forces `length == width`. A princess with `length=7.0, width=5.0` validates and generates a valid rectangular solid exactly as a square one does. The shape is square only when the caller passes equal values.

This was a deliberate choice not to add a constraint: there is no geometric reason to reject a rectangle, and inventing a squareness requirement would have been a fabricated domain rule with no source (STONE-GOV-010). The default Golden case uses 6.5 × 6.5 (square) because that is the natural comparison against the 6.5 mm round default, not because non-square is disallowed.

### Real generated result

`princess`, 6.5 × 6.5 mm, depth 4.0 → **75.480 mm³**, one valid solid.

## CUSHION

| Property | Value |
|---|---|
| Symmetry class | `ROUNDED_RECTILINEAR` |
| Required dimensions | `length`, `width`, `depth` |
| Current setting compatibility | `EXPERIMENTAL` |

### Construction

Four straight edges joined by four quarter-circle arcs:

```python
cr = _CUSHION_CORNER_RATIO * min(hw, hl)      # 0.25
k  = cr * _COS_45                              # cr * cos(45°)

.moveTo(hw - cr, hl)
.lineTo(-hw + cr, hl)
.threePointArc((-hw + cr - k, hl - cr + k), (-hw, hl - cr))
.lineTo(-hw, -hl + cr)
.threePointArc((-hw + cr - k, -hl + cr - k), (-hw + cr, -hl))
.lineTo(hw - cr, -hl)
.threePointArc((hw - cr + k, -hl + cr - k), (hw, -hl + cr))
.lineTo(hw, hl - cr)
.threePointArc((hw - cr + k, hl - cr + k), (hw - cr, hl))
.close()
```

Each `threePointArc` midpoint is the point on that corner's quarter circle at 45°, offset by `k` from the arc centre along both axes.

`_CUSHION_CORNER_RATIO = 0.25` is a software reference construction parameter, again scaled against `min(half_width, half_length)` so the corner radius can never exceed the shape's own half-extent. The brief's guidance was followed exactly:

> *"If internal corner parameter is necessary: use a deterministic software default clearly labeled as reference-geometry construction, not professional standard."*

No commercial cushion subtype semantics (cushion brilliant, cushion modified, "crushed ice") are modelled or implied.

### Two real OpenCascade failures preceded this formulation

Cushion was the only shape that required more than one attempt, and both failures are worth recording because both were silent-looking API traps rather than geometric errors:

**Attempt 1 — fillet on an extruded face.** The natural CadQuery idiom for a rounded rectangle:

```python
cq.Workplane("XY").rect(2*hw, 2*hl).extrude(0.001).faces(">Z").edges().fillet(cr)
```

failed outright with:

```
BRep_API: command not done
```

A fillet on the edges of a near-zero-thickness extruded face is not a construction OpenCascade will perform. This ruled out deriving the outline from a filleted solid and forced explicit line-and-arc construction.

**Attempt 2 — a wrong arc midpoint.** The first explicit construction used `cr * 0.29289` as the corner offset (the `1 − cos(45°)` sagitta value, mistakenly applied as the midpoint offset). OpenCascade rejected it:

```
StdFail_NotDone: GC_MakeArcOfCircle::Value() - no result
```

The three supplied points were not co-circular, so no arc through them exists. Corrected to `k = cr * cos(45°)`, which places the midpoint genuinely on the quarter circle.

Both failures were found during prototyping against the real installed CadQuery 2.8.0, before production code was written — see [`572-stone-generation-pipeline.md`](572-stone-generation-pipeline.md) for the full recorded investigation. The lesson generalises: an arc through three points only exists if the points are actually co-circular, and OpenCascade reports that as a bare `StdFail_NotDone` with no hint about which point is wrong.

### Real generated result

`cushion`, 7.0 × 7.0 mm, depth 4.0 → **86.365 mm³**, one valid solid.

## Shared verified behaviour

| Test | Applies to |
|---|---|
| `TestNonRoundShapeGeneration::*` (3 tests) | all three shapes — valid single solid, measured extents, metal separation |
| `TestStoneStepExport::test_step_roundtrip_has_no_regressions` | emerald, cushion, princess (plus oval) |
| `TestNonRoundAssembly::test_shape_generates_a_fully_connected_solitaire_assembly` | emerald, cushion, princess (plus oval) |
| `TestStoneProductionExportExclusion::test_step_export_excludes_stone_by_default` | all three |

Golden coverage: `SOL-015-emerald-solitaire` (8 × 6), `SOL-016-cushion-solitaire` (7 × 7), `SOL-017-princess-solitaire` (6.5 × 6.5).

## Setting compatibility

All three are `EXPERIMENTAL`, with the same recorded reason in the capability registry: *"Current prong placement is generic/circular, not corner-aware."*

A real angular-stone setting places prongs at the **corners**, because that is where an angular stone is both most vulnerable and most securely gripped. The current layout distributes prongs evenly around a circle derived from `resolved_width_mm`, which for a square or rectangular stone leaves the corners exposed and the prongs sitting mid-edge. Honestly reported, not faked — see [`573-stone-setting-interface.md`](573-stone-setting-interface.md) and Sprint 19.
