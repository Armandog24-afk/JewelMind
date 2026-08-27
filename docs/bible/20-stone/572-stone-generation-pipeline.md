---
id: JM-BIBLE-572
title: Stone Generation Pipeline
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
  - JM-BIBLE-563
implementation_status: current
professional_validation: not_required
normative: true
---

# Stone Generation Pipeline

## The stages

```
StoneSpec (JDL, already Pydantic-validated)
   │
   ├─ round? ──► _build_round_stone()          ← byte-identical pre-Sprint-18 path
   │                                              (STONE-GOV-016, see 568)
   └─ otherwise ─► _build_non_round_stone():
         1. resolve dimensions       domain/stone_dimensions.py
                                     resolved_length_mm / resolved_width_mm / resolved_depth_mm
         2. look up outline builder  _NON_ROUND_OUTLINE_BUILDERS[shape]
                                     → StoneShapeUnsupportedError on a miss
         3. compute Z levels         girdle_z = band_top_z + basketHeight
                                     crown_h  = depth * 0.35
                                     pavilion_h = depth * 0.65
         4. sample the outline 3×    scales 0.05 (culet), 1.0 (girdle), 0.56 (table)
         5. translate each wire      .translate((0, 0, z))
         6. loft                     cq.Solid.makeLoft([culet, girdle, table], ruled=True)
         7. validate                 .Solids() non-empty AND .isValid()
                                     → StoneGenerationError on failure
         8. apply orientation        _apply_orientation() — own-bbox-center Z rotation
         9. assemble metadata        shape, girdleZMm, crown/pavilion, resolved dims,
                                     orientationDeg, isGemologicalReproduction=False,
                                     referenceGeometryVersion
        10. return                   GeneratedComponent(name="stone_reference", …)
```

Steps 3–10 are entirely **shape-agnostic**. The only per-shape input is the function fetched in step 2. This is what makes an eighth shape a small, local change rather than dispatch surgery.

## Construction-strategy investigation

The brief required selecting the construction strategy *"through actual experiments"* rather than assumption. All seven outlines and all seven three-level lofts were prototyped against the real installed **CadQuery 2.8.0 / OpenCascade** before any production code was written, and additionally checked for a STEP export/re-import roundtrip and a 90° rotation on the two pointed shapes (the riskiest cases).

The strategy chosen — one shared three-level ruled loft over a per-shape 2D outline primitive — was confirmed viable for all seven. Three real failures were found and corrected during that investigation. All three were **API-level traps rather than geometric errors**, which is the main reason recording them is worthwhile.

### Finding 1 — `Workplane.val()` returns an `Edge`, not a `Wire`

The first attempt passed outline results straight to `cq.Solid.makeLoft()` and failed:

```
TypeError: AddWire(): incompatible function arguments. The following argument types are supported:
    1. (self: BRepOffsetAPI_ThruSections, wire: TopoDS_Wire) -> None
Invoked with: <BRepOffsetAPI_ThruSections object>, <TopoDS_Edge object>
```

A CadQuery chain that ends on an arc leaves an `Edge` as the pending object; `.val()` returns that `Edge`. `makeLoft` requires `TopoDS_Wire`. Confirmed directly:

```
marquise no-close val type: Edge    isValid=True
marquise closed  val type: Wire     isValid=True
```

Note `isValid()` returned `True` for the `Edge` too — so a validity check would **not** have caught this. The fix is that every outline function ends with `.close()` where the construction needs it, guaranteeing a `Wire` (see [`566-stone-outline-contract.md`](566-stone-outline-contract.md)).

### Finding 2 — fillet on a near-zero-thickness extruded face is not constructible

The natural CadQuery idiom for a rounded rectangle (cushion):

```python
cq.Workplane("XY").rect(2*hw, 2*hl).extrude(0.001).faces(">Z").edges().fillet(cr)
```

failed with a bare:

```
BRep_API: command not done
```

OpenCascade will not fillet the edges of a 0.001 mm-thick extrusion. This ruled out deriving cushion's outline from a filleted solid and forced explicit line-and-arc construction.

### Finding 3 — a `threePointArc` through non-co-circular points

Cushion's first explicit construction used `cr * 0.29289` as the corner-arc midpoint offset (the `1 − cos(45°)` sagitta value, mistakenly used as a midpoint offset). OpenCascade rejected it:

```
StdFail_NotDone: GC_MakeArcOfCircle::Value() - no result
```

