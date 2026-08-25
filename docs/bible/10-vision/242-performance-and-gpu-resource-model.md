---
id: JM-BIBLE-242
title: Performance and GPU Resource Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-220
related_documents:
  - JM-BIBLE-A47
implementation_status: partial
professional_validation: not_required
normative: true
---

# Performance and GPU Resource Model

## Geometry disposal — pre-existing, re-confirmed unchanged

`frontend/src/hooks/useComponentGeometries.ts` already disposed every `BufferGeometry` correctly before this Sprint (once replaced, and on unmount) — this Sprint changed nothing here, and the pre-existing test suite (`useComponentGeometries.test.ts`, 7 tests, all still passing) continues to cover it, including the "disposes the previous geometry once a new successful set replaces it" and "disposes all held geometries on unmount" cases.

## Material disposal — relies on React Three Fiber's own guarantee

Every `<meshPhysicalMaterial>` in `ComponentMesh.tsx` is created declaratively via JSX, never imperatively cached outside the R3F tree. React Three Fiber's documented behavior is to call `.dispose()` on any Three.js object it created via JSX once that JSX node unmounts — this is a library-level guarantee this Sprint relies on rather than re-implements. A direct consequence: toggling a component's visibility off unmounts its `ComponentMesh` (and disposes its material), and toggling it back on remounts a fresh one — a minor, accepted inefficiency (recreating a small material object is cheap) rather than a leak.

## Environment/PMREM and ContactShadows disposal

Both are `@react-three/drei` components; their internal render-target/PMREM cleanup on unmount (e.g. switching from Presentation back to Technical mode) is the library's responsibility, not re-implemented here. This Sprint did not independently verify this with a browser GPU-memory profiler (no such tooling was available in this session's environment) — recorded honestly as a real, if low-priority, verification gap in [`247-vision-gap-analysis.md`](247-vision-gap-analysis.md), not silently assumed.

## No arbitrary FPS guarantee

Restating [`09-foundry/215-foundry-performance-model.md`](../09-foundry/215-foundry-performance-model.md)'s approach at the rendering layer: no numeric frame-rate target is asserted. `frameloop` was left at React Three Fiber's default (`'always'`, a continuous render loop), not switched to on-demand rendering — a real, deliberate choice for simplicity in this Sprint, with on-demand rendering recorded as a future optimization if performance profiling ever motivates it.

## What was, and was not, measured

This Sprint did not instrument or measure mesh-load time, first-visual-frame time, view-mode-switch time, or capture duration with a profiler — the session's browser environment could not visually composite the page (see [`SPRINT-8-VALIDATION-REPORT.md`](SPRINT-8-VALIDATION-REPORT.md) for why), which also made frame-timing measurement unreliable to report honestly. No fabricated numbers are given here.

## A real, environment-specific finding worth recording

During this Sprint's browser verification, the preview browser tab's `document.visibilityState` was `'hidden'` (the host application's Browser pane was not visually displayed), which both paused/throttled `requestAnimationFrame`-driven rendering and delayed React Three Fiber's `ResizeObserver`-based canvas sizing until a synthetic `window` `resize` event was dispatched. This is standard browser behavior for backgrounded tabs, not a JewelMind code defect — real users, whose browser tab is visible by definition, do not experience this. It is recorded here because it directly explains why this Sprint's own browser-based verification could not capture pixel screenshots, and to prevent a future engineer from mistaking this environment artifact for an application bug.
