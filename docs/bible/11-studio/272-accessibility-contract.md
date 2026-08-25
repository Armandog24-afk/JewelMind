---
id: JM-BIBLE-272
title: Accessibility Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-243
related_documents: []
implementation_status: partial
professional_validation: not_required
normative: true
---

# Accessibility Contract

## Improvements made this Sprint, confirmed by inspection

| Area | Before | After |
|---|---|---|
| Focus visibility | `.form-field input:focus { outline: none }` with only a border-color change — no ring for any button, and inputs relied on a subtle 1px color shift alone | A global `:focus-visible` rule (`outline: 2px solid var(--color-gold); outline-offset: 2px`) applies to every button/link/input/select/summary/`[tabindex]` element, visible only for keyboard focus (not mouse clicks), site-wide |
| Numeric field invalid state | No visual indication when a typed value fell outside `min`/`max` | `aria-invalid`, an `aria-describedby`-linked error message, and a red border, added to every `NumericField` |
| Destructive action | `Reset project` had no confirmation | Native `window.confirm()` dialog — accessible by construction |
| Model status | Only a color-coded banner (`.stale-banner`), no header-level status | `ModelStatusBadge`, `role="status"`, `aria-live="polite"`, always a text label plus a detail sentence |

## Already correct before this Sprint, confirmed unchanged

Every form field already had a real `<label htmlFor>` association (no unlabelled input existed); no icon-only button existed anywhere in the codebase (every button, including Vision's camera-preset buttons, carries a visible text label); `ValidationItem`/`ErrorBanner` already used `role="alert"`/`role="listitem"` appropriately.

## Non-color-only statuses

Restating STUDIO-GOV-009: `ModelStatusBadge`'s tone only changes color; the label and detail text are what actually communicate state, confirmed by `modelState.test.ts`'s assertion that every state has a non-empty label and detail.

## No certification claimed

Per this Sprint's explicit instruction, this is a practical, WCAG-oriented improvement pass, not a certified audit — no automated axe/Lighthouse accessibility scan was run this Sprint (no such tooling was available in this session), and contrast ratios were not numerically measured. This is stated plainly rather than implied.

## A real, honest gap noted during testing

`frontend/src/components/ConfigurationPanel.test.tsx`'s "collapsed by default" test could not rely on Testing Library's `queryByLabelText` hidden-detection for the closed `<details>` element, because jsdom does not compute the UA-stylesheet `display: none` rule for non-`summary` children of a closed `<details>` the way real browsers do. The test was adjusted to check the element's `open` property directly. This is a jsdom testing-environment limitation, not evidence of a real accessibility problem — real browsers do correctly hide the collapsed content from assistive technology.
