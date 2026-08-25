---
id: JM-BIBLE-273
title: Keyboard and Input Model
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-272
related_documents:
  - JM-BIBLE-A50
implementation_status: current
professional_validation: not_required
normative: true
---

# Keyboard and Input Model

## The 6 shortcuts, exactly as shipped

| Key | Action | Guarded by |
|---|---|---|
| `G` | Generate / regenerate the model | Ignored while a blocking validation error exists or a generation is already in flight |
| `F` | Fit camera to the model | — |
| `1` | Front camera | — |
| `2` | Side camera | — |
| `3` | Top camera | — |
| `4` | Three-quarter camera | — |

Implemented in `frontend/src/studio/keyboardShortcuts.ts` (pure key-resolution and ignore-logic, 7 tests) plus a single `window`-level `keydown` listener in `ModelViewport.tsx`, attached once on mount.

## Never interferes with typing

`shouldIgnoreShortcut()` ignores every keystroke when: a modifier key (Cmd/Ctrl/Alt) is held, the event target is an `<input>`/`<textarea>`/`<select>`, or the target is `contenteditable`. Verified live this Sprint: typing the letter `g` into the project-name field produced the literal text "...ringg" with no side effect, while pressing `g` with focus on a button triggered a real regeneration.

## Discoverable, not hidden

Every shortcut-bearing button's `title` attribute states its key (e.g. "Front camera (shortcut: 1)", "Generate the model (shortcut: G, while not typing in a field)") — confirmed present in the real rendered DOM this Sprint. There is no separate, dedicated "keyboard shortcuts" help screen; the tooltip-level discoverability was judged sufficient for a 6-key set, per this Sprint's own "do not overbuild this" instruction.

## Deliberately small

No chorded shortcuts, no shortcut for Reset (a destructive action correctly requires a deliberate click + confirmation, not a single keystroke), and no shortcut for export actions (each export is a meaningful, potentially slow network action better triggered deliberately). This set covers exactly the two highest-frequency actions during iterative design (generate, inspect from a different angle).
