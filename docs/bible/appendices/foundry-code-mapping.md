---
id: JM-BIBLE-A39
title: "Appendix: Foundry Code Mapping"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-217
related_documents:
  - JM-BIBLE-A32
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Foundry Code Mapping

Restates [`09-foundry/217-current-exporter-code-mapping.md`](../09-foundry/217-current-exporter-code-mapping.md)'s table as a standalone quick reference.

| File | Classification |
|---|---|
| `exporters/step_exporter.py` | FOUNDRY (clean as of Sprint 7 — no `cadquery` import) |
| `exporters/stl_exporter.py` | FOUNDRY (clean as of Sprint 7) |
| `exporters/selection.py` | FOUNDRY, one named/tolerated CAD-kernel exception (new this Sprint) |
| `exporters/json_exporter.py` | FOUNDRY |
| `exporters/specification.py` | FOUNDRY |
| `exporters/filenames.py` | FOUNDRY |
| `exporters/integrity.py` | FOUNDRY (new this Sprint) |
| `services/model_service.py::export_step_file()`/`export_stl_file()` | MIXED (API/FOUNDRY/ATLAS-adjacent orchestration) |
| `api/routes.py` export routes | API/FOUNDRY-adjacent |

**Mixed-responsibility modules: 1** (`ModelService.generate()`, unchanged from Sprint 6 — out of this Sprint's scope), down from Sprint 6's count of 3.
