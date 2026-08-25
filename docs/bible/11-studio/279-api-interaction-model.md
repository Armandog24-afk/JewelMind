---
id: JM-BIBLE-279
title: API Interaction Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-278
related_documents: []
implementation_status: current
professional_validation: not_required
normative: true
---

# API Interaction Model

## Already centralized, confirmed by audit — no rewrite performed

Every backend call in this codebase already goes through `frontend/src/api/client.ts`: `fetchHealth`, `validateDefinitionOnServer`, `generateModel`, `fetchModelMetadata`, `previewUrl`, `exportStep`/`exportStl`/`exportJson`/`exportSpecification` (via the shared `downloadPost()` helper), and `fetchSpecificationText`. This Sprint's own code audit searched for direct, scattered `fetch()` calls outside this file and found none — `TechnicalSpecification.tsx` calls `fetchSpecificationText()` from `client.ts`, not `fetch()` directly. No centralization work was needed; this document records the audit's (clean) result rather than a change.

## Request/error handling, confirmed consistent

Every function in `client.ts` throws the same `ApiError` shape (status, code, message, requestId, details) on a non-2xx response — confirmed by inspection of `request()` and `downloadPost()`, both of which parse the backend's `ErrorEnvelope` identically. Every caller (`useProjectStore.generate()`, `runExport()`, `TechnicalSpecification`) catches this same `ApiError` type.

## No abort/cancel support — a real, unchanged gap

Confirmed: no `AbortController` is used for `generateModel()`, `runExport()`, or `fetchSpecificationText()` — a request in flight cannot be cancelled by the user, and a second click while one is pending is prevented only by disabling the triggering button (`generationStatus === 'generating'`/`exportStatus[kind] === 'exporting'`), not by an actual network-level cancellation. This is the same category of gap `useComponentGeometries.ts` already solves correctly for preview-mesh fetches (it does use `AbortController`, confirmed in Sprint 8's audit) — the asymmetry is real and recorded in [`283-studio-gap-analysis.md`](283-studio-gap-analysis.md), not fixed this Sprint (out of scope: "do not broadly rewrite the API client if existing structure is already good").

## Request state, per call site

`useProjectStore` tracks exactly the request states each call site needs (`generationStatus` for generate, one `exportStatus` entry per artifact kind) — no shared, generic "request state" abstraction exists or was added, since the existing per-purpose fields already avoid the "one `isLoading` boolean" anti-pattern this Sprint's own principles warn against (see [`278-frontend-state-architecture.md`](278-frontend-state-architecture.md)).
