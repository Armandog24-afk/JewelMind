---
id: JM-BIBLE-160
title: Alchemist Governance
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-090
  - JM-BIBLE-120
related_documents:
  - JM-BIBLE-ALCHEMIST-README
implementation_status: current
professional_validation: not_required
normative: true
---

# Alchemist Governance

## ALCHEMIST-GOV-001 through ALCHEMIST-GOV-015

| ID | Rule |
|---|---|
| **ALCHEMIST-GOV-001** | Alchemist must not invent jewelry intent. It orchestrates; it never guesses a missing or ambiguous design decision on the author's behalf. |
| **ALCHEMIST-GOV-002** | Alchemist must only compile supported JDL capabilities — see [`181-compiler-capability-model.md`](181-compiler-capability-model.md). An unsupported combination produces a diagnostic, never a best-effort guess. |
| **ALCHEMIST-GOV-003** | Blocking Forge diagnostics stop affected compilation stages — restates FORGE-GOV-006/`has_errors()` gating at the Alchemist level; see [`165-forge-evaluation-integration.md`](165-forge-evaluation-integration.md). |
| **ALCHEMIST-GOV-004** | `GeometryPlan` must be deterministic — same inputs, same plan, every time; see [`166-geometry-plan-model.md`](166-geometry-plan-model.md). |
| **ALCHEMIST-GOV-005** | `GeometryPlan` must be traceable to JDL fields — every component plan declares its `sourceJDLPaths`. |
| **ALCHEMIST-GOV-006** | Atlas failures must propagate explicitly — never swallowed silently; see [`172-diagnostics-and-failure-propagation.md`](172-diagnostics-and-failure-propagation.md). |
| **ALCHEMIST-GOV-007** | Required component failures must not be silently ignored — restates ATLAS-GOV-006/LAW-005 at the compiler level. |
| **ALCHEMIST-GOV-008** | Artifact generation must use explicit requests — see [`177-artifact-request-model.md`](177-artifact-request-model.md); no artifact is ever produced as a side effect the caller didn't ask for. |
| **ALCHEMIST-GOV-009** | Compilation outputs must record version fingerprints — see [`174-determinism-and-version-fingerprint.md`](174-determinism-and-version-fingerprint.md). Currently only partially true; see that document's CURRENT/PLANNED table. |
| **ALCHEMIST-GOV-010** | Cached results must never be reused across incompatible compiler/kernel versions — see [`176-compilation-cache-model.md`](176-compilation-cache-model.md). Currently not enforced (the cache key is `definitionHash` alone) — a real, recorded gap. |
| **ALCHEMIST-GOV-011** | Compiler fallbacks must remain observable — restates ATLAS-GOV-005 at the compiler level; every fallback (fillet, fuse) surfaces in `warnings`, never hidden. |
| **ALCHEMIST-GOV-012** | No LLM may make authoritative runtime geometry decisions — restates LAW-003 explicitly for the compilation-orchestration layer, where a future AI-assisted feature (Sprint 4's [`06-forge/114-future-ai-assisted-rule-discovery.md`](../06-forge/114-future-ai-assisted-rule-discovery.md)) might otherwise be tempted to intervene. |
| **ALCHEMIST-GOV-013** | Compilation must preserve StoneReference production exclusion — restates LAW-006/ATLAS-GOV-007 at the compiler level; no compilation path may default `includeStoneReference` to `true`. |
| **ALCHEMIST-GOV-014** | Identical compilation inputs under the same version fingerprint should produce geometrically equivalent results — restates ATLAS-GOV-003/JDL-GOV-010 at the compiler level, with the same honest caveat: geometric equivalence, not necessarily binary file identity (see [`07-atlas/137-determinism-and-reproducibility.md`](../07-atlas/137-determinism-and-reproducibility.md)). |
| **ALCHEMIST-GOV-015** | Compiler orchestration must remain independent of frontend state — `ModelService`/`build_solitaire_ring()` never read `useProjectStore.ts` or any browser-side value; a compilation's result depends only on its `JewelryDefinition` input. |

## When an ADR is required

Introducing a `GeometryPlan` as a real, materialized object; changing which stage produces which artifact (e.g. decoupling preview from core generation); introducing `compilationHash`; changing cache-key strategy; or any change that violates ALCHEMIST-GOV-001 through ALCHEMIST-GOV-015 without superseding this document first.

## When an RFC is required

A major pipeline change: introducing asynchronous/long-running compilation, introducing component-level regeneration, or restructuring the JDL→Forge→Alchemist→Atlas→Foundry/Vision pipeline itself. Adding a single new artifact type to the existing pipeline shape does not require an RFC, only the standard code+docs+tests change.
