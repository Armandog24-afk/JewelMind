---
id: JM-BIBLE-A32
title: "Appendix: Compiler Code Mapping"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-183
related_documents:
  - JM-BIBLE-A26
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Compiler Code Mapping

The condensed table from [`08-alchemist/183-current-backend-to-compiler-mapping.md`](../08-alchemist/183-current-backend-to-compiler-mapping.md).

| File | Classification |
|---|---|
| `api/routes.py`, `api/schemas.py` | API |
| `validation/*.py` | FORGE |
| `services/model_service.py` | ALREADY_ALCHEMIST_LIKE + MIXED_RESPONSIBILITY |
| `geometry/components/*.py`, `geometry/assemblies/solitaire.py` | ATLAS |
| `geometry/constants.py` | ATLAS (today), conceptually ALCHEMIST planning |
| `preview/mesh.py` | VISION (generation half), invoked as MIXED_RESPONSIBILITY |
| `exporters/step_exporter.py`, `stl_exporter.py` | FOUNDRY + MIXED_RESPONSIBILITY (direct `cadquery` import) |
| `exporters/json_exporter.py`, `specification.py`, `filenames.py` | FOUNDRY |
| `utils/hashing.py` | JDL |
| `api/errors.py` | API |
| `services/cad_engine.py` | ATLAS-adjacent |

**Compiler-like services: 1** (`ModelService`). **Mixed-responsibility modules: 3** (`ModelService.generate()`, `step_exporter.py`, `stl_exporter.py`).
