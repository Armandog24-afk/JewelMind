---
id: JM-BIBLE-A22
title: "Appendix: Atlas Coordinate Reference"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-123
related_documents: []
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Atlas Coordinate Reference

| Concept | Value |
|---|---|
| World origin | Center of the ring / finger hole |
| Finger-hole axis | Global Y |
| Band plane | X/Z |
| Ring top | `(0, 0, +outer_radius)` |
| Assembly anchor axis | `x=0, y=0`, parallel to Z, from `z=band_top_z` upward |
| Positive Z | Away from the band, toward the stone |
| Prong angular origin | `prong_0` at local angle 0 (positive local X) |
| Rotation direction | Counterclockwise (increasing index → increasing angle via `math.cos`/`math.sin`) |
| `EMBED_MM` | 0.4mm — cross-component embedding depth |

Real derived values for the default definition (`definitionHash: 355ddca57e7e49ad`): `inner_radius=8.9`, `outer_radius=10.700000000000001`, `band_top_z=10.700000000000001`, `prong_center_radius=3.085`. See `specs/atlas/v1/test-vectors/coordinate-vectors.json` for the full real prong-position set.

**No coordinate inconsistency was found** across `band.py`, `stone.py`, `prongs.py`, `basket.py`, and `geometry/assemblies/solitaire.py` — see [`07-atlas/123-coordinate-system-and-orientation.md`](../07-atlas/123-coordinate-system-and-orientation.md) for the confirmation and inspection method.
