---
id: JM-BIBLE-551
title: Shank Generation Pipeline
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-SHANK-README
  - JM-BIBLE-540
  - JM-BIBLE-542
related_documents:
  - JM-BIBLE-545
  - JM-BIBLE-548
  - JM-BIBLE-552
implementation_status: current
professional_validation: not_required
normative: true
---

# Shank Generation Pipeline

## Dispatch: `build_shank()`

`geometry/shank/builder.py::build_shank()` is the single public entry point (`geometry/shank/__init__.py` exposes exactly this one symbol). It dispatches deterministically on whether either taper is actually requested — never on a heuristic, a prior call's result, or any external state (SHANK-GOV-001):

```python
def build_shank(definition: JewelryDefinition) -> GeneratedComponent:
    width_taper = definition.band.widthTaper
    thickness_taper = definition.band.thicknessTaper
    if width_taper.mode == "NONE" and thickness_taper.mode == "NONE":
        return _build_uniform_shank(definition)
    return _build_tapered_shank(definition)
```

## The uniform path: byte-identical `revolve()`

`_build_uniform_shank()` is, by design, the exact pre-Sprint-17 construction — the module's own docstring states it was never changed by this Sprint's taper work, and this is what guarantees zero Golden regression for every existing case (SHANK-GOV-003). It builds one profile wire via `build_profile()`, revolves it 360 degrees around the ring's Y axis (`wire.revolve(360, (0, 0, 0), (0, 1, 0))`), and then attempts the outer-rim fillet exactly as before: a fillet radius capped at `min(0.25mm, width * 0.15, thickness * 0.15)`, applied via a `try`/`except` around `_try_fillet_outer_rim()`. If the fillet fails or produces no solid, the exception is caught, a warning is appended, and construction proceeds with sharp edges rather than failing the whole component — this fallback predates Sprint 17 and was not touched by it. `sectionCount: 1` in the returned metadata marks this as the single-section, revolve-based path.

## The tapered path: why loft, not sweep

Sprint 17's brief investigated a sweep-along-a-varying-profile construction before settling on a loft. A real sweep experiment was tried first and abandoned: sweeping a single profile along a path does not by itself vary that profile's own dimensions as it travels the path — the varying width/thickness at each angular position is exactly the information a taper needs to express, and expressing that per-position variation cleanly through a sweep operation was not the direction the implementation converged on. The chosen design instead samples the profile explicitly at many discrete angular positions and lofts through them, which puts the taper's per-position width/thickness values directly into the geometry that gets built, rather than needing them expressed as a property of a single swept profile. This section deliberately does not describe further CadQuery sweep-API mechanics beyond what is stated here, to avoid asserting kernel behavior beyond what was actually verified during this Sprint.

`_build_tapered_shank()`'s real construction:

```python
wires = [
    _section_wire(i / SECTION_COUNT, ..., width_taper, thickness_taper)
    for i in range(SECTION_COUNT + 1)  # +1 closes the loop: wire[N] == wire[0]
]
solid = cq.Solid.makeLoft(wires, ruled=True)
```

Each `_section_wire(u, ...)` reuses the exact same `geometry.shank.profile.build_profile()` used by the uniform path, at a width/thickness resolved by `taper_ratio(u, taper)` and rotated to `angle_deg_for_u(u)` degrees — see [`545-section-profile-contract.md`](545-section-profile-contract.md) and [`548-taper-model.md`](548-taper-model.md) for those two functions' full contracts. Profile generation itself never sees longitudinal variation (SHANK-GOV-004); all taper interpolation happens in `builder.py`/`taper.py`.

## `SECTION_COUNT = 48`, an empirically tuned constant

`SECTION_COUNT` is not a guessed round number. It was chosen by measuring real volume convergence of the tapered loft across 16, 24, 36, 48, and 72 sections: 48 sections landed within 0.16% of the 72-section volume while costing approximately 22% less (fewer profile wires to build and loft). This is the module's own documented justification (`builder.py`'s comment above `SECTION_COUNT`), and per SHANK-GOV-008, changing this constant — or the head-anchoring convention `u=0`, or the `TOWARD_BOTTOM` interpolation formula — is a MAJOR change to Shank's generation contract, requiring a new Golden case or an explicit, documented baseline update, never a silent numeric drift.

## The failure path: `ShankConstructionError`

`_build_tapered_shank()` never silently falls back to a uniform shank on failure. Two explicit failure points, both raising the real `ShankConstructionError` exception (SHANK-GOV-007):

1. `cq.Solid.makeLoft(wires, ruled=True)` raising any exception — caught, re-raised as `ShankConstructionError` with the original exception's message included, never swallowed.
2. A loft that succeeds mechanically but produces no solids (`not solid.Solids()`) or an invalid solid (`not solid.isValid()`) — also raises `ShankConstructionError`, explicitly framed in the message as "not constructible with the current loft-based builder," not a bug to paper over silently.

`_build_uniform_shank()` is not subject to this failure path at all — its only `try`/`except` is around the outer-rim fillet, which degrades to sharp edges on failure rather than failing construction, exactly as before this Sprint.

## What the pipeline reads from the definition

`build_shank()` and its two private builders read exactly: `definition.band.profile`, `definition.band.width`, `definition.band.thickness`, `definition.band.widthTaper`, `definition.band.thicknessTaper`, and (via `inner_radius()`/`outer_radius()`) `definition.ring.innerDiameter`. No other JDL field feeds any part of this pipeline — see [`542-shank-domain-model.md`](542-shank-domain-model.md).
