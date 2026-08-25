---
id: JM-BIBLE-A43
title: "Appendix: Vision Material Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-232
related_documents:
  - JM-BIBLE-233
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Vision Material Catalog

Restates [`10-vision/232-metal-material-model.md`](../10-vision/232-metal-material-model.md) and [`233-stone-material-model.md`](../10-vision/233-stone-material-model.md) as one flat reference table, kept in sync with `frontend/src/vision/materials.ts` and `specs/vision/v1/test-vectors/material-vectors.json`.

| Key | Color | Metalness (pres. / tech.) | Roughness (pres. / tech.) | Transmission (pres. / tech.) |
|---|---|---|---|---|
| `yellow_gold_18k` | `#d4af37` | 0.95 / 0.55 | 0.28 / 0.55 | 0 / 0 |
| `white_gold_18k` | `#e7e7ea` | 0.95 / 0.55 | 0.20 / 0.55 | 0 / 0 |
| `rose_gold_18k` | `#e3b7a4` | 0.95 / 0.55 | 0.30 / 0.55 | 0 / 0 |
| `platinum` | `#dcdcdc` | 0.95 / 0.55 | 0.18 / 0.55 | 0 / 0 |
| `silver` | `#c8c8ce` | 0.95 / 0.55 | 0.24 / 0.55 | 0 / 0 |
| `stone_reference` | `#eaf6ff` / `#bfe3ff` | 0 / 0.1 | 0.03 / 0.05 | 0.92 / 0 |
