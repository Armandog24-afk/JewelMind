import { describe, expect, it } from 'vitest'
import { resolveShortcutKey, shouldIgnoreShortcut } from './keyboardShortcuts'

describe('shouldIgnoreShortcut', () => {
  it('ignores keystrokes while a modifier key is held', () => {
    expect(shouldIgnoreShortcut(document.createElement('div'), true)).toBe(true)
  })

  it('ignores keystrokes while typing in a text input', () => {
    expect(shouldIgnoreShortcut(document.createElement('input'), false)).toBe(true)
  })

  it('ignores keystrokes while typing in a textarea or select', () => {
    expect(shouldIgnoreShortcut(document.createElement('textarea'), false)).toBe(true)
    expect(shouldIgnoreShortcut(document.createElement('select'), false)).toBe(true)
  })

  it('ignores keystrokes in a contenteditable region', () => {
    const div = document.createElement('div')
    div.setAttribute('contenteditable', 'true')
    document.body.append(div)
    try {
      expect(shouldIgnoreShortcut(div, false)).toBe(true)
    } finally {
      div.remove()
    }
  })

  it('allows the shortcut everywhere else', () => {
    expect(shouldIgnoreShortcut(document.createElement('button'), false)).toBe(false)
    expect(shouldIgnoreShortcut(document.body, false)).toBe(false)
  })
})

describe('resolveShortcutKey', () => {
  it('recognizes the 6 defined shortcut keys, case-insensitively', () => {
    expect(resolveShortcutKey('g')).toBe('g')
    expect(resolveShortcutKey('G')).toBe('g')
    expect(resolveShortcutKey('1')).toBe('1')
  })

  it('returns null for every other key', () => {
    expect(resolveShortcutKey('a')).toBeNull()
    expect(resolveShortcutKey('Enter')).toBeNull()
    expect(resolveShortcutKey('5')).toBeNull()
  })
})
