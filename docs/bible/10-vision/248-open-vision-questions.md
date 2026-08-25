---
id: JM-BIBLE-248
title: Open Vision Questions
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-247
related_documents:
  - JM-BIBLE-VISION-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Open Vision Questions

| ID | Question | Impact | Priority | Provisional decision | Target decision sprint |
|---|---|---|---|---|---|
| `VISION-OQ-001` | Should Vision eventually consume GLB rather than STL components? | Affects payload size, material fidelity, and parsing complexity | Medium | Not yet — STL remains real and current; GLB stays `VISION-GAP-001` | A future performance-focused sprint |
| `VISION-OQ-002` | Should presentation images be generated client-side or server-side long term? | Affects image quality ceiling vs. infrastructure cost | Medium | Client-side, as shipped this Sprint — sufficient for v1's needs | Revisit only if customers request marketing-grade renders |
| `VISION-OQ-003` | Should rendering settings become part of project state (persisted)? | Affects whether `viewMode`/camera/visibility survive a page reload | Low | No — `useVisionStore` is deliberately session-only today, mirroring how `componentVisibility` was already session-only before this Sprint | Any future "remember my view preferences" feature request |
| `VISION-OQ-004` | Should presentation state affect compilation identity (`definitionHash`)? | Would conflate design intent with display preference | High if answered wrong | **No** — restates VISION-GOV-014 as a hard boundary, not merely a preference | Not open for revisiting without an ADR |
| `VISION-OQ-005` | Should presentation images be stored as project artifacts? | Would require a persistence layer for generated images | Medium | Not today — capture is a one-shot client-side download, no server storage | A future project-workflow sprint (Studio v1 territory) |
| `VISION-OQ-006` | Should users be allowed to choose backgrounds? | Affects UI surface area vs. presentation flexibility | Low-Medium | Not yet — one background per mode; see `VISION-GAP-005` | Any future presentation-polish sprint |
| `VISION-OQ-007` | Should the technical viewer expose measurements? | Direct engineering value | Medium | Not yet — see `VISION-GAP-010` | A future technical-view-focused sprint |
| `VISION-OQ-008` | Should users be able to select individual prongs? | Would need per-solid identity within the `prongs` compound, which today is a single merged component | Medium | Not yet — `prongs` is currently one compound solid in the preview manifest, not N separately-addressable prongs | Would require an Atlas-side change first (component granularity), not just a Vision change |
| `VISION-OQ-009` | Should Vision support exploded view? | Presentation/engineering value | Low-Medium | Not yet — see `VISION-GAP-008` | Not before Studio v1 |
| `VISION-OQ-010` | Should a future path tracer be integrated? | Would raise Presentation mode toward true photorealism | Low today | No — real-time WebGL rasterization remains the approach; see `VISION-GAP-002` for the server-side alternative | Only if a dedicated rendering-quality sprint is chartered |
| `VISION-OQ-011` | Should Vision support transparent PNG? | Useful for compositing captured images elsewhere | Low-Medium | Not yet — see `VISION-GAP-013`; technically low-effort | Any near-term Vision-refinement sprint |
| `VISION-OQ-012` | Should turntable video become an artifact? | Presentation appeal | Low | Not yet — see `VISION-GAP-007`; would also raise new questions about video format/storage | Not scheduled |

## What this document is not

Not a roadmap and not a set of recommendations disguised as questions — each provisional decision reflects exactly what the code does today, so a future decision-maker starts from the true current state.
