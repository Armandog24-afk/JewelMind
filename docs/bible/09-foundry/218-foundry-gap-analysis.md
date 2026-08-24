---
id: JM-BIBLE-218
title: Foundry Gap Analysis
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-217
related_documents:
  - JM-BIBLE-187
implementation_status: current
professional_validation: not_required
normative: false
---

# Foundry Gap Analysis

No solution is proposed beyond what's needed to close each gap responsibly — per this Sprint's instruction not to invent solutions merely to fill the document.

## A gap closed this Sprint

`ALCHEMIST-GAP-010` ("Weak separation of compile vs. export stages — two of the four exporters import `cadquery` directly," explicitly recommended for "a future Foundry-formalization sprint (Sprint 7)" by Sprint 6's own gap analysis) is **RESOLVED** by this Sprint's `exporters/selection.py` extraction — see [`217-current-exporter-code-mapping.md`](217-current-exporter-code-mapping.md).

## Remaining and newly identified gaps

| Gap ID | Current state | Target | Risk | Priority | Affected files | Recommended future sprint | Code change required? |
|---|---|---|---|---|---|---|---|
| `FOUNDRY-GAP-001` No unified `ArtifactManifest` | Each artifact type requested and evaluated independently | A single response aggregating outcomes for a multi-artifact request | Low today (no multi-artifact endpoint exists) | Medium | `api/routes.py`, new schema-backed response model | A sprint that ships a combined "export bundle" endpoint | Yes, moderate |
| `FOUNDRY-GAP-002` No `overallStatus`/partial-success vocabulary implemented | Caller infers outcome from independent HTTP results | `ALL_REQUESTED_SUCCEEDED`/`PARTIAL_SUCCESS`/etc. computed by the backend | Low today | Medium | Same as GAP-001 | Same sprint as GAP-001 | Yes, moderate |
| `FOUNDRY-GAP-003` No `ExportVersionFingerprint` assembly | Each field independently queryable, none recorded together | A structured object attached to each artifact record | Low (informational only) | Low | `services/model_service.py`, `exporters/integrity.py` | Any future observability-focused sprint | Yes, small |
| `FOUNDRY-GAP-004` 3 of 13 conceptual diagnostic codes have no real code, and 2 more map to an `AppError` subclass (`ExportFailedError`, code `EXPORT_FAILED`) that is defined in `api/errors.py` but never actually raised by `export_json_route()`/`specification_route()` | JSON/specification export failures surface as unhandled, unstructured 500s instead of the `ErrorEnvelope` shape every other export failure uses | Wire `ExportFailedError` into both routes' `try`/`except`, matching the STEP/STL pattern; add dedicated classes for the 3 fully-missing cases | Low (these paths are rare — malformed JSON export, disk-full temp errors) but the dead-code class is a genuine, easily-fixed inconsistency | Medium | `api/errors.py`, `api/routes.py` | Any future error-handling-refinement sprint | Yes, small |
| `FOUNDRY-GAP-005` No runtime STEP format-signature check | Only STL has `binary_stl_triangle_count()` | An equivalent lightweight STEP header/signature check | Low | Low | `exporters/integrity.py` | Any future hardening sprint | Yes, small |
| `FOUNDRY-GAP-006` No STL geometric roundtrip, only structural | Header/size check only, no mesh-fidelity comparison | A real mesh-level roundtrip, if a suitable dependency-free approach is found | Low | Low | `backend/tests/test_export_integrity.py` | A sprint willing to evaluate a new dependency | Uncertain — may require a new library, which FOUNDRY-GOV-014's "no fragile dependency" spirit cautions against |
| `FOUNDRY-GAP-007` No external CAD application has ever imported a JewelMind STEP/STL file | All external interoperability claims remain `EXPORT_SUPPORTED` only | At least one real `IMPORT_TESTED` result against FreeCAD (no purchase required) | Low (no evidence of incompatibility, just no evidence of compatibility either) | Medium | none (testing activity, not code) | A sprint with access to install FreeCAD | No |
| `FOUNDRY-GAP-008` No janitor process for crash-orphaned temp files | Relies entirely on the happy-path `BackgroundTask`/`except` cleanup | A periodic sweep of stale `jewelmind_*_export_*` files | Low (prototype scale, restart-friendly) | Low | `services/model_service.py` | Any future operations-hardening sprint | Yes, small |
| `FOUNDRY-GAP-009` No concurrency/rate limit on export endpoints | Same as `08-alchemist/186` finding | A per-client rate limit or concurrency cap | Low (prototype scale) | Low | `api/routes.py` | Any future production-hardening sprint | Yes, moderate |

## Summary

9 new/remaining gaps identified, plus 1 (`ALCHEMIST-GAP-010`) closed. **None requires jewelry expertise** — every gap is a software-architecture or testing-coverage question, consistent with Foundry's role as artifact packaging and integrity validation, never jewelry-domain interpretation. The highest-priority remaining gap is `FOUNDRY-GAP-007` (no real external CAD interoperability test has ever been performed), because it is the one gap whose resolution requires no code change at all — only access to a free tool (FreeCAD) and the discipline to record a real result.
