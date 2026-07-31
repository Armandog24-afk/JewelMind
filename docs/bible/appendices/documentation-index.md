---
id: JM-BIBLE-A04
title: "Appendix: Documentation Index"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on: []
related_documents: []
implementation_status: current
---

# Appendix: Documentation Index

Every document in the Technical Bible, plus the pre-existing `docs/`
reference set and the root-level project documents. "Bible" documents
carry a Bible `id`; pre-existing documents do not (they predate the
front-matter convention and are listed here for completeness, per
[`000-bible-governance.md`](../00-foundation/000-bible-governance.md)).

## Technical Bible — `docs/bible/`

| ID | Title | Status | Implementation status | Path |
|---|---|---|---|---|
| JM-BIBLE-README | Technical Bible — Index | accepted | current | [`README.md`](../README.md) |
| JM-BIBLE-000 | Bible Governance | accepted | current | [`00-foundation/000-bible-governance.md`](../00-foundation/000-bible-governance.md) |
| JM-BIBLE-001 | Project Overview | accepted | current | [`00-foundation/001-project-overview.md`](../00-foundation/001-project-overview.md) |
| JM-BIBLE-002 | Vision and Mission | accepted | vision | [`00-foundation/002-vision-and-mission.md`](../00-foundation/002-vision-and-mission.md) |
| JM-BIBLE-003 | Product Principles | accepted | current | [`00-foundation/003-product-principles.md`](../00-foundation/003-product-principles.md) |
| JM-BIBLE-004 | JewelMind Constitution | accepted | current | [`00-foundation/004-jewelmind-constitution.md`](../00-foundation/004-jewelmind-constitution.md) |
| JM-BIBLE-005 | Current Product Status | accepted | current | [`00-foundation/005-current-product-status.md`](../00-foundation/005-current-product-status.md) |
| JM-BIBLE-006 | Scope and Boundaries | accepted | current | [`00-foundation/006-scope-and-boundaries.md`](../00-foundation/006-scope-and-boundaries.md) |
| JM-BIBLE-007 | System Map | accepted | current | [`00-foundation/007-system-map.md`](../00-foundation/007-system-map.md) |
| JM-BIBLE-008 | Glossary | accepted | current | [`00-foundation/008-glossary.md`](../00-foundation/008-glossary.md) |
| JM-BIBLE-010 | User Problems | accepted | current | [`01-product/010-user-problems.md`](../01-product/010-user-problems.md) |
| JM-BIBLE-011 | Target Users | accepted | partial | [`01-product/011-target-users.md`](../01-product/011-target-users.md) |
| JM-BIBLE-012 | Current User Journey | accepted | current | [`01-product/012-current-user-journey.md`](../01-product/012-current-user-journey.md) |
| JM-BIBLE-013 | Functional Requirements | accepted | current | [`01-product/013-functional-requirements.md`](../01-product/013-functional-requirements.md) |
| JM-BIBLE-014 | Non-Functional Requirements | accepted | current | [`01-product/014-non-functional-requirements.md`](../01-product/014-non-functional-requirements.md) |
| JM-BIBLE-015 | Success Metrics | draft | partial | [`01-product/015-success-metrics.md`](../01-product/015-success-metrics.md) |
| JM-BIBLE-020 | Architecture Overview | accepted | current | [`02-architecture/020-architecture-overview.md`](../02-architecture/020-architecture-overview.md) |
| JM-BIBLE-021 | Repository Map | accepted | current | [`02-architecture/021-repository-map.md`](../02-architecture/021-repository-map.md) |
| JM-BIBLE-022 | Domain Boundaries | accepted | current | [`02-architecture/022-domain-boundaries.md`](../02-architecture/022-domain-boundaries.md) |
| JM-BIBLE-023 | Data Flow | accepted | current | [`02-architecture/023-data-flow.md`](../02-architecture/023-data-flow.md) |
| JM-BIBLE-024 | Runtime and Deployment | accepted | current | [`02-architecture/024-runtime-and-deployment.md`](../02-architecture/024-runtime-and-deployment.md) |
| JM-BIBLE-025 | Security and Data Handling | accepted | current | [`02-architecture/025-security-and-data-handling.md`](../02-architecture/025-security-and-data-handling.md) |
| JM-BIBLE-026 | Known Technical Limitations | accepted | current | [`02-architecture/026-known-technical-limitations.md`](../02-architecture/026-known-technical-limitations.md) |
| JM-BIBLE-ADR-INDEX | Architecture Decision Records — Index | accepted | current | [`03-decisions/README.md`](../03-decisions/README.md) |
| JM-BIBLE-ADR-001 | CadQuery for the MVP geometry engine | accepted | current | [`03-decisions/ADR-001-cadquery-for-mvp.md`](../03-decisions/ADR-001-cadquery-for-mvp.md) |
| JM-BIBLE-ADR-002 | No Rhino/commercial CAD runtime dependency | accepted | current | [`03-decisions/ADR-002-no-rhino-runtime-dependency.md`](../03-decisions/ADR-002-no-rhino-runtime-dependency.md) |
| JM-BIBLE-ADR-003 | Deterministic geometry generation | accepted | current | [`03-decisions/ADR-003-deterministic-geometry.md`](../03-decisions/ADR-003-deterministic-geometry.md) |
| JM-BIBLE-ADR-004 | Backend-authoritative validation | accepted | current | [`03-decisions/ADR-004-backend-authoritative-validation.md`](../03-decisions/ADR-004-backend-authoritative-validation.md) |
| JM-BIBLE-ADR-005 | Canonical `JewelryDefinition` schema | accepted | current | [`03-decisions/ADR-005-canonical-jewelry-definition.md`](../03-decisions/ADR-005-canonical-jewelry-definition.md) |
| JM-BIBLE-ADR-006 | Stone reference separated from production metal | accepted | current | [`03-decisions/ADR-006-stone-reference-separated-from-metal.md`](../03-decisions/ADR-006-stone-reference-separated-from-metal.md) |
| JM-BIBLE-ADR-007 | Backend-generated, per-component STL preview (not GLB) | accepted | current | [`03-decisions/ADR-007-backend-generated-preview.md`](../03-decisions/ADR-007-backend-generated-preview.md) |
| JM-BIBLE-ADR-008 | Monorepo architecture | accepted | current | [`03-decisions/ADR-008-monorepo-architecture.md`](../03-decisions/ADR-008-monorepo-architecture.md) |
| JM-BIBLE-ADR-009 | Millimeter-only coordinate/unit system | accepted | current | [`03-decisions/ADR-009-millimeter-coordinate-system.md`](../03-decisions/ADR-009-millimeter-coordinate-system.md) |
| JM-BIBLE-ADR-010 | STEP and STL as the export strategy | accepted | current | [`03-decisions/ADR-010-step-and-stl-export-strategy.md`](../03-decisions/ADR-010-step-and-stl-export-strategy.md) |
| JM-BIBLE-A01 | Appendix: Implementation Inventory | accepted | current | [`appendices/implementation-inventory.md`](implementation-inventory.md) |
| JM-BIBLE-A02 | Appendix: Test Inventory | accepted | current | [`appendices/test-inventory.md`](test-inventory.md) |
| JM-BIBLE-A03 | Appendix: API Inventory | accepted | current | [`appendices/api-inventory.md`](api-inventory.md) |
| JM-BIBLE-A04 | Appendix: Documentation Index | accepted | current | [`appendices/documentation-index.md`](documentation-index.md) (this document) |

