---
id: JM-BIBLE-488
title: Alchemist Inspection Integration
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-INSPECTION-README
  - JM-BIBLE-460
related_documents:
  - JM-BIBLE-168
  - JM-BIBLE-174
  - JM-BIBLE-160
normative: true
implementation_status: current
professional_validation: not_required
---

# Alchemist Inspection Integration

## There is no separate Alchemist runtime module

Grepping `docs/bible/08-alchemist/` and `backend/jewelmind/` for a real, explicitly-implemented "Alchemist" compiler module finds none. `docs/bible/08-alchemist/168-atlas-execution-contract.md` (Sprint 6) already established this precisely: the conceptual `execute_geometry_plan(plan: GeometryPlan) -> AtlasExecutionResult` interface has no real function behind it, because no `GeometryPlan` exists to pass. The real call is `build_solitaire_ring(definition: JewelryDefinition) -> GeneratedModel`, and the real orchestrator that plays Alchemist's architectural role is `ModelService.generate()` in `backend/jewelmind/services/model_service.py`. This Sprint's inspection integration is described here the same honest way — wired into that real orchestrator, not into a fictional separate compilation stage.

## Where inspection actually lands in `AtlasExecutionResult`'s conceptual mapping

`168-atlas-execution-contract.md`'s "Current mapping" table already carried an `inspectionFacts` row before this Sprint, mapped to: *"The one runtime fact (fuse solid count), inline, not returned as a separate structured list."* This Sprint materially changes that mapping without changing the table's shape:

| `AtlasExecutionResult` field (conceptual) | Mapping before Sprint 14 | Mapping after Sprint 14 |
|---|---|---|
| `inspectionFacts` | The one runtime fact (fuse solid count), inline, not returned as a separate structured list | `ModelRecord.inspection_report: GeometryInspectionReport` — a real, separate, structured result with `componentResults`, `assemblyResult`, and a flattened `geometricFacts: list[GeometricFact]` |

Every other row in that table (`executionStatus`, `componentResults`, `assembly`, `geometryMetadata`, `fallbacks`, `warnings`, `errors`, `duration`) is unchanged by this Sprint — inspection is additive to `ModelService.generate()`'s existing return shape, not a replacement of it.

## The real target sequence, mapped onto real code

```
JDL (JewelryDefinition)
  → validate_definition() [Forge, pre-generation — unchanged]
  → build_solitaire_ring(definition) [Atlas generation — unchanged]
  → write_component_previews(...) [preview manifest — unchanged, runs before inspection]
  → inspect_model(generated_model) [Atlas inspection — NEW this Sprint]
  → ModelRecord.inspection_report [stored — NEW this Sprint]
  → (Forge post-geometry evaluation of inspection_report — NOT wired, see 487-forge-fact-contract.md)
  → ModelRecord returned to the API layer
```

This is the literal, current body of `ModelService.generate()` (`backend/jewelmind/services/model_service.py`, lines ~67-113): validation, `build_solitaire_ring()`, `write_component_previews()`, then `inspect_model(generated_model)`, then `ModelRecord(...)` construction with `inspection_report=inspection_report`. The inline comment at the call site is explicit about scope:

> "Real runtime geometry inspection (Sprint 14) — read-only, never blocks generation on its own result"

No `GeometryPlan` was introduced, no new compiler stage class was created, and no code was added to `services/model_service.py` that imports `cadquery` (confirmed — the file imports only `jewelmind.geometry.inspection.inspector.inspect_model` and `jewelmind.geometry.inspection.models.GeometryInspectionReport`, both kernel-neutral per INSPECT-GOV-016).

## What this Sprint deliberately did not do

This Sprint did not build a separate Alchemist module, and did not need to — doing so would have been exactly the kind of broad, unrelated architectural refactor the Sprint 14 brief explicitly warned against, and would have required an ADR per `docs/bible/08-alchemist/160-alchemist-governance.md` (materializing `GeometryPlan` or changing which stage produces which artifact are both listed there as ADR triggers). Wiring inspection into the real current orchestrator instead of a fictional new one is the same discipline `168-atlas-execution-contract.md` already modeled for the Atlas-execution boundary.

## `kernelVersion`: a small, real, partial answer to a Sprint 6 gap

`docs/bible/08-alchemist/174-determinism-and-version-fingerprint.md` documented that only 2 of 8 conceptual `CompilationEnvironmentFingerprint` fields were recorded anywhere in current output — CadQuery version and OpenCascade version were both explicitly "No." This Sprint's `GeometryInspectionReport.kernelVersion` (populated from `cadquery.__version__` via `inspector.py::_kernel_version()`, with a `try`/`except` that returns `None` rather than raising if version introspection itself fails) now records the CadQuery version on every generation — but only inside the inspection report, not as part of `definitionHash` or any future `compilationHash`. This is a real, partial improvement to observability, not a closure of the fingerprint gap `174` describes: OpenCascade's own version (as opposed to CadQuery's) is still not separately recorded, and `kernelVersion` does not participate in any hash or provenance chain today. See [`494-current-runtime-inspection-gap-analysis.md`](494-current-runtime-inspection-gap-analysis.md) for this listed as an open gap, and ALCHEMIST-GOV-009's requirement that a future version-axis addition be recorded formally rather than left as this Sprint leaves it.

## `definitionHash` is untouched

`GeometryInspectionReport.definitionHash` is read from `model.definition_hash` — the same hash `build_solitaire_ring()` already computed before inspection ever runs. Inspection never recomputes, mutates, or influences `definitionHash` in any way, preserving ALCHEMIST-GOV-010 (`definitionHash` never encodes compiler/kernel version) exactly as `docs/bible/08-alchemist/175-definition-hash-vs-compilation-hash.md` requires.
