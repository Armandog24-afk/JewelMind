---
id: JM-BIBLE-023
title: Data Flow
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-007
related_documents:
  - JM-BIBLE-020
  - JM-BIBLE-A03
  - JM-BIBLE-063
implementation_status: current
---

# Data Flow

Request-by-request walkthrough of the current system. Endpoint details
(exact request/response shapes) are in `docs/api.md` and
[`appendices/api-inventory.md`](../appendices/api-inventory.md); this
document is about *sequencing and responsibility handoff*.

**Relationship to JDL (Sprint 3):** the flows below are the current,
concrete instance of the eleven-stage JDL processing model in
[`05-jdl/063-jdl-processing-model.md`](../05-jdl/063-jdl-processing-model.md)
(JDL-0 through JDL-10). `validate_definition()` covers JDL-5/JDL-6,
`build_solitaire_ring()` covers JDL-7/JDL-8, and the exporters cover
JDL-10. This document does not restate that model; it shows exactly where
each stage lives in the running request/response sequence.

## `POST /api/models/validate`

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant API as api/routes.py
    participant VAL as validation/engine.py
    FE->>API: JewelryDefinition
    API->>VAL: validate_definition(definition)
    VAL-->>API: ValidationResult list
    API-->>FE: results, hasErrors
```

Deliberately does not touch `model_service` or CadQuery at all (see
[`022-domain-boundaries.md`](022-domain-boundaries.md)) — this is why
validation keeps working even if the CAD engine is down.

## `POST /api/models/generate`

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant API as api/routes.py
    participant MS as services/model_service.py
    participant VAL as validation/engine.py
    participant GEO as geometry/assemblies/solitaire.py
    participant PV as preview/mesh.py
    FE->>API: JewelryDefinition
    API->>MS: generate(definition)
    MS->>VAL: validate_definition(definition)
    alt has errors
        VAL-->>MS: errors present
        MS-->>API: raise ValidationBlockedError
        API-->>FE: 422 VALIDATION_BLOCKED
    else valid
        VAL-->>MS: no errors
        MS->>GEO: build_solitaire_ring(definition)
        GEO-->>MS: GeneratedModel
        MS->>PV: write_component_previews(model)
        PV-->>MS: preview manifest
        MS-->>API: ModelRecord (cached by definition hash)
        API-->>FE: modelId, validation, metadata, previewComponents
    end
```

## `GET /api/models/{modelId}/preview/{componentName}`

The frontend calls this once per visible component after a successful
generate. Each call streams a real binary STL file from the model's temp
directory (`model_service.preview_file`) — see LAW-002.

## `POST /api/models/export/step` and `/export/stl`

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant API as api/routes.py
    participant MS as services/model_service.py
    participant EXP as exporters/step_exporter.py
    FE->>API: modelId, includeStoneReference
    API->>MS: get_record(modelId)
    alt unknown modelId
        MS-->>API: raise ModelNotFoundError
        API-->>FE: 404 MODEL_NOT_FOUND
    else found
        API->>MS: export_step_file(modelId, ...)
        MS->>MS: unique temp file (tempfile.mkstemp)
        MS->>EXP: export_step(model, destination, include_stone)
        EXP-->>MS: written file path
        MS-->>API: path
        API-->>FE: FileResponse (background task deletes temp file after send)
    end
```

STL follows the same shape, with an additional tolerance-validation step
in `api/schemas.py::ExportStlRequest` before the request even reaches the
handler (see [`013-functional-requirements.md`](../01-product/013-functional-requirements.md)
JM-FR-019/020).

## `POST /api/models/export/json` and `/specification`

Both resolve the cached `ModelRecord` by `modelId` and render from data
already present on it (`record.definition` and, for the specification,
`record.generated_at` — see JM-FR-017) — neither touches CadQuery again.

## Responsibility handoff summary

| Step | Owner | Hands off to |
|---|---|---|
| Instant feedback while typing | Frontend validation mirror | Nothing — purely advisory |
| Authoritative validation | Backend `validation/engine.py` | Geometry, only if valid |
| Geometry construction | `geometry/` | Assembly builder |
| Assembly + hashing | `geometry/assemblies/solitaire.py` | Model service cache |
| Caching + temp files | `services/model_service.py` | Preview / export on demand |
| Preview tessellation | `preview/mesh.py` | Frontend, via URL |
| File export | `exporters/` | Frontend, via download |
