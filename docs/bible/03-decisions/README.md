---
id: JM-BIBLE-ADR-INDEX
title: Architecture Decision Records — Index
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on: []
related_documents:
  - JM-BIBLE-000
implementation_status: current
---

# Architecture Decision Records

An ADR records a significant architectural decision, the alternatives
that were weighed, and the consequences — so a future reader understands
*why* the system is shaped the way it is, not just *that* it is. See
[`00-foundation/000-bible-governance.md`](../00-foundation/000-bible-governance.md)
for when a new ADR is required.

All ten ADRs below reflect decisions already embodied in the current
repository — they were written by inspecting the actual code, tests, and
structure, not from a separate historical discussion log. Where an
alternative is described as "considered," it is presented as a documented
architectural evaluation grounded in what the codebase would have needed
to do differently, not a claim about a specific past meeting or debate.

| ADR | Title | Status |
|---|---|---|
| [ADR-001](ADR-001-cadquery-for-mvp.md) | CadQuery for the MVP geometry engine | Accepted |
| [ADR-002](ADR-002-no-rhino-runtime-dependency.md) | No Rhino/commercial CAD runtime dependency | Accepted |
| [ADR-003](ADR-003-deterministic-geometry.md) | Deterministic geometry generation | Accepted |
| [ADR-004](ADR-004-backend-authoritative-validation.md) | Backend-authoritative validation | Accepted |
| [ADR-005](ADR-005-canonical-jewelry-definition.md) | Canonical `JewelryDefinition` schema | Accepted |
| [ADR-006](ADR-006-stone-reference-separated-from-metal.md) | Stone reference separated from production metal | Accepted |
| [ADR-007](ADR-007-backend-generated-preview.md) | Backend-generated, per-component STL preview (not GLB) | Accepted |
| [ADR-008](ADR-008-monorepo-architecture.md) | Monorepo architecture | Accepted |
| [ADR-009](ADR-009-millimeter-coordinate-system.md) | Millimeter-only coordinate/unit system | Accepted |
| [ADR-010](ADR-010-step-and-stl-export-strategy.md) | STEP and STL as the export strategy | Accepted |

## Numbering rule

ADRs are numbered sequentially and never renumbered or deleted, even if
superseded — a superseded ADR gets `status: deprecated` in its own front
matter and a link to the ADR that replaced it.
