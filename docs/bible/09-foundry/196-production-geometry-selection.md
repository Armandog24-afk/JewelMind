---
id: JM-BIBLE-196
title: Production Geometry Selection
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-195
related_documents:
  - JM-BIBLE-143
implementation_status: current
professional_validation: not_required
normative: true
---

# Production Geometry Selection

## The rule

An exporter selects which shapes to serialize using explicit component identity — `model.combined_metal` and `model.components["stone_reference"].shape` — never by inferring "this is metal" or "this is a gemstone" from a shape's assigned viewer material, color, or any other visual/rendering property. Material assignment lives entirely in the frontend viewer (`ModelViewport.tsx`) and is never consulted by, or even visible to, backend export code.

## Real code (Sprint 7 extraction)

`backend/jewelmind/exporters/selection.py` — `select_export_shapes(model, *, include_stone)` — is called identically by both `step_exporter.py` and `stl_exporter.py`. It was extracted this Sprint from logic that was previously duplicated verbatim in both files (see [`217-current-exporter-code-mapping.md`](217-current-exporter-code-mapping.md) for the exact before/after). It is a pure extraction: no behavior changed, confirmed by the full backend test suite passing unchanged (194 tests) after the refactor.

```python
def select_export_shapes(model: GeneratedModel, *, include_stone: bool) -> cq.Shape:
    shapes = [model.combined_metal]
    if include_stone:
        shapes.append(model.components["stone_reference"].shape)
    return shapes[0] if len(shapes) == 1 else cq.Compound.makeCompound(shapes)
```

## Why this is the right boundary for Foundry to own

`combined_metal` is already fully assembled by Atlas (`_fuse_metal(band, prongs, basket)` in `geometry/assemblies/solitaire.py`) before Foundry ever runs — Foundry does not decide *how* the metal is fused, only *whether* the stone reference joins it as a separate compound member for this particular export. This keeps Foundry's only geometric decision a selection (which pre-built shapes to include), never a construction (Foundry never calls a boolean/fillet/tessellation operation itself) — restating ATLAS-GOV-002/FOUNDRY-GOV-018's Atlas/Foundry boundary concretely.

## Confirmed non-fusion of the stone

`select_export_shapes()` never passes `stone_reference` into the same solid as `combined_metal`; when included, it becomes a second, independent member of a `cq.Compound`. This was verified during Sprint 7 by comparing solid counts: excluding the stone yields the same solid count `combined_metal` reports on its own; including it adds exactly one additional solid, confirmed by `backend/tests/test_foundry_registry.py::test_component_inclusion_vectors_match_live_default_export`.
