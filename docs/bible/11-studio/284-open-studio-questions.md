---
id: JM-BIBLE-284
title: Open Studio Questions
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-283
related_documents:
  - JM-BIBLE-STUDIO-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Open Studio Questions

| ID | Question | Impact | Priority | Provisional decision | Target decision sprint |
|---|---|---|---|---|---|
| `STUDIO-OQ-001` | Should advanced parameters be collapsed by default? | Affects first-impression simplicity vs. immediate visibility of all controls | Medium | Yes, as shipped — collapsed by default, one click away | Revisit only if user feedback says otherwise |
| `STUDIO-OQ-002` | Should `innerDiameter` and ring size remain independently editable? | Affects whether a future auto-derivation could replace `JM-RING-003`'s cross-check | Medium | Yes — both remain independent this Sprint; no derivation was added | A future sprint focused on parameter-editing ergonomics |
| `STUDIO-OQ-003` | Should preview tolerances remain user-facing? | Affects whether tessellation quality stays a design-time knob or becomes an internal-only setting | Low-Medium | Yes, kept user-facing (Advanced group) — some users may want faster/coarser previews | Revisit if usage data ever shows nobody touches it |
| `STUDIO-OQ-004` | Should technical metadata live in a drawer or side panel? | Affects viewport clutter vs. discoverability | Low | Stays in the existing `Model info` tab — no drawer added this Sprint | Any future viewport-layout sprint |
| `STUDIO-OQ-005` | Should Outputs become a persistent right panel (not a tab)? | Affects layout real estate and discoverability | Medium | No — stays a tab alongside Validation/Specification/JSON/Model info, to avoid shrinking the viewport | Revisit if usage data shows Outputs is used far more often than the other tabs |
| `STUDIO-OQ-006` | Should Studio support undo/redo before cloud projects? | Affects whether local-only undo/redo is worth building ahead of a bigger project-management feature | Medium | Not yet — see `STUDIO-GAP-005` | A dedicated sprint, likely before cloud projects (undo/redo has value even fully local) |
| `STUDIO-OQ-007` | Should PNG appear alongside manufacturing outputs? | Affects whether the Outputs list should visually separate "manufacturing-relevant" from "presentation-only" artifacts | Low-Medium | Currently listed together, distinguished only by name/purpose text, not a visual grouping | A future Outputs-polish sprint, if user confusion is reported |
| `STUDIO-OQ-008` | Should users choose which warnings are visible? | Affects whether Forge diagnostics ever become filterable/dismissible | Medium | No — restates STUDIO-GOV-010; every diagnostic Forge returns is shown | Not open for revisiting without a product/safety review, given the professional-review context |
| `STUDIO-OQ-009` | Should a generated design be automatically named? | Affects whether `project.name` ever auto-populates from parameters | Low | No — `project.name` remains a free-text field the user sets deliberately | A future naming/UX-polish sprint |
| `STUDIO-OQ-010` | Should Studio later support multiple open projects? | Affects the entire project/session model | High | Not yet — see `STUDIO-GAP-001`/`002` | A dedicated project-workflow sprint |
| `STUDIO-OQ-011` | Should desktop panels become resizable? | Affects layout flexibility vs. implementation robustness against the 3D canvas's resize behavior | Medium | Not yet — see [`265-layout-system.md`](265-layout-system.md) | Only if a robust approach (accounting for Vision's ResizeObserver timing) is designed first |
| `STUDIO-OQ-012` | Which mobile actions should be read-only? | Affects how much of the design-editing surface should be touch-optimized vs. inspection-only | Medium | Not yet decided — this Sprint verified layout stacking but did not restrict any action on narrow screens | A dedicated mobile-experience sprint, informed by real usage data |

## What this document is not

Not a roadmap and not a set of recommendations disguised as questions — each provisional decision reflects exactly what the product does today, so a future decision-maker starts from the true current state.
