---
id: JM-BIBLE-234
title: Background and Environment Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-228
related_documents:
  - JM-BIBLE-230
implementation_status: current
professional_validation: not_required
normative: true
---

# Background and Environment Model

## Backgrounds

| Mode | Color | Rationale |
|---|---|---|
| Technical | `#15171a` | Matches the application's own dark theme (`--color-bg` in `theme.css`) — the viewport reads as part of the app, not a separate "photo studio" |
| Presentation | `#dedad5` | A light neutral warm gray, distinct from the app's dark chrome — evokes a simple studio backdrop without any pattern, gradient, or texture |

Both are flat `<color attach="background">` values — no gradient, skybox, or image.

## Environment (Presentation mode only): procedural, never remote

`three-stdlib`'s `RoomEnvironment()` — a small, self-contained Three.js scene (a handful of colored planes forming a simple room) — is passed as `children` to drei's `<Environment>` component, which renders it into an offscreen cubemap and converts it to a PMREM (pre-filtered mipmapped radiance environment map) for use as `scene.environment`. This is drei's "portal" mode, distinct from its `preset`/`files` modes, and issues **zero network requests** — confirmed by inspecting `EnvironmentProps` (a `scene`/children input never touches the `files`/`preset` code path that fetches an HDRI).

## Why RoomEnvironment specifically

It is bundled with `three-stdlib` (already an indirect dependency of `@react-three/drei`, now declared as a direct dependency of this project — see [`246-current-viewer-code-mapping.md`](246-current-viewer-code-mapping.md)), requires no asset file, and is the same technique `model-viewer` (Google's web component for 3D model display) uses for its own default environment — a well-established, low-risk choice for exactly this use case.

## No customizable scenes yet

Only one background per view mode exists today; user-selectable backgrounds are explicitly out of this Sprint's scope and recorded as PLANNED in [`247-vision-gap-analysis.md`](247-vision-gap-analysis.md)/[`248-open-vision-questions.md`](248-open-vision-questions.md).

## Nothing external required

No HDRI file, no paid asset pack, no CDN — restating VISION-GOV-010 concretely: `npm install` alone is sufficient for the environment to work, since `RoomEnvironment` and the PMREM pipeline are pure Three.js/three-stdlib code shipped in the already-declared dependency tree.
