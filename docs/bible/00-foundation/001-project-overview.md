---
id: JM-BIBLE-001
title: Project Overview
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on: []
related_documents:
  - JM-BIBLE-005
  - JM-BIBLE-006
  - JM-BIBLE-002
implementation_status: current
---

# Project Overview

## What JewelMind is today

JewelMind is a **parametric jewelry CAD prototype**. In its current form
it supports exactly one product type — a **simplified solitaire ring** —
configured through a web form and turned into real, deterministic 3D
geometry.

Concretely, today, JewelMind:

- accepts a structured set of parameters describing a solitaire ring
  (ring size, band width/thickness/profile, stone diameter/depth, prong
  count/diameter/height, basket height, metal, manufacturing method —
  the full canonical shape is `shared/types/jewelry-definition.ts` /
  `backend/jewelmind/domain/schema.py`, documented in `docs/domain-model.md`);
- validates that set of parameters against sixteen deterministic business
  rules, both instantly in the browser and authoritatively on the backend
  (`docs/validation-rules.md`);
- generates real, deterministic 3D solid geometry for that ring using
  **CadQuery**, a Python library built on the **OpenCascade** B-Rep
  kernel — the same category of geometry kernel used by professional CAD
  systems (`backend/jewelmind/geometry/`);
- renders a browser preview **derived directly from that backend
  geometry** (tessellated to STL meshes and loaded into a React Three
  Fiber viewport) — the preview is never a separate, disconnected 3D
  model (`frontend/src/hooks/useComponentGeometries.ts`);
- exports the generated geometry as a real STEP file and a real STL file,
  the canonical parameters as JSON, and a human-readable Markdown
  technical specification (`backend/jewelmind/exporters/`);
- runs this whole pipeline with **no dependency on Rhino, MatrixGold,
  JewelCAD, an interactive FreeCAD session, any other commercial CAD
  application, or any LLM at runtime** — geometry is produced entirely by
  deterministic CadQuery code.

## What JewelMind is not (today)

JewelMind today is **not**:

- a multi-stone or pavé-setting configurator;
- a system that supports necklaces, earrings, bracelets, or any jewelry
  category other than a ring;
- a system that accepts natural-language or image input to produce
  geometry;
- a manufacturing-readiness certifier — every export is explicitly labeled
  preliminary and requiring professional review (`shared/disclaimer.ts`,
  `backend/jewelmind/domain/disclaimer.py`);
- a multi-user, authenticated, or persisted-to-a-database system — state
  lives in the browser's `localStorage` and an in-memory server-side cache
  that is cleared on backend restart (see
  [`02-architecture/025-security-and-data-handling.md`](../02-architecture/025-security-and-data-handling.md)).

See [`006-scope-and-boundaries.md`](006-scope-and-boundaries.md) for the
complete, itemized scope boundary, and
[`005-current-product-status.md`](005-current-product-status.md) for a
capability-by-capability implementation matrix backed by file paths and
tests.

## How it is built

- **Frontend:** React + TypeScript (strict mode) + Vite + React Three
  Fiber, one Zustand store (`frontend/`).
- **Backend:** Python 3.11 + FastAPI + Pydantic v2 + CadQuery (`backend/`).
- **Shared:** a hand-maintained TypeScript mirror of the backend's
  canonical schema and validation rules, for instant frontend feedback —
  the backend remains authoritative (`shared/`).
- **One monorepo, one frontend, one backend** — no microservices. See
  [`02-architecture/020-architecture-overview.md`](../02-architecture/020-architecture-overview.md)
  and [ADR-008](../03-decisions/ADR-008-monorepo-architecture.md).

## Long-term vision (explicitly not current functionality)

JewelMind's long-term vision is a parametric jewelry design platform
capable of transforming design intent into editable, validated, and
exportable jewelry definitions and CAD models — across more jewelry
types, more setting styles, and eventually assisted by natural-language
or visual intent capture in front of the same deterministic validation and
geometry core. **This is vision, not current functionality.** See
[`002-vision-and-mission.md`](002-vision-and-mission.md) for the full,
explicitly-labeled statement, and do not read any "current" section of
this Bible as implying more than what is listed in
[`005-current-product-status.md`](005-current-product-status.md).
