---
id: JM-BIBLE-134
title: Boolean Operation Strategy
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-133
related_documents:
  - JM-BIBLE-077
implementation_status: current
professional_validation: not_required
normative: true
---

# Boolean Operation Strategy

## Current strategy, exactly

`solitaire.py::_fuse_metal(band, prongs, basket)`:

```python
try:
    fused = band.shape.fuse(basket.shape)
    fused = fused.fuse(prongs.shape)
    if not fused.Solids():
        raise ValueError("fuse produced no solids")
    return fused, []
except Exception as exc:
    warnings.append(f"Combined metal union failed ({exc}); exporting band, prongs, and basket as a multi-solid compound instead of a single fused solid.")
    compound = cq.Compound.makeCompound([band.shape, basket.shape, prongs.shape])
    return compound, warnings
```

- **Union**: `band.fuse(basket)`, then the result `.fuse(prongs)` — two sequential pairwise fuses, not a single N-way boolean.
- **Cut**: used once, in `basket.py` (`outer.cut(inner)`), unrelated to assembly-level fusing.
- **Intersection**: never used anywhere in this codebase.
- **Compound fallback**: `cq.Compound.makeCompound([band.shape, basket.shape, prongs.shape])` — all three original, un-fused solids, never a partial subset.

## Rules this strategy already follows

1. **Never silently discard a component after a failed union** — the fallback compound includes all three solids; none is dropped (LAW-005).
2. **Distinguish a fused production solid from a multi-solid assembly** — `len(model.combined_metal.Solids())` is `1` on success, `3` on fallback; both are recorded, and `test_geometry.py::test_solitaire_assembly_metal_is_single_fused_solid_by_default` asserts the success case explicitly.
3. **Report boolean failures** — a warning is always appended on fallback, surfaced in `GeneratedModel.warnings` and the specification export.
4. **Preserve original components where diagnostic recovery is possible** — `band.shape`, `basket.shape`, `prongs.shape` are still the original, valid, individually-inspectable solids even after a fuse failure; nothing about the fuse attempt mutates them.

## Risk from tolerance-sensitive OpenCascade operations

OCCT's boolean fuse implementation is a well-known source of edge-case failures (coincident/near-coincident faces, tiny overlap regions, specific curve-surface intersection configurations) that are sensitive to the exact geometry passed in and, in principle, to the OCCT version itself. This codebase does not attempt to predict or prevent these failures ahead of time — it accepts that they can happen and always has a valid, real-geometry fallback ready (never a placeholder). This is a deliberate, already-correct design choice, not a gap requiring a fix in this Sprint — see [`137-determinism-and-reproducibility.md`](137-determinism-and-reproducibility.md) for how this interacts with the OCCT-version reproducibility caveat.
