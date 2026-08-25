---
id: JM-BIBLE-020
title: Architecture Overview
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-007
related_documents:
  - JM-BIBLE-021
  - JM-BIBLE-022
  - JM-BIBLE-ADR-008
  - JM-BIBLE-121
  - JM-BIBLE-161
implementation_status: current
---

# Architecture Overview

This document summarizes the architecture at a level above
`docs/architecture.md`, which remains the authoritative, detailed
reference — see that file for the full request-flow walkthrough and
directory-by-directory breakdown.

## Shape: one monorepo, one frontend, one backend

```
jewelmind/
  frontend/   React + TypeScript (strict) + Vite + React Three Fiber
  backend/    Python 3.11 + FastAPI + Pydantic v2 + CadQuery
  shared/     TypeScript-only domain types & validation mirror
  docs/       Technical reference docs + this Bible
  examples/   Sample JewelryDefinition JSON files + a headless generator script
  scripts/    Dev convenience scripts
```

No microservices, no message queue, no separate database service. See
[ADR-008](../03-decisions/ADR-008-monorepo-architecture.md) for why.

## Layering

The backend is organized in strict layers, each with one responsibility:

```
api/        <- HTTP only: routing, request/response schemas, error mapping
services/   <- orchestration: validate -> generate -> cache -> export
validation/ <- business rules, no CadQuery, no HTTP
geometry/   <- CadQuery geometry construction, no HTTP, no business rules
preview/    <- mesh tessellation for the browser
exporters/  <- file format writers (STEP, STL, JSON, specification)
domain/     <- the canonical schema itself
utils/      <- hashing, logging — no domain knowledge
```

`domain/` and `validation/` have zero dependency on FastAPI or CadQuery —
they are pure Python business logic, testable in isolation. `geometry/`
has zero dependency on FastAPI or HTTP concerns. This separation is what
[`022-domain-boundaries.md`](022-domain-boundaries.md) exists to enforce
and document.

## Conversation Engine (interaction-state layer)

As of Sprint 12, `backend/jewelmind/conversation/` and
`frontend/src/components/ConversationPanel.tsx` add an interaction-state
layer sitting above Designer and Design Intent, with zero authority over
either: a sequence of natural-language turns is classified
deterministically (`classify_action()`) into one of 13 canonical
`ConversationActionType` values and orchestrated around the existing
`DesignerService.interpret()` call — Conversation adds no new technical
extraction, no new JDL proposal construction, and no direct `cadquery`
import anywhere in the package. `ConversationPanel` is now the
natural-language surface actually mounted in `App.tsx`, superseding
`DesignerPanel` there (`DesignerPanel.tsx` itself remains in the codebase
and stays tested standalone). Like Designer, the backend is stateless per
request: `ConversationEngine` never persists a `ConversationSession`
server-side, and accepting a proposal only confirms — via real
content-hash staleness comparison — that it is safe for the caller to
apply through the same `applyDesignerProposal()`/`applyIntent()` paths
already in use since Sprint 10. This layer is formalized as
**"Conversation Engine"** in Sprint 12 — see
[`14-conversation/README.md`](../14-conversation/README.md).

## Designer (natural-language input layer)

As of Sprint 10, `backend/jewelmind/designer/` and
`frontend/src/components/DesignerPanel.tsx` add a natural-language input
layer sitting upstream of every other layer in this diagram, with zero
authority over any of them: a user's Italian- or English-language
request is turned into a structured `DesignerProposal` (candidate JDL
fields, unsupported-feature/ambiguity/clarification diagnostics, a
diff), but that candidate is only ever a proposal — it still passes
through the exact same `JewelryDefinition.model_validate()` and
`validate_definition()` (Forge) calls as any manually-edited definition,
and only an explicit user action (`useProjectStore.applyDesignerProposal()`)
can write it into `currentDefinition`. Designer never talks to Atlas,
Alchemist, or Foundry directly, and never generates geometry itself.
This layer is formalized as **"Designer"** in Sprint 10 — see
[`12-designer/README.md`](../12-designer/README.md).

## Design Intent (aesthetic semantic layer)

As of Sprint 11, `backend/jewelmind/design_intent/` sits between
Designer and JDL, with zero authority over either: it separates the
*subjective* remainder of a natural-language request (e.g. "delicate",
"minimal") from the *technical* fields Designer already resolves,
structures it into a `DesignIntent` (statements, relations, conflicts,
unresolved descriptors), and passes it back on `DesignerProposal.designIntent`
for review in the Studio UI's "Design intent" section — but it never
writes to a JDL dotted path, never touches `candidateJDL`, and never
influences the same JDL-validation/Forge-evaluation gate Designer's
technical fields pass through. Design Intent never talks to Atlas,
Alchemist, or Foundry directly, and registers zero automatic
subjective-to-numeric mappings in v1 by design. This layer is
formalized as **"Design Intent"** in Sprint 11 — see
[`13-design-intent/README.md`](../13-design-intent/README.md).

## CadQuery / OpenCascade as the geometry core