## Pre-existing technical reference — `docs/`

These predate the Bible and remain authoritative for their own detail
(see [`000-bible-governance.md`](../00-foundation/000-bible-governance.md)).
No Bible `id` is assigned to them in this Sprint 1 pass.

| Title | Status | Path |
|---|---|---|
| Architecture | authoritative (detail level) | [`../../architecture.md`](../../architecture.md) |
| API reference | authoritative (detail level) | [`../../api.md`](../../api.md) |
| Development guide | authoritative (detail level) | [`../../development.md`](../../development.md) |
| Domain model | authoritative (detail level) | [`../../domain-model.md`](../../domain-model.md) |
| Geometry conventions | authoritative (detail level) | [`../../geometry-conventions.md`](../../geometry-conventions.md) |
| Known limitations | authoritative (detail level) | [`../../known-limitations.md`](../../known-limitations.md) |
| Validation rules | authoritative (detail level) | [`../../validation-rules.md`](../../validation-rules.md) |

## Root-level project documents

| Title | Purpose | Path |
|---|---|---|
| README | Product description, setup, commands | [`../../../README.md`](../../../README.md) |
| CLAUDE.md | Non-negotiable rules for coding agents, including Technical Bible rules | [`../../../CLAUDE.md`](../../../CLAUDE.md) |
| AUDIT_FIXES.md | Data-safety/reliability hardening pass summary | [`../../../AUDIT_FIXES.md`](../../../AUDIT_FIXES.md) |
