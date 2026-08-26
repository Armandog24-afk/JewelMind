---
id: JM-BIBLE-541
title: Shank Architecture Overview
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-SHANK-README
  - JM-BIBLE-540
  - JM-BIBLE-ATLAS-README
related_documents:
  - JM-BIBLE-526
  - JM-BIBLE-RING-README
  - JM-BIBLE-120
implementation_status: current
professional_validation: not_required
normative: true
---

# Shank Architecture Overview

## The layering, exactly

```
Atlas (geometry/, Sprint 5 — generic, Ring-agnostic)
  → geometry/connection.py         ShankConnectionInterface + shank_connection_interface()
  → geometry/shank/                 the Shank subsystem (this Sprint)
      profile.py     flat_profile_wire() / comfort_fit_profile_wire() / build_profile()
      taper.py       taper_ratio() / angle_deg_for_u()
      builder.py     _build_uniform_shank() / _build_tapered_shank() / build_shank()
      capability.py  SHANK_CAPABILITIES / get_shank_capability()
  → geometry/components/band.py     build_ring_band = build_shank  (thin, stable re-export)
Ring (ring/, Sprint 16)
  → ring/models.py::ShankDefinition  data mapping only, not a geometry builder
```

`geometry/shank/__init__.py` exposes exactly one symbol, `build_shank`, confirming the package's public surface is a single entry point (`backend/jewelmind/geometry/shank/__init__.py`). Everything else under `geometry/shank/` is an internal implementation module.

## Why the package sits inside Atlas, not Ring

SHANK-GOV-006 requires reusable geometry infrastructure to stay Ring-agnostic: `profile.py` and `taper.py` know nothing about `JewelryDefinition`, `BandSpec`, or any Ring concept — `profile.py::build_profile()` takes only `inner_r`/`outer_r`/`half_width`, and `taper.py::taper_ratio()` takes only `u` and a `BandTaperSpec`. `builder.py` is the one module in the package that imports `jewelmind.domain.schema.JewelryDefinition` and therefore has Ring-shaped knowledge, but it still lives under `jewelmind.geometry` (Atlas), not `jewelmind.ring` — because Atlas's own component builders (`prongs.py`, `basket.py`, `stone.py`) already read `JewelryDefinition` fields directly (this predates Sprint 17; see [`07-atlas/121-atlas-architecture-overview.md`](../07-atlas/121-atlas-architecture-overview.md)). Depending on `JewelryDefinition` is normal for an Atlas component builder; depending on `jewelmind.ring` is not.

`geometry/connection.py` is the sharper case. It is the named handoff between Shank geometry and the `RingHead` component builders (`prongs.py`, `basket.py`), and it could plausibly have been written as a Ring-domain concept. It is not: `ShankConnectionInterface` and `shank_connection_interface()` live at `backend/jewelmind/geometry/connection.py`, in the Atlas layer, specifically so that `prongs.py`/`basket.py` — which are themselves Atlas-layer builders — can depend on it without reaching up into `jewelmind.ring`.

## The circular import this Sprint found and fixed

An earlier version of this same module was placed inside `jewelmind/ring/` during implementation. That produced a real, reproducible circular import:

```
jewelmind.ring.adapter
  → jewelmind.jewelry_category.errors
  → jewelry_category/__init__.py
  → dispatch.py
  → jewelmind.ring.families
  → jewelmind.geometry.assemblies.solitaire
  → geometry/components/basket.py
  → back to jewelmind.ring.connection   (mid-import)
```

This is not an accident of import ordering that a different `import` statement order would have papered over — it is Ring depending on Atlas (`ring.families` → `geometry.assemblies.solitaire`) while an Atlas-layer component builder (`basket.py`) simultaneously depended back on Ring (`ring.connection`), which is exactly the layering direction SHANK-GOV-006 and the Ring Architecture v2 rule ("Ring depends on Atlas, never the reverse," see [`18-ring-architecture/520-jewelry-category-architecture.md`](../18-ring-architecture/520-jewelry-category-architecture.md)) forbid. The fix was to relocate the module to `jewelmind/geometry/connection.py` — an Atlas-layer file — with no change to `ShankConnectionInterface`'s fields or `shank_connection_interface()`'s computation. `prongs.py`/`basket.py` now call `shank_connection_interface(definition)` instead of separately importing `band_top_z()`/`prong_center_radius()`/`EMBED_MM` directly from `geometry/constants.py`.

The fix was verified by importing each affected package independently from a fresh Python process, in more than one order: `python -c "import jewelmind.ring"`, `python -c "import jewelmind.jewelry_category"`, and `python -c "import jewelmind.geometry.components.prongs"` — each succeeding on its own, confirming the cycle was actually broken rather than merely reordered.

## `geometry/components/band.py` as a stable re-export

`geometry/components/band.py` no longer contains the construction logic. It is now exactly:

```python
from jewelmind.geometry.shank.builder import build_shank as build_ring_band
```

This exists so every pre-Sprint-17 caller (`geometry/assemblies/solitaire.py`, `backend/tests/test_geometry.py`) keeps importing `build_ring_band` from the same module path, unchanged — see [`556-current-band-migration.md`](556-current-band-migration.md) for the full migration record. The component's generated name stays `"band"` in both the uniform and tapered metadata shapes; only the internal module that builds it moved.

## Why this matters in practice

The circular-import case is the concrete argument for SHANK-GOV-006 rather than an abstract layering preference: the bug was real, it was caused by exactly the dependency direction the rule prohibits, and the fix required moving one file rather than restructuring the subsystem, because `profile.py`/`taper.py`/`builder.py` had already been kept Ring-agnostic at the primitive level. A future addition to `geometry/shank/` that imports `jewelmind.ring` for any reason — even a seemingly harmless type import — risks reintroducing the same cycle and violates SHANK-GOV-006 directly.