All 3D geometry is constructed through CadQuery
(`backend/jewelmind/geometry/`), which drives the OpenCascade B-Rep
kernel. This is a deliberate choice over a mesh-only or procedural-only
approach — see [ADR-001](../03-decisions/ADR-001-cadquery-for-mvp.md).
**This layer is formalized as "Atlas"** in Sprint 5 —
[`07-atlas/README.md`](../07-atlas/README.md) — the deterministic
geometry layer that owns primitives, coordinate conventions, component
contracts, and geometric inspection, while jewelry-domain thresholds
remain owned exclusively by Forge ([`06-forge/README.md`](../06-forge/README.md)).

## Preview pipeline

The backend tessellates each named solid to its own binary STL file
(`preview/mesh.py`) rather than packaging everything into one GLB — see
[ADR-007](../03-decisions/ADR-007-backend-generated-preview.md) and
`docs/known-limitations.md` for the reasoning. As of Sprint 8, each
component's manifest entry also carries explicit `geometryRole`/
`productionRole`/`meshSource`/`generationStatus` fields, so the frontend
never has to infer a component's material category from its name
string. The frontend fetches and parses these directly
(`frontend/src/hooks/useComponentGeometries.ts`), never rendering
anything not derived from real backend geometry (LAW-002). This layer
is formalized as **"Vision"** in Sprint 8 — see
[`10-vision/README.md`](../10-vision/README.md) — which adds a
Technical/Presentation view split, camera presets, a centralized
material system, and client-side PNG capture, all consuming this exact
same preview geometry.

## Export pipeline

STEP, STL, JSON, and Markdown-specification exporters
(`backend/jewelmind/exporters/`) each take the already-generated
`GeneratedModel` and definition, and write a real file. Export requests
are keyed by `modelId` (not by a raw definition), so an export always
corresponds to an already-validated, already-generated model — see
[`023-data-flow.md`](023-data-flow.md). This layer is formalized as
**"Foundry"** in Sprint 7 — see [`09-foundry/README.md`](../09-foundry/README.md).
STEP and STL share a single component-selection function
(`exporters/selection.py::select_export_shapes()`, extracted in Sprint 7
from previously duplicated logic); every STEP/STL export is also
checksummed (SHA-256) and validated non-empty before being returned.

## Validation pipeline

Two engines run the same sixteen rules: `backend/jewelmind/validation/engine.py`
(authoritative) and `shared/validation/engine.ts` (frontend mirror, for
instant feedback only). The backend always re-validates before generation
and export regardless of what the frontend believes — see Product
Principle 6.

## Compilation orchestration

`ModelService.generate()` (`backend/jewelmind/services/model_service.py`)
is the closest current analogue to what Sprint 6 formalizes as
**"Alchemist"** — the compilation orchestration layer that sequences
Forge validation, Atlas geometry construction, and preview generation.
See [`08-alchemist/README.md`](../08-alchemist/README.md) for the full
specification, including the one concrete architectural gap it
identifies: preview generation is currently coupled to core geometry
generation inside this same function, while STEP/STL/JSON/specification
export is correctly decoupled into separate, later calls.

## State management

- **Frontend:** one Zustand store (`frontend/src/store/useProjectStore.ts`)
  holds `currentDefinition`, `validationResults`, `generatedModel`,
  `generationStatus`, `exportStatus`, `backendStatus`,
  `lastSuccessfulPreview`, and `isStale`. As of Sprint 8, a second,
  deliberately separate Zustand store
  (`frontend/src/store/useVisionStore.ts`) holds Vision-only
  presentation state (`viewMode`, `componentVisibility`,
  `selectedComponent`, `showGrid`, `showAxes`) — it has zero import of
  `useProjectStore` and never calls `generate()`, so a view/camera/
  material change can never trigger geometry regeneration; see
  [`10-vision/221-vision-architecture-overview.md`](../10-vision/221-vision-architecture-overview.md).
  As of Sprint 9, `useVisionStore` also persists `viewMode` (only) across
  reloads, and gained `requestCapture()`/`captureRequestToken` so
  Studio's consolidated Outputs panel can trigger a Presentation-mode
  image capture without holding a direct reference into the viewport
  component.
- **Frontend, product-workspace logic:** `frontend/src/studio/` (new,
  Sprint 9) holds pure, store-independent functions —
  `computeModelState()` (the 7-value model-lifecycle status),
  `computeOutputEligibility()` (the 5-value per-artifact export
  eligibility), and `keyboardShortcuts.ts` (the small Generate/Fit/
  camera-preset shortcut set) — consumed by, but never owning, the two
  stores above. See
  [`11-studio/278-frontend-state-architecture.md`](../11-studio/278-frontend-state-architecture.md).
- **Local persistence:** `localStorage`, one project slot, validated on
  load (`frontend/src/store/persistence.ts`).
- **Server-side model cache:** an in-memory, process-lifetime cache of
  generated models keyed by definition hash, capped at 20 entries with
  LRU eviction (`backend/jewelmind/services/model_service.py`). This is
  not a database — see
  [`025-security-and-data-handling.md`](025-security-and-data-handling.md).

## Runtime and deployment

See [`024-runtime-and-deployment.md`](024-runtime-and-deployment.md) for
local non-Docker development, Docker Compose, ports, and CI.
