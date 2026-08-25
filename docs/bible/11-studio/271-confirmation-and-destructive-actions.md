---
id: JM-BIBLE-271
title: Confirmation and Destructive Actions
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-250
related_documents: []
implementation_status: current
professional_validation: not_required
normative: true
---

# Confirmation and Destructive Actions

## The one materially destructive action in this application

`Reset project` (`ProjectActions.tsx`) discards the current `JewelryDefinition`, clears its `localStorage` entry, and drops any in-memory `generatedModel`/`lastSuccessfulPreview` — with no undo. This is the only action in the entire workspace that meets the bar for a confirmation, per this Sprint's own instruction ("use confirmation only when action is materially destructive").

## Real implementation

`window.confirm('Reset the current design? This discards your parameters and any generated model, and cannot be undone.')` — a native browser dialog, chosen deliberately over a custom modal component for this single use case: it needed no new component, no new CSS, no focus-trap implementation, and is inherently keyboard- and screen-reader-accessible by virtue of being a real OS/browser dialog. `resetProject()` (the store action) is only called if the user confirms.

## Nothing else was made to prompt for confirmation

Editing a parameter, switching view mode, toggling component visibility, and every export/capture action remain confirmation-free — none of them destroys anything the user cannot immediately reverse (an edit can be typed back; the last-good model survives a failed regeneration by design; exports never mutate state). Adding confirmation dialogs to any of these would have violated this Sprint's explicit "do not add unnecessary confirmation dialogs" instruction for no safety benefit.

## Real test coverage

`ProjectActions.test.tsx` (2 new tests) confirms: clicking Reset while `window.confirm` is mocked to return `false` leaves the current definition untouched; clicking Reset while it returns `true` actually resets it.
