---
id: JM-BIBLE-162
title: Compiler Boundaries
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-161
related_documents: []
implementation_status: current
professional_validation: not_required
normative: true
---

# Compiler Boundaries

| Layer | Owns | Current code |
|---|---|---|
| JDL | Declarative design input, schema, canonicalization | `domain/schema.py`, `utils/hashing.py` |
| Forge | Rule evaluation, eligibility, provenance | `validation/rules.py`, `validation/engine.py` |
| Alchemist | Orchestration, sequencing, traceability | `services/model_service.py` (mostly), parts of `api/routes.py` |
| Atlas | Geometry construction, geometric facts | `geometry/**` |
| Foundry (Sprint 7) | Artifact serialization | `exporters/**` |
| Vision (not yet formalized) | Rendering/preview presentation | `preview/mesh.py` (generation half) + frontend viewer (presentation half) |
| API layer | HTTP transport, request/response shape | `api/routes.py`, `api/schemas.py`, `api/errors.py` |
| Cache/storage | Model lifecycle, temp files | `services/model_service.py`'s `ModelService` class |

## Examples of correct vs. wrong placement

| Wrong | Why wrong | Correct |
|---|---|---|
| Alchemist hardcodes a minimum band thickness | Jewelry-domain threshold, not orchestration | Forge evaluates the rule (`JM-BAND-002`); Alchemist reads the result and decides whether to proceed |
| Alchemist directly creates CadQuery cylinders | CAD-kernel construction, not orchestration | Alchemist requests a prong component through a `GeometryPlan`; Atlas builds it (`build_prongs()`) |
| Alchemist writes a STEP file itself | Artifact serialization, not orchestration | Alchemist requests the artifact; the exporter (Foundry-to-be) writes it |
| Alchemist decides preview mesh color | Rendering/presentation, not orchestration | Vision (frontend) decides material/color; Alchemist only ensures real geometry reaches it |

## Where the current code actually blurs this boundary

`ModelService.generate()` is the single largest boundary-blurring point in the current codebase: it performs orchestration (calling validation, then geometry, then preview) **and** directly touches Atlas-level concerns (constructing temp directories for tessellation output) **and** partially overlaps Foundry concerns (it is the thing that ultimately makes preview tessellation happen, not a separate Vision-layer call). This is not a defect — a monorepo backend legitimately doesn't need five separate services for a single-ring-style prototype — but it is worth naming honestly as `MIXED_RESPONSIBILITY` rather than pretending a clean five-layer split already exists in code. See [`183-current-backend-to-compiler-mapping.md`](183-current-backend-to-compiler-mapping.md) for the full classification of every relevant file.
