---
id: JM-BIBLE-021
title: Repository Map
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on: []
related_documents:
  - JM-BIBLE-020
  - JM-BIBLE-A01
implementation_status: current
---

# Repository Map

This is a factual map of the repository as it exists today. For what each
module is *responsible for* (as opposed to where it lives), see
[`appendices/implementation-inventory.md`](../appendices/implementation-inventory.md).

## Root

| Path | Purpose |
|---|---|
| `README.md` | Product description, setup, test commands, troubleshooting. |
| `CLAUDE.md` | Non-negotiable rules and quick map for coding agents. |
| `AUDIT_FIXES.md` | Summary of the data-safety/reliability hardening pass. |
| `docker-compose.yml` | Local Docker orchestration (frontend + backend). |
| `.env.example` | Documented, non-secret environment variable defaults. |
| `.github/workflows/ci.yml` | GitHub Actions: backend tests, frontend tests/build, Docker smoke test. |
| `Makefile` | Convenience targets wrapping the commands in `docs/development.md`. |
| `docs/` | Technical reference docs (pre-existing) + this Bible (`docs/bible/`). |
| `examples/` | Sample `JewelryDefinition` JSON files. |
| `scripts/` | Dev convenience scripts (`dev-backend.*`, `dev-frontend.*`, `generate_example.py`). |

## `backend/jewelmind/`

| Path | Purpose |
|---|---|
| `domain/schema.py` | Canonical `JewelryDefinition` (Pydantic v2, strict). |
| `domain/defaults.py` | The default definition (matches the product spec exactly). |
| `domain/disclaimer.py` | The single canonical professional-review notice text. |
| `validation/rules.py` | `ValidationResult` model and rule-ID constants. |
| `validation/engine.py` | The sixteen deterministic validation rule implementations. |
| `validation/sizing.py` | EU/French ring-size ↔ inner-diameter conversion utility. |
| `geometry/constants.py` | The coordinate convention (band revolve axis, assembly anchor point). |
| `geometry/model.py` | `GeneratedComponent`, `GeneratedModel`, `BoundingBox`. |
| `geometry/primitives/selectors.py` | Fillet-edge selection helper for the band. |
| `geometry/components/band.py` | Flat/comfort-fit band builder. |
| `geometry/components/stone.py` | Stone reference builder. |
| `geometry/components/prongs.py` | Prong builder (4 or 6). |
| `geometry/components/basket.py` | Basket support builder. |
| `geometry/assemblies/solitaire.py` | Combines the four components; fuses metal; computes the hash. |
| `preview/mesh.py` | Tessellates each component to a binary STL + manifest. |
| `exporters/filenames.py` | Filename sanitization. |
| `exporters/step_exporter.py` | Real STEP export. |
| `exporters/stl_exporter.py` | Real STL export. |
| `exporters/json_exporter.py` | Canonical JSON export. |
| `exporters/specification.py` | Markdown technical specification. |
| `services/model_service.py` | Orchestration + in-memory model cache + temp-file lifecycle. |
| `services/cad_engine.py` | One-time CadQuery/OpenCascade readiness probe. |
| `api/app.py` | FastAPI app factory, CORS, error handlers, request-ID middleware. |
| `api/routes.py` | All HTTP routes; lazy `model_service` import (see `024-runtime-and-deployment.md`). |
| `api/schemas.py` | Request/response Pydantic models. |
| `api/errors.py` | `AppError` hierarchy and the shared error envelope. |
| `utils/hashing.py` | Canonical JSON serialization + definition hashing. |
| `utils/logging.py` | Structured (structlog) logging configuration. |

## `frontend/src/`

| Path | Purpose |
|---|---|
| `api/client.ts` | Fetch-based API client + response types. |
| `api/types.ts` | TypeScript mirrors of backend response schemas. |
| `store/useProjectStore.ts` | The single Zustand store. |
| `store/persistence.ts` | `localStorage` load/save/clear with structural validation. |
| `hooks/useComponentGeometries.ts` | Fetches, parses, and disposes preview mesh geometries. |
| `components/ConfigurationPanel.tsx` | The left-panel parameter form. |
| `components/ModelViewport.tsx` | The 3D preview viewport (React Three Fiber). |
| `components/ComponentMesh.tsx` | One rendered mesh with material. |
| `components/ValidationPanel.tsx` / `ValidationItem.tsx` | Validation results display. |
| `components/RightPanelTabs.tsx` | Validation / Specification / JSON / Model info tabs. |
| `components/ProjectActions.tsx` | Generate / Export / Reset buttons. |
| `components/BackendStatus.tsx` | Backend health indicator. |
| `components/ProfessionalReviewNotice.tsx` | The permanent disclaimer banner. |

## `shared/`

| Path | Purpose |
|---|---|
| `types/jewelry-definition.ts` | TypeScript mirror of the canonical schema + `isValidJewelryDefinition()` runtime guard. |
| `validation/engine.ts`, `rules.ts`, `sizing.ts` | Frontend validation mirror. |
| `disclaimer.ts` | TypeScript copy of the professional-review notice text. |

## `docs/`

| Path | Purpose |
|---|---|
| `architecture.md`, `api.md`, `domain-model.md`, `geometry-conventions.md`, `validation-rules.md`, `development.md`, `known-limitations.md` | Pre-existing technical reference set (still authoritative for its own detail). |
| `bible/` | This Technical Bible. |

See [`appendices/documentation-index.md`](../appendices/documentation-index.md)
for the complete list of every document with its status.
