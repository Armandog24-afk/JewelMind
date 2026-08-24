---
id: JM-BIBLE-190
title: Foundry Governance
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-090
  - JM-BIBLE-120
  - JM-BIBLE-160
related_documents:
  - JM-BIBLE-FOUNDRY-README
implementation_status: current
professional_validation: not_required
normative: true
---

# Foundry Governance

## FOUNDRY-GOV-001 through FOUNDRY-GOV-018

| ID | Rule |
|---|---|
| **FOUNDRY-GOV-001** | Foundry must not alter jewelry design intent. It packages already-generated geometry and metadata into files; it never changes a `JewelryDefinition` value, geometry, or a Forge validation outcome to make an export "succeed." |
| **FOUNDRY-GOV-002** | Never fake an export — restates CLAUDE.md's "Never fake an export" at the artifact-generation layer. Every STEP/STL byte comes from a real `Shape.exportStep()`/`exportStl()` call against real B-Rep geometry; JSON comes from a real `model_dump()`; a specification comes from real computed values. No placeholder file, stub byte string, or hardcoded sample is ever returned as a successful artifact. |
| **FOUNDRY-GOV-003** | Foundry must never introduce a jewelry-domain threshold. A numeric rule belongs in Forge (`backend/jewelmind/validation/`) with a rule ID; an exporter or artifact-integrity check may only test structural/file-level facts (file exists, is non-empty, has the expected format signature), never a jewelry proportion or tolerance. |
| **FOUNDRY-GOV-004** | StoneReference is excluded from production exports by default — see [`195-component-inclusion-policy.md`](195-component-inclusion-policy.md) and [`196-production-geometry-selection.md`](196-production-geometry-selection.md). Restates LAW-006/ATLAS-GOV-007 at the export layer. |
| **FOUNDRY-GOV-005** | Foundry must never claim manufacturing readiness for any artifact it produces. The professional-review notice (`PROFESSIONAL_REVIEW_NOTICE`) applies to every exported artifact that can carry prose, not only the in-app viewer header. |
| **FOUNDRY-GOV-006** | STEP export must never claim to preserve parametric history, a native CAD feature tree, MatrixGold-equivalent editability, Rhino-native structure, or guaranteed import quality in every CAD application — see [`197-step-export-contract.md`](197-step-export-contract.md). |
| **FOUNDRY-GOV-007** | STL export must never claim to preserve JDL parametric information or B-Rep topology — it is a derived, tessellated, one-way artifact; see [`198-stl-export-contract.md`](198-stl-export-contract.md). |
| **FOUNDRY-GOV-008** | Every exporter writes one complete, real file per artifact in a single operation. No export path may return a partial, empty, or corrupt file as a success — enforced today by `validate_non_empty()` in `exporters/integrity.py`. |
| **FOUNDRY-GOV-009** | Foundry must never silently drop a required production component from an export. A missing or failed required component is a failure the caller can observe, never a quietly smaller file — restates ATLAS-GOV-006/LAW-005 at the export layer. |
| **FOUNDRY-GOV-010** | Foundry diagnostic codes are stable once published — never renamed or reused. Restates FORGE-GOV-001/JDL-GOV-007 at the export layer; see [`204-export-diagnostics.md`](204-export-diagnostics.md). |
| **FOUNDRY-GOV-011** | Foundry must never expose an internal server path, stack trace, or filesystem detail in a public error message or response header. |
| **FOUNDRY-GOV-012** | Foundry must never guess a unit. Every artifact's unit contract must be grounded in actual exporter/format behaviour, inspected directly from real output — see [`212-unit-and-scale-contract.md`](212-unit-and-scale-contract.md). |
| **FOUNDRY-GOV-013** | STL must never become the canonical source geometry. Every export or preview always re-tessellates from the live B-Rep; nothing ever reads geometry back from a previously written mesh file. Restates ATLAS-GOV-009 at the export layer. |
| **FOUNDRY-GOV-014** | Foundry must never call an untested external CAD workflow "validated." A `WORKFLOW_VALIDATED` interoperability claim requires an actual recorded test run, never an assumption of format compatibility — see [`209-cad-interoperability-philosophy.md`](209-cad-interoperability-philosophy.md). |
| **FOUNDRY-GOV-015** | Every temporary file Foundry creates is cleaned up on both the success and failure path — see [`207-temp-file-lifecycle.md`](207-temp-file-lifecycle.md). |
| **FOUNDRY-GOV-016** | A changed export default (which components are included, whether the stone is included by default, which artifact formats exist) is a MAJOR, documented change — never a silent behavior shift. |
| **FOUNDRY-GOV-017** | Foundry must report partial success honestly. If some requested artifacts succeed and others fail, the caller must be able to tell which is which; Foundry must never report complete success when a required artifact failed — see [`205-export-failure-and-partial-success.md`](205-export-failure-and-partial-success.md). |
| **FOUNDRY-GOV-018** | Foundry preserves the Atlas/Forge boundary at the export layer: it reports what was exported and whether it passed an integrity check, but it never interprets a geometric fact as a jewelry-domain violation (Forge's job) and never constructs or mutates geometry itself (Atlas's job). Restates ATLAS-GOV-001/002. |

## When an ADR is required

Replacing the export format set, changing which components are included in a production export by default, changing StoneReference's default export inclusion, moving integrity validation to a different layer, or any change that violates FOUNDRY-GOV-001 through FOUNDRY-GOV-018 without superseding this document first.

## When an RFC is required

Adding a new artifact format beyond STEP/STL/JSON/technical specification, or a structural change to how artifacts are requested/manifested across the whole pipeline. Adding a single new integrity check to an existing format does not require an RFC, only the standard code+docs+tests change.
