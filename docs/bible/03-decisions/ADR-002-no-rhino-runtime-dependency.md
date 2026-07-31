---
id: JM-BIBLE-ADR-002
title: "ADR-002: No Rhino/commercial CAD runtime dependency"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on: []
related_documents:
  - JM-BIBLE-ADR-001
  - JM-BIBLE-004
implementation_status: current
---

# ADR-002: No Rhino/commercial CAD runtime dependency

## Status

Accepted.

## Context

Much of the professional jewelry CAD world runs on Rhino (often with the
MatrixGold or JewelCAD plugins) or on standalone JewelCAD. These are
powerful, but require a paid license and, typically, an interactive
desktop session — incompatible with a server-side, automatable pipeline,
and with a product that a user should be able to run without buying
separate CAD software.

## Decision

JewelMind's runtime **must never require Rhino, MatrixGold, JewelCAD, an
interactive FreeCAD desktop instance, or any other paid/interactive CAD
application** to generate, preview, or export geometry. This is codified
as a non-negotiable rule in `CLAUDE.md` and reflected in Product
Principle 8 and the introduction to
[`004-jewelmind-constitution.md`](../00-foundation/004-jewelmind-constitution.md).

## Alternatives considered

- **Scripting Rhino/Grasshopper headlessly via `Rhino.Compute` or a
  similar server product.** Rejected: still requires a Rhino license and
  infrastructure, reintroducing the exact dependency this decision avoids.
- **Requiring users to have MatrixGold/JewelCAD installed and importing/
  exporting through it.** Rejected: makes the MVP unusable without a paid
  license, contradicting the goal of a broadly accessible prototype.
- **CadQuery/OpenCascade headless (the chosen path).** Selected — see
  [ADR-001](ADR-001-cadquery-for-mvp.md).

## Positive consequences

- Anyone can run the full pipeline (`docker compose up --build`, or the
  non-Docker workflow in `docs/development.md`) without purchasing
  anything.
- No licensing compliance burden for the project itself.
- Forces geometry logic to be expressed in portable, testable code
  instead of interactive manual CAD steps.

## Negative consequences

- Cannot directly reuse existing Rhino/Grasshopper jewelry-design scripts
  or plugins that may exist in the wider jewelry-CAD ecosystem.
- STEP/STL are the practical interchange point for professionals who do
  use Rhino/MatrixGold downstream — no native `.3dm` export exists (see
  [ADR-010](ADR-010-step-and-stl-export-strategy.md)).

## Risks

- A future feature request might seem easiest to satisfy by scripting a
  commercial tool. This ADR must be explicitly revisited (new ADR) before
  doing so, not silently bypassed.

## Review trigger

Revisit only if a future scope change makes a paid CAD dependency
genuinely unavoidable — this must go through a new ADR, not a quiet
dependency addition (see LAW enforcement in
[`000-bible-governance.md`](../00-foundation/000-bible-governance.md)).

## Related implementation files

`backend/requirements.txt` (no commercial CAD SDK present),
`backend/Dockerfile` (no interactive application installed).

## Related tests

No direct test can prove a negative; enforced by dependency-list review
and `CLAUDE.md`'s explicit rule.
