---
id: JM-BIBLE-A20
title: "Appendix: Atlas Component Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-130
related_documents:
  - JM-BIBLE-A05
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Atlas Component Catalog

The 4 current geometry components, cross-checked against `backend/jewelmind/geometry/components/*.py` and `backend/jewelmind/geometry/assemblies/solitaire.py` during this Sprint. Real volumes/bounding boxes are for the default definition (`definitionHash: 355ddca57e7e49ad`).

| Component | Type | `geometryRole` | Production included | Preview included | Volume (mm³) | Source file |
|---|---|---|---|---|---|---|
| `band` | Solid | `production_metal` | Yes (default) | Yes | 250.99168317654699 | `geometry/components/band.py` |
| `stone_reference` | Solid | `stone_reference` | No (default; opt-in) | Yes | 58.22141924499569 | `geometry/components/stone.py` |
| `prongs` | Compound (6 solids, default) | `production_metal` | Yes (default) | Yes | 29.650351464580467 | `geometry/components/prongs.py` |
| `basket_support` | Solid | `production_metal` | Yes (default) | Yes | 83.15575842566426 | `geometry/components/basket.py` |
| `channel_walls` | Solid (1; 4 pieces fused) | `production_metal` | Yes (default) | Yes | 109.75999999999999 (`ESM-001`: 0.8mm walls, 5.0mm clear, 9.0mm run, closed ends) | `setting/channel.py` |
| `bars` | Compound (n solids, one per bar) | `production_metal` | Yes (default) | Yes | 66.14999999999999 (`ESM-002`: 3 bars, 0.9mm, 5.0mm long) | `setting/bar.py` |
| `flush_collar` | Solid | `production_metal` | Yes (default) | Yes | 229.75835873021411 (`ESM-003`: 1.2mm collar, 0.5mm rim, stone recessed) | `setting/flush.py` |
| `tension_supports` | Compound (2 solids) | `production_metal` | Yes (default) | Yes | 43.157873897946579 (`ESM-006`: 2.4 x 1.8mm pads, 1.3mm grip height, stone relieved) | `setting/tension.py` |
| `combined_metal` (assembly-level, not a named component) | Solid (1) or Compound (3, fallback) | n/a | Yes, always | No (not previewed separately from its constituent components) | 341.44334316909976 | `geometry/assemblies/solitaire.py` |

**Total components: 4** (plus the one assembly-level derived shape, `combined_metal`, which is not itself a named `GeneratedComponent`).
