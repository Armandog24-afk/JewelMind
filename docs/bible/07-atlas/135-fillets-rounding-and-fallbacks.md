---
id: JM-BIBLE-135
title: Fillets, Rounding, and Fallbacks
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-133
related_documents:
  - JM-BIBLE-A25
implementation_status: current
professional_validation: not_required
normative: true
---

# Fillets, Rounding, and Fallbacks

## The band outer-rim fillet, exactly

From `band.py::build_ring_band`:

```python
fillet_radius = min(
    _FILLET_MAX_MM,                       # 0.25mm, a fixed constant
    definition.band.width * _FILLET_FRACTION,     # 0.15 fraction of width
    definition.band.thickness * _FILLET_FRACTION, # 0.15 fraction of thickness
)
if fillet_radius > 0.02:
    try:
        filleted = _try_fillet_outer_rim(solid, outer_r, fillet_radius)
        if not filleted.solids().vals():
            raise ValueError("fillet produced no solid")
        solid = filleted
    except Exception as exc:
        fallback_used = True
        warnings.append(f"Outer rim fillet could not be applied ({exc}); falling back to sharp edges.")
```

- **Attempted operation**: select the two flat, circular outer-rim edges (via `FlatCircleAtRadius`, `geometry/primitives/selectors.py`) and apply `.fillet(fillet_radius)`.
- **Failure condition**: the fillet call raises an OCCT exception, *or* it succeeds but produces zero solids (checked explicitly).
- **Fallback result**: the pre-fillet, sharp-edged solid — a real, valid, complete solid, just without the rounded rim.
- **Warning generated**: `"Outer rim fillet could not be applied ({exc}); falling back to sharp edges."`, appended to the component's `warnings` list.
- **Geometry difference**: sharp 90° outer edges instead of a rounded rim of radius up to 0.25mm — a small, cosmetic difference; the band's overall dimensions (`inner_radius`, `outer_radius`, `width`) are unaffected either way.
- **Impact on export**: none beyond the cosmetic edge difference — the band is still a single valid solid either way, still fuses (or falls back to compound) the same way downstream.
- **Metadata signal**: `component.metadata["filletApplied"]` is `True`/`False`, letting a caller distinguish the two outcomes without parsing the warning text.

## Three previously-undocumented magic numbers, formalized here

| Constant | Value | Role |
|---|---|---|
| `_FILLET_FRACTION` | 0.15 | Fillet radius is capped at 15% of the band's width or thickness, whichever is smaller |
| `_FILLET_MAX_MM` | 0.25mm | Absolute cap regardless of band size |
| (inline) `0.02` | 0.02mm | Below this fillet radius, the operation is not even attempted (too small to be visually meaningful, and closer to numerical-tolerance territory) |

None of these three appeared in `docs/known-limitations.md`, `docs/geometry-conventions.md`, or any prior Bible sprint before this document. They are not dangerous — the fillet is purely cosmetic and always has a safe fallback — so per this Sprint's instruction, they are documented here rather than "fixed" (there is nothing to fix).

## Comfort-fit has no fallback path

Unlike the flat profile's fillet, the comfort-fit inner arc (`_build_comfort_fit_wire`) has no try/except and no fallback — see [`126-curve-and-profile-model.md`](126-curve-and-profile-model.md). This is a real asymmetry between the two profiles, recorded as a gap in [`150-atlas-gap-analysis.md`](150-atlas-gap-analysis.md), not a defect requiring an immediate fix (no failure has ever been observed for any valid parameter range).

## The full fallback register

See [`atlas-fallback-register.md`](../appendices/atlas-fallback-register.md) for this fillet fallback and the assembly-level fuse fallback (Boolean strategy, [`134-boolean-operation-strategy.md`](134-boolean-operation-strategy.md)) documented side by side with regression-test references and risk assessment. **These are the only two fallback paths that exist anywhere in the current geometry codebase.**
