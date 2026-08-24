---
id: JM-BIBLE-187
title: Alchemist Gap Analysis
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-183
related_documents:
  - JM-BIBLE-150
implementation_status: current
professional_validation: not_required
normative: false
---

# Alchemist Gap Analysis

No solution is proposed beyond what's needed to close each gap responsibly — per this Sprint's instruction not to invent solutions merely to fill the document.

| Gap ID | Current state | Target | Risk | Priority | Affected files | Recommended future sprint | Code change required? |
|---|---|---|---|---|---|---|---|
| `ALCHEMIST-GAP-001` No explicit `GeometryPlan` class | Derived values computed and consumed inline | A materialized, inspectable, cacheable plan object | Low today (nothing needs it yet) | Low | `geometry/assemblies/solitaire.py`, all `geometry/components/*.py` | A future sprint that genuinely needs plan inspection/caching | Yes, moderate |
| `ALCHEMIST-GAP-002` Mixed orchestration/geometry responsibilities | `ModelService.generate()` does validation-gate + Atlas call + preview generation + temp-file lifecycle in one function | Cleaner separation, e.g. preview decoupled from generation | Low (all tested, correct) | Medium | `services/model_service.py` | A sprint focused on decoupling preview (see GAP-004) | Yes, moderate |
| `ALCHEMIST-GAP-003` No compilation hash | Only `definitionHash` exists | `compilationHash` including version fingerprint | Medium — cache can serve stale-relative-to-version results (see GAP-005) | Medium | `utils/hashing.py`, `services/model_service.py` | A sprint that ships a second compiler/generator/kernel version | Yes, moderate |
| `ALCHEMIST-GAP-004` Preview coupled to core generation | A preview failure would fail all of `generate()` | Preview generation decoupled into its own callable step, mirroring exports | Low today (no preview failure has ever been observed) but architecturally real | High (clearest, most concrete finding of this Sprint) | `services/model_service.py`, `preview/mesh.py` | Next sprint focused on preview/Vision formalization | Yes, small-to-moderate |
| `ALCHEMIST-GAP-005` Cache not version-fingerprint-aware | Cache key is `definitionHash` alone | Cache key incorporates `compilationHash` | Medium (theoretical today — no second version has ever shipped) | Medium | `services/model_service.py` | Same sprint that implements GAP-003 | Yes, small |
| `ALCHEMIST-GAP-006` No formal compilation state machine | States are implicit in control flow, not named/tracked | An explicit state enum on `ModelRecord`/response | Low | Low | `services/model_service.py`, `api/schemas.py` | Any future observability-focused sprint | Yes, moderate |
| `ALCHEMIST-GAP-007` Limited partial-success model | A model either fully succeeds or fully fails; no `COMPLETED_WITH_WARNINGS` distinct status | An explicit status distinguishing "succeeded, but see warnings" from "succeeded cleanly" | Low (warnings are still returned today, just not flagged as a distinct status) | Low | `api/schemas.py::GenerateResponse` | Any future API-refinement sprint | Yes, small |
| `ALCHEMIST-GAP-008` No capability handshake | No endpoint declares what's supported | A `/api/capabilities` endpoint returning `compiler-capabilities.schema.json`'s shape | Low | Low | New `api/routes.py` endpoint | A sprint focused on API self-description | Yes, small |
| `ALCHEMIST-GAP-009` Limited event instrumentation | One log event per generation | Full stage-by-stage structured events (see [`184-compiler-observability.md`](184-compiler-observability.md)) | Low | Low | `services/model_service.py`, all builders | Any future observability sprint | Yes, moderate |
| `ALCHEMIST-GAP-010` Weak separation of compile vs. export stages | Two of the four exporters (STEP, STL) import `cadquery` directly | Exporters request pre-combined shapes from Atlas rather than calling `cq.Compound.makeCompound()` themselves | Low (correct today, just a boundary blur) | Low | `exporters/step_exporter.py`, `stl_exporter.py` | A future Foundry-formalization sprint (Sprint 7) | Yes, small |

## Summary

10 gaps identified. **None requires jewelry expertise** — every gap is a software-architecture question, consistent with Alchemist's role as pure orchestration. The single highest-priority, most concrete gap is `ALCHEMIST-GAP-004` (preview/generation coupling), because it is the one gap with a real, demonstrable failure-mode difference from the target architecture, not merely a structural tidiness question.
