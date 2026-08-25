---
id: JM-BIBLE-243
title: Accessibility and Input Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-220
related_documents: []
implementation_status: partial
professional_validation: not_required
normative: true
---

# Accessibility and Input Model

## Input support

| Input | Support |
|---|---|
| Mouse | `OrbitControls` (orbit, zoom via wheel), all buttons real HTML `<button>` elements |
| Trackpad | Same `OrbitControls` — pinch-to-zoom and two-finger pan work through the browser's own wheel/gesture event translation, not custom-handled |
| Touch | `OrbitControls`'s built-in touch support (one-finger orbit, two-finger pinch/pan) — not independently tested on a physical touch device this Sprint (no such device was available in this session), but not disabled or overridden either |
| Keyboard | Every Vision control (`ViewModeSwitch`, `ViewportToolbar`, `ComponentVisibilityPanel`, `PresentationPanel`) is a real `<button>`/`<input type="checkbox">` element, natively focusable and activatable via keyboard (Tab + Enter/Space) — no custom `<div onClick>` control was introduced |

## Labels and roles

`ViewModeSwitch` uses `role="tablist"`/`role="tab"`/`aria-selected`, matching the existing `RightPanelTabs` pattern already in this codebase. `ViewportToolbar` uses `role="toolbar"` with a descriptive `aria-label`. Every camera-preset and toggle button has a `title` attribute (browser tooltip) in addition to its visible text label — no icon-only, unlabeled button was introduced this Sprint.

## No full accessibility certification claimed

Per this Sprint's own explicit scope, this is not a WCAG conformance audit — color-contrast ratios were not independently measured, and the 3D canvas itself (like any WebGL canvas) has no meaningful screen-reader-accessible representation of the rendered geometry. This is a known, industry-wide limitation of interactive 3D content, not something Vision v1 claims to solve.

## Contrast

All new UI elements (`ViewModeSwitch`, `PresentationPanel`, the visibility panel's quick-action buttons) reuse the existing `theme.css` custom properties (`--color-text-muted`, `--color-gold-strong`, `--color-border`) rather than introducing new colors — inheriting whatever contrast characteristics the pre-existing theme already has, rather than introducing an untested new palette.
