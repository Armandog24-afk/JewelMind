---
id: JM-BIBLE-247
title: Vision Gap Analysis
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-246
related_documents:
  - JM-BIBLE-248
implementation_status: current
professional_validation: not_required
normative: false
---

# Vision Gap Analysis

No solution is proposed beyond what's needed to name each gap responsibly — per this Sprint's own instruction not to implement all of these now.

| Gap ID | Current state | Business value | Complexity | Priority | Target sprint |
|---|---|---|---|---|---|
| `VISION-GAP-001` GLB preview transport | STL only, confirmed real and current — see [`224-preview-mesh-contract.md`](224-preview-mesh-contract.md) | Medium — smaller payloads, native material/normal support, no custom STL parse | Medium | Low | A future performance-focused sprint |
| `VISION-GAP-002` Server-side high-quality rendering | Client-side WebGL only | Medium — would enable true photorealistic marketing images | High | Low | A future "Studio"-adjacent sprint, only if customer demand appears |
| `VISION-GAP-003` Physically richer gemstone shaders | `MeshPhysicalMaterial` transmission preset only, no faceting/dispersion | Medium — more convincing stone appearance | High (custom shader work, explicitly discouraged this Sprint) | Low | Not before a dedicated rendering-quality sprint |
| `VISION-GAP-004` Second/higher-res/square capture size | Fixed `1920×1080` only | Low-Medium — product-image flexibility | Low (function is already resolution-agnostic) | Medium | Any near-term Vision-refinement sprint |
| `VISION-GAP-005` HDRI studio presets | One procedural `RoomEnvironment` only | Low-Medium — visual variety | Low-Medium (must stay CDN-free per VISION-GOV-010, so any HDRI would need to ship as a bundled asset) | Low | A future presentation-polish sprint |
| `VISION-GAP-006` Visual regression / golden-view testing | Not implemented — see [`245-visual-regression-strategy.md`](245-visual-regression-strategy.md) | Medium — catches unintended visual drift | High (needs a controlled, non-backgrounded browser environment) | Medium | A future test-infrastructure sprint |
| `VISION-GAP-007` Turntable animation | Not implemented | Low-Medium — presentation appeal | Medium | Low | A future presentation-polish sprint |
| `VISION-GAP-008` Exploded technical views | Not implemented | Medium for engineering review | Medium-High (needs a per-component offset animation) | Low | Not before Studio v1 |
| `VISION-GAP-009` Section/cutaway views | Not implemented | Medium for engineering review | High (needs a clipping-plane render pass) | Low | Not before Studio v1 |
| `VISION-GAP-010` Measurement overlays | Not implemented | Medium — direct technical value | Medium | Medium | A future technical-view-focused sprint |
| `VISION-GAP-011` Annotations | Not implemented | Low-Medium | Medium | Low | Not scheduled |
| `VISION-GAP-012` Screenshots with branding | Not implemented — capture is a plain PNG | Low | Low | Low | Not scheduled |
| `VISION-GAP-013` Transparent-background PNG | Not implemented — background is always opaque | Medium — useful for compositing into other materials | Low (renderer already supports `alpha: true`; not enabled this Sprint) | Medium | Any near-term Vision-refinement sprint |
| `VISION-GAP-014` Batch render presets / render queue | Not implemented | Low today (single-model workflow) | Medium | Low | Not before multi-project workflows exist |
| `VISION-GAP-015` AR preview | Not implemented | Unknown — no user research exists | High (needs WebXR or a model-viewer-style AR pipeline) | Low | Not scheduled |
| `VISION-GAP-016` Mobile rendering optimization | Not independently profiled on a mobile device this Sprint | Medium if mobile usage is real | Medium | Medium | Any future sprint once mobile usage data exists |
| `VISION-GAP-017` Visual comparison between versions | Not implemented — no version history concept exists yet | Medium | High (depends on a project-history feature that doesn't exist) | Low | Not before Studio v1's project workflow |
| `VISION-GAP-018` `VISION_*` diagnostic codes have no real implementation | 0 of 9 conceptual codes exist as distinct, named errors — see [`241-rendering-errors-and-diagnostics.md`](241-rendering-errors-and-diagnostics.md) | Low-Medium — better debuggability | Low | Low | Any future hardening sprint |
| `VISION-GAP-019` GPU resource cleanup for `Environment`/`ContactShadows` not independently profiled | Relies on drei's own disposal guarantees, unverified with a GPU memory profiler this Sprint | Low (no observed leak) | Low | Low | Any future performance-audit sprint |

## Summary

19 gaps identified, all software/tooling questions — **none requires jewelry expertise**, consistent with Vision's role as a rendering layer. The highest-value near-term items are `VISION-GAP-004` (second capture size), `VISION-GAP-013` (transparent PNG), and `VISION-GAP-010` (measurement overlays), because each is low-to-medium complexity with direct, immediate user value and does not depend on any other unbuilt feature.
