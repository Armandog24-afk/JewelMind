---
id: JM-BIBLE-A41
title: "Appendix: Vision Component Style Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-226
related_documents:
  - JM-BIBLE-231
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Vision Component Style Catalog

| Component | `geometryRole` | Technical material | Presentation material |
|---|---|---|---|
| `band` | `production_metal` | Selected metal color, `metalness 0.55`, `roughness 0.55`, no environment | Selected metal color, `metalness 0.95`, per-metal roughness, environment-lit |
| `prongs` | `production_metal` | Same as band | Same as band |
| `basket_support` | `production_metal` | Same as band | Same as band |
| `stone_reference` | `stone_reference` | `#bfe3ff`, `opacity 0.55`, `metalness 0.1`, `roughness 0.05` | `#eaf6ff`, `transmission 0.92`, `ior 2.4`, `clearcoat 1` |

See [`10-vision/232-metal-material-model.md`](../10-vision/232-metal-material-model.md) and [`233-stone-material-model.md`](../10-vision/233-stone-material-model.md) for full parameter tables.
