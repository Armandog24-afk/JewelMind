/**
 * Pure helpers for Studio v1's small keyboard-shortcut set. See
 * docs/bible/11-studio/273-keyboard-and-input-model.md. Kept
 * deliberately tiny — one action per key, never a chord, never
 * overriding a key a text field needs.
 */

export type ShortcutKey = 'g' | 'f' | '1' | '2' | '3' | '4'

export const SHORTCUT_DESCRIPTIONS: Record<ShortcutKey, string> = {
  g: 'Generate / regenerate the model',
  f: 'Fit camera to the model',
  '1': 'Front camera',
  '2': 'Side camera',
  '3': 'Top camera',
  '4': 'Three-quarter camera',
}

const TEXT_INPUT_TAGS = new Set(['INPUT', 'TEXTAREA', 'SELECT'])

/** True when the keystroke should be ignored because the user is
 * actively typing — a text field, a `contenteditable` region, or any
 * element with a modifier key held (reserved for the browser/OS). */
export function shouldIgnoreShortcut(target: EventTarget | null, modifierHeld: boolean): boolean {
  if (modifierHeld) return true
  if (!(target instanceof HTMLElement)) return false
  if (TEXT_INPUT_TAGS.has(target.tagName)) return true
  // Checks both the live property (the real signal in a real browser,
  // since it accounts for inherited contenteditable regions) and the
  // raw attribute (a jsdom-safe fallback — jsdom does not implement the
  // contenteditable editing-host algorithm, so isContentEditable is
  // always false there even when the attribute is set).
  if (target.isContentEditable) return true
  if (target.getAttribute('contenteditable') === 'true' || target.getAttribute('contenteditable') === '') {
    return true
  }
  return false
}

export function resolveShortcutKey(rawKey: string): ShortcutKey | null {
  const key = rawKey.toLowerCase()
  if (key === 'g' || key === 'f' || key === '1' || key === '2' || key === '3' || key === '4') {
    return key
  }
  return null
}
