---
id: JM-BIBLE-607
title: "Custom Outline Contract"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-02
source_of_truth: true
depends_on:
  - JM-BIBLE-601
related_documents:
  - JM-BIBLE-608
  - JM-BIBLE-613
implementation_status: current
professional_validation: not_required
normative: true
---

# Custom Outline Contract

**This is the escape hatch.** It is the single feature that makes the claim in
STONEV2-GOV-002 true: after Sprint 20 the Stone System no longer depends on a
finite built-in shape list.

## The representation, and why it is points

```json
{
  "points": [{"x": 0.0, "y": 4.0}, {"x": 3.0, "y": 1.5}, ...],
  "unit": "mm",
  "label": "convex reference outline"
}
```

Ordered points, and only ordered points. Two reasons:

1. Every accepted input form — JSON, a vector path, a future SVG adapter — can
   be reduced to points without loss of determinism.
2. Points carry **no capacity to express executable geometry**. JDL's
   no-executable-code rule applies here too: no field, in any representation,
   may carry an expression, script, macro or function body.

Curve segments and SVG import are `PLANNED`. Accepting them would mean
accepting a richer grammar, which is a decision that needs its own RFC.

## The closure rule

**The ring is closed implicitly.** The last point connects back to the first,
and a caller must NOT repeat the first point at the end.

A duplicated closing point is **rejected**, not trimmed. Accepting both
spellings would make the input contract two things instead of one, and would
mean a caller could not tell from the schema which form JewelMind expects.

## The canonical local frame

The outline lies in the local XY plane; depth runs along +Z. LENGTH is the Y
extent, WIDTH the X extent. **The origin is the outline's bounding-box centre.**

Bounding-box centre rather than centroid, because that is what every native
shape already uses — `_apply_orientation()` rotates about the bounding-box
centre, and `StoneSettingReference.centerXMm/centerYMm` reports it. Using a
centroid here would put a custom stone in a different frame from every native
stone and silently misplace every setting built around it.

## Dimensions are derived, not declared

A custom outline has no `length`/`width` fields. Its dimensions come from its own
points, and are labelled `DERIVED_FROM_OUTLINE`.

`domain/stone_dimensions.py` computes them directly from the declared points —
deliberately without importing any geometry kernel, because Forge depends on
that module and Forge must never pull in CadQuery. The arithmetic is a bounding
box over already-declared points, so it is exact and needs no kernel.

## The full pipeline

```
CustomOutline (points, unit, label)
      │
      ├─ validate      reject a malformed outline           (never repair)
      ├─ normalize     unit → mm, winding → CCW, origin → bbox centre
      │                every operation RECORDED in provenance
      ▼
StoneOutline (normalized points, isPolygonal, derivation)
      │
      ├─ outline_builder_for()  →  (scale) -> cq.Wire
      ▼
build_profile(FACETED or CABOCHON)  →  real B-Rep solid
      │
      ▼
StoneSettingReference.outlinePoints  →  a real bezel or prong setting
```

A custom outline reuses the **same** profile pipeline every native shape uses
(brief section 26). It is not a parallel code path.

## The Setting integration — the sprint's architecture proof

Brief section 72 required demonstrating that Sprint 19's Bezel can consume a
custom outline **without a per-shape bezel implementation**.

Before Sprint 20 it could not. `girdle_outline_wire()` looked the outline up in
a table keyed by shape NAME, and dimensions came from named-cut fields, so a
custom stone raised a bare `AssertionError` deep inside `resolved_length_mm()`.

Two changes fixed it:

1. `StoneSettingReference` now carries `outlinePoints` — the real outline the
   Stone System built.
2. `build_stone_setting_reference()` reads dimensions from the **built
   component's metadata** rather than from the request, so it describes the
   stone that exists.

Result: a custom outline — **convex and concave** — drives both the bezel and
prong families with real CAD geometry, and there is no `shape == "custom"`
branch anywhere in the Setting System. That absence is verified structurally, by
AST-parsing every setting module for a comparison of `.shape` against a string
literal.

That scan also found two **pre-existing** name branches and removed them:
strategy selection now reads `isRadiallySymmetric` (a geometric property)
instead of `shape == "round"`, and `round` was given a signature-adapted entry
in the outline-builder table instead of its own conditional.

### One subtlety: exact wires beat carried points

`girdle_outline_wire()` prefers a native shape's **exact analytic builder** and
falls back to the carried points only when there is no builder — custom,
imported, or measured-with-outline.

Preferring the points would have been simpler and was measurably wrong: the
carried points are a 48-point discretization, so an oval bezel built from them
stopped needing its documented STEP-safety repair (a polyline has no ELLIPSE
edge to offset into an `OFFSET` curve) and the oval's `OUTLINE_CARDINAL` prong
moved by 6.3e-5mm. Both small; both geometry changes nobody asked for.

## Concave outlines

Concave outlines **generate valid geometry** — verified with a real 7-point
concave test outline producing a valid single solid with an exact STEP
roundtrip, and a working bezel.

They are honestly recorded as a known limitation rather than a blanket
guarantee: the Golden case covers a convex outline, and not every possible
concavity is bezel-verified. A deep enough notch could make a constant offset
self-intersect, and that has not been characterized.

## Cross-references

- [`custom-outline-validation.md`](custom-outline-validation.md) — exactly what
  is rejected.
- [`stone-setting-compatibility-v2.md`](stone-setting-compatibility-v2.md)
- [`../21-setting/bezel-setting-contract.md`](../21-setting/bezel-setting-contract.md)
