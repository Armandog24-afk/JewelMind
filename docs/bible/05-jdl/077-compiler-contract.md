---
id: JM-BIBLE-077
title: Compiler Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-063
  - JM-BIBLE-076
related_documents:
  - JM-BIBLE-078
  - JM-BIBLE-121
implementation_status: partial
professional_validation: not_required
normative: true
---

# Compiler Contract

**Relationship to Atlas (Sprint 5):** [`07-atlas/121-atlas-architecture-overview.md`](../07-atlas/121-atlas-architecture-overview.md)
and [`07-atlas/132-construction-pipeline.md`](../07-atlas/132-construction-pipeline.md)
give the "Plan + Generate" phase below its own twelve-stage breakdown
(`ATLAS-0`..`ATLAS-11`), confirming the same PARTIAL finding this
document already makes: no separate geometry-plan object exists between
validation and construction — `build_solitaire_ring()` still does both
in one call.

The field-by-field mapping onto current backend types is in [`specs/jdl/v1/compiler-contract.md`](../../../specs/jdl/v1/compiler-contract.md). This document states the contract's intent and the prohibitions that make it a *contract* rather than just a description of what the code happens to do.

## What "compiling" means for JDL v1

Turning a JDL Canonical Document into: validation diagnostics, a geometry plan (today, implicit), generated geometry, geometry metadata, and — on request — exported artifacts. `ModelService.generate()` is the closest current entry point; see [`specs/jdl/v1/compiler-contract.md`](../../../specs/jdl/v1/compiler-contract.md) for its exact phase sequence.

## Determinism requirement (restates JDL-GOV-010)

For a fixed JDL Canonical Document and a fixed `GENERATOR_VERSION`, the compiler must produce the same `definitionHash`, the same per-component volumes and bounding boxes, and the same validation diagnostics, every time, on every machine. This is not a new requirement invented for JDL — it is CLAUDE.md's "Preserve CAD determinism" rule and LAW-003, restated here as a compiler-level contract clause so a future compiler implementation (e.g. a second backend, or a distributed generation worker) has an explicit target to test against.

## Prohibited compiler behaviors

| Prohibition | Why | Current enforcement |
|---|---|---|
| Silently changing user intent | A validation error must be reported, not "corrected" by clamping | `has_errors()` gates generation; no clamping code exists |
| Inventing missing components | A document implies exactly the components its fields describe | `build_solitaire_ring()` always builds exactly band + stone_reference + prongs + basket_support for the current schema — no conditional component invention |
| Ignoring validation errors | LAW-008 | `ValidationBlockedError` raised before `build_solitaire_ring()` runs |
| Fusing the stone into production metal | LAW-006 | `combined_metal` never includes `stone_reference`; verified by `test_geometry.py::test_stone_reference_is_valid_and_separate_from_metal` |
| Silently dropping a failed component | LAW-005 | `_fuse_metal()` falls back to `cq.Compound.makeCompound([...])` with a warning, never a component omission |
| Non-deterministic output | JDL-GOV-010 | No randomness or wall-clock dependency exists in `geometry/` |
| LLM-dependent geometry decisions | LAW-003 | No AI SDK dependency exists in `backend/requirements.txt` |
| Hiding fallback geometry | LAW-005 | Every fallback path appends to `GeneratedComponent.warnings`/`GeneratedModel.warnings`, surfaced in the specification export |

## Current vs. future, explicitly

The current compiler does not materialize a separate "geometry plan" artifact between validation and generation (see [`specs/jdl/v1/compiler-contract.md`](../../../specs/jdl/v1/compiler-contract.md)'s PARTIAL row) — planning and generation happen inside one function call, `build_solitaire_ring()`. This contract does not require splitting that call apart; it only requires that whatever the current implementation does remains deterministic and prohibition-compliant. A future implementation is free to materialize an explicit plan stage as long as it keeps the same guarantees.
