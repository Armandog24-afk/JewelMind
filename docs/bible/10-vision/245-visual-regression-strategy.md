---
id: JM-BIBLE-245
title: Visual Regression Strategy
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-244
related_documents:
  - JM-BIBLE-A47
implementation_status: planned
professional_validation: not_required
normative: false
---

# Visual Regression Strategy

## Decision: no pixel-diff screenshot tests added this Sprint

Per this Sprint's own explicit instruction ("Do not add fragile CI screenshots if environment variability makes them unreliable"), no golden-image/pixel-diff test suite was added. This Sprint's own browser-verification session directly demonstrated the relevant risk: the same rendering pipeline behaved differently (canvas sizing, `requestAnimationFrame` throttling) depending on tab visibility in the automated environment used to test it — exactly the kind of environment variability that makes naive pixel-diff CI tests flaky rather than trustworthy. Investing in golden-image testing before that variability is understood and controlled for would produce a test suite that fails for reasons unrelated to real regressions.

## What IS tested programmatically instead

Every piece of Vision's rendering logic that can be expressed as pure state/math is unit-tested: camera pose computation (`camera.test.ts`, 8 tests), material resolution (`materials.test.ts`, 8 tests), capture gating (`capture.test.ts`, 5 tests), filename generation (`filename.test.ts`, 4 tests), and view/visibility state transitions (`useVisionStore.test.ts`, 6 tests) — 31 new tests total, all deterministic and environment-independent. This satisfies the Sprint's own fallback instruction: "At minimum test scene state and render contracts programmatically."

## Baseline cases for a future golden-view suite

If visual regression testing is pursued later (see [`247-vision-gap-analysis.md`](247-vision-gap-analysis.md) `VISION-GAP-006`), these are the representative cases this Sprint's own manual verification already exercised and would form a natural starting baseline:

| Case | Exercised this Sprint? |
|---|---|
| Default six-prong comfort-fit solitaire, yellow gold | Yes — generated and inspected via browser session |
| Flat-band solitaire | Yes — regenerated after switching `band.profile` to `flat`, confirmed no errors |
| Four-prong solitaire | **Not independently exercised this Sprint** — recorded honestly as not verified, not silently assumed to work (see [`SPRINT-8-VALIDATION-REPORT.md`](SPRINT-8-VALIDATION-REPORT.md)) |
| Yellow gold / white gold / rose gold / platinum / silver | Materials verified via unit test (`materials.test.ts`) for all 5; only yellow gold was visually exercised in the live browser session |

## What a future implementation would need

A controlled, fully-visible (non-headless, non-backgrounded) browser context with a fixed viewport size and a fixed, injected `devicePixelRatio`, plus tolerance-based image comparison (never exact pixel equality, for the same reason kernel-derived floats use `pytest.approx` elsewhere in this Bible) — this is a real, nontrivial infrastructure investment, not a quick addition, which is why it remains PLANNED rather than attempted partially this Sprint.
