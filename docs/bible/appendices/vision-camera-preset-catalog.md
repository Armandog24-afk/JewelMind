---
id: JM-BIBLE-A42
title: "Appendix: Vision Camera Preset Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-229
related_documents:
  - JM-BIBLE-237
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Vision Camera Preset Catalog

| Preset key | Label | Direction (scene space, unnormalized) |
|---|---|---|
| `perspective` | Perspective | `(1, 0.75, 1)` |
| `front` | Front | `(1, 0.12, 0.001)` |
| `side` | Side | `(0.001, 0.12, 1)` |
| `top` | Top | `(0.0001, 1, 0.0002)` |
| `three_quarter` | Three-quarter | `(1, 0.8, 1)` |

`distance = size * 1.6`, where `size` is the model's real bounding-box diagonal (scene units, mm-equivalent), floored at 5. "Fit to view" and "Reset camera" call `computeFitPose()`/`computeCameraPreset('perspective', ...)` respectively — see [`10-vision/229-camera-system.md`](../10-vision/229-camera-system.md).
