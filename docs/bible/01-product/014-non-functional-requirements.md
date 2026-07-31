---
id: JM-BIBLE-014
title: Non-Functional Requirements
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on: []
related_documents:
  - JM-BIBLE-013
  - JM-BIBLE-025
implementation_status: current
---

# Non-Functional Requirements

| ID | Category | Requirement | Status | Evidence |
|---|---|---|---|---|
| JM-NFR-001 | Determinism | The same `JewelryDefinition` must always produce the same geometry, volumes, and definition hash. | current | `test_geometry.py::test_definition_hash_is_deterministic`; [ADR-003](../03-decisions/ADR-003-deterministic-geometry.md) |
| JM-NFR-002 | Reliability | A failed boolean fuse during assembly must fall back to a valid multi-solid compound rather than dropping components. | current | `geometry/assemblies/solitaire.py::_fuse_metal`; [LAW-005](../00-foundation/004-jewelmind-constitution.md) |
| JM-NFR-003 | Reliability | The CAD engine being unavailable must not crash the backend process. | current | `services/cad_engine.py`, lazy import in `api/routes.py::_get_model_service` |
| JM-NFR-004 | Error handling | Every unexpected server error must map to a documented error code and never leak a Python traceback to the client. | current | `backend/jewelmind/api/app.py`; `test_api_hardening.py` |
| JM-NFR-005 | Performance | Generating a default solitaire ring completes in well under one second on the reference development machine. | current | Observed `generationDurationSeconds` values of roughly 0.3–0.6s in test fixtures and manual runs; no formal performance budget defined yet (see 015-success-metrics.md). |
| JM-NFR-006 | Maintainability | Domain logic (validation, geometry) must have no framework (FastAPI/React) imports. | current | Code review of `backend/jewelmind/validation/` and `geometry/` import statements; enforced by convention, not an automated check. |
| JM-NFR-007 | Testability | Every validation rule and every geometry component must have at least one dedicated automated test. | current | `docs/validation-rules.md` cross-referenced against `test_validation.py` (20 tests); `test_geometry.py` (14 tests). |
| JM-NFR-008 | Accessibility | Every form input must have an associated, readable label. | current | `frontend/src/components/ConfigurationPanel.test.tsx::has accessible labels for every numeric field` |
| JM-NFR-009 | Security | No API key, secret, or credential is required or stored anywhere in the running application. | current | `docs/known-limitations.md`; `AUDIT_FIXES.md` §8 (repository secret scan). |
| JM-NFR-010 | Portability | The backend must run without any commercial or GUI-based CAD application. | current | `backend/requirements.txt` (CadQuery only); [ADR-001](../03-decisions/ADR-001-cadquery-for-mvp.md), [ADR-002](../03-decisions/ADR-002-no-rhino-runtime-dependency.md) |
| JM-NFR-011 | CAD independence | The geometry pipeline must not call any LLM or non-deterministic model at runtime. | current | [LAW-003](../00-foundation/004-jewelmind-constitution.md); absence of any AI SDK dependency in `backend/requirements.txt` |
| JM-NFR-012 | Documentation quality | Every architectural decision meeting the criteria in `000-bible-governance.md` must have an ADR. | current | Ten ADRs in [`03-decisions/`](../03-decisions/) |
| JM-NFR-013 | Reliability | Three.js geometries and materials created for the preview must be disposed when replaced or on unmount, to avoid GPU memory growth across repeated regeneration. | current | `frontend/src/hooks/useComponentGeometries.ts`; `useComponentGeometries.test.ts` (dispose-on-replace, dispose-on-unmount tests) |
| JM-NFR-014 | Reliability | In-flight preview-mesh network requests must be cancelled when superseded by a newer request. | current | `useComponentGeometries.ts` (AbortController); `useComponentGeometries.test.ts::aborts the in-flight fetch when superseded` |

## Not yet formally specified

- **Performance under load** (concurrent requests, large batch generation)
  has no defined budget or test — see JM-NFR-005's note and
  [`026-known-technical-limitations.md`](../02-architecture/026-known-technical-limitations.md).
- **Accessibility beyond labeled form inputs** (full keyboard navigation
  audit, screen-reader testing of the 3D viewport) has not been
  systematically verified.