The three supplied points were not co-circular, so no arc through them exists. Corrected to `k = cr * cos(45°)`, which places the midpoint genuinely on the quarter circle. The generalisable lesson: **an arc through three points exists only if the points are actually co-circular, and OpenCascade reports the failure as a bare `StdFail_NotDone` with no indication of which point is wrong.**

### The assumption that turned out unnecessary

The highest-risk going-in assumption was that the pointed shapes (marquise, pear) would need numerical stabilization — a microscopic tip blunting, which the brief explicitly pre-authorized on condition it be documented as a geometry-engine accommodation rather than a jewelry standard.

**They did not, and none was implemented.** Both build valid single solids, survive a STEP roundtrip, and rotate cleanly with the sharp construction as written. `outline.py` contains no tip blunting, no minimum-radius clamp, and no epsilon offset. See [`569-elongated-stone-contract.md`](569-elongated-stone-contract.md) — this is stated explicitly there too, because a future reader might reasonably expect stabilization to exist and "restore" it.

The one accommodation that *does* exist for every non-round shape is the proportional culet (`_CULET_SCALE_RATIO = 0.05` instead of a degenerate point), documented in [`567-stone-reference-geometry-contract.md`](567-stone-reference-geometry-contract.md).

### Why `ruled=True`

A ruled loft interpolates the surface between consecutive sections with straight lines, rather than fitting a smooth spline through all three. This is a deliberate robustness choice: over three self-similar closed wires a ruled loft is markedly less likely to self-intersect or produce an invalid solid than a splined one, and it yields crisp crown and pavilion faces instead of a bulge. It also matches what the pre-Sprint-18 round builder already used, so round's behaviour is unchanged.

## Why one shared pipeline, not seven builders

The brief cautioned in both directions: *"Do not create seven unrelated builders if shared primitives make sense. Also do not force every shape through one overly generic algorithm if it becomes fragile."*

The resolution: **one shared pipeline, seven outline primitives, one deliberate exception.**

- The pipeline (dimension resolution → 3-level sampling → loft → validate → orient) is genuinely identical across shapes and was verified to be robust for all six non-round shapes. Duplicating it six times would have been six places to drift.
- The per-shape variation is entirely 2D and entirely isolated in `outline.py`, where each function is small and independently readable.
- The one exception is `round`, which keeps its own builder — not because the shared path would be fragile for it, but because byte-identical output is a hard requirement and the two loft constructions are not provably bit-identical. See [`568-round-stone-contract.md`](568-round-stone-contract.md).

## The failure path

`StoneGenerationError` (`geometry/stone/errors.py`) is raised in two real situations, both in `_build_non_round_stone()`:

```python
try:
    solid = cq.Solid.makeLoft([culet_wire, girdle_wire, table_wire], ruled=True)
except Exception as exc:
    raise StoneGenerationError(
        f"Could not construct a stone reference for shape={stone.shape!r} …: {exc}. "
        "This is a real construction failure, never silently downgraded to another shape."
    ) from exc

if not solid.Solids() or not solid.isValid():
    raise StoneGenerationError(
        f"The requested stone shape={stone.shape!r} produced no valid solid — …"
    )
```

Both checks matter independently: `makeLoft` can *succeed* and still return something with no solids or failing `isValid()`, which a try/except alone would miss.

Nothing catches `StoneGenerationError` to substitute a different shape, a simpler solid, or an empty component (STONE-GOV-013). A construction failure is an observable error, not a quiet downgrade. `StoneShapeUnsupportedError` covers the separate case of a shape with no registered builder — unreachable in practice because `StoneShape` is a closed enum, but kept as a real explicit guard rather than an implicit `KeyError` (STONE-GOV-007).

## Determinism

No stage reads wall-clock time, randomness, or external state (STONE-GOV-002). The girdle Z depends only on the definition's own ring and setting fields; the outline scales are module constants; the loft is deterministic for fixed input wires. `test_stone_schemas.py::test_example_reproduces_live` re-derives all 7 recorded examples from live code and asserts the volumes match, which is a real determinism check across process runs.

## Performance

Stone generation is a three-wire loft — a single-digit-millisecond operation per shape, not a measurable contributor next to the band's 48-section tapered loft (Sprint 17) or the boolean metal fuse. The full 89-test `test_stone.py` suite, which builds many complete solitaire assemblies including STEP/STL exports and inspection runs, completes in roughly 45 seconds. No shape is a pathological outlier, and no per-shape optimisation was needed or attempted. Per the brief, no SLA is asserted.
