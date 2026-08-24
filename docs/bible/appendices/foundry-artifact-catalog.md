---
id: JM-BIBLE-A34
title: "Appendix: Foundry Artifact Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-190
related_documents:
  - JM-BIBLE-192
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Foundry Artifact Catalog

| Artifact | Category | Function | Deterministic? | Stone default | Real size (default solitaire) |
|---|---|---|---|---|---|
| STEP | `PRODUCTION_ARTIFACT` | `exporters/step_exporter.py::export_step()` | Geometry: yes. Bytes: no — see [`09-foundry/197-step-export-contract.md`](../09-foundry/197-step-export-contract.md) | Excluded | 197081 bytes |
| STL | `PRODUCTION_ARTIFACT` | `exporters/stl_exporter.py::export_stl()` | Yes, byte-for-byte | Excluded | 522784 bytes (10454 triangles) |
| JSON | `DESIGN_DEFINITION_ARTIFACT` | `exporters/json_exporter.py::export_json()` | Yes, byte-for-byte | n/a (metadata only) | Varies with definition size |
| Technical specification | `TECHNICAL_ARTIFACT` | `exporters/specification.py::build_specification()` | Yes, given a fixed `generated_at` | Dimensions only, always included | Varies with definition/validation results |
| Per-component preview mesh | `PREVIEW_ARTIFACT` | `preview/mesh.py::write_component_previews()` | Yes | Always included (transparent material) | One `.stl` per component |

See [`09-foundry/192-artifact-domain-model.md`](../09-foundry/192-artifact-domain-model.md) for category definitions and lifecycle states.
