import { beforeEach, describe, expect, it } from 'vitest'
import { createDefaultDefinition } from '@shared/types/jewelry-definition'
import { clearDefinition, loadDefinition, saveDefinition } from './persistence'

const STORAGE_KEY = 'jewelmind:project-definition:v1'

describe('persistence (localStorage safety)', () => {
  beforeEach(() => {
    window.localStorage.clear()
  })

  it('returns null when nothing has been saved', () => {
    expect(loadDefinition()).toBeNull()
  })

  it('round-trips a valid definition', () => {
    const def = createDefaultDefinition()
    def.project.name = 'My Custom Ring'
    def.band.width = 3.1
    saveDefinition(def)
    expect(loadDefinition()).toEqual(def)
  })

  it('clearDefinition removes the saved value', () => {
    saveDefinition(createDefaultDefinition())
    clearDefinition()
    expect(loadDefinition()).toBeNull()
  })

  it('does not crash on corrupted (unparsable) JSON and returns null', () => {
    window.localStorage.setItem(STORAGE_KEY, '{not valid json!!')
    expect(() => loadDefinition()).not.toThrow()
    expect(loadDefinition()).toBeNull()
  })

  it('rejects an empty object', () => {
    window.localStorage.setItem(STORAGE_KEY, '{}')
    expect(loadDefinition()).toBeNull()
  })

  it('rejects a JSON value that is not an object (array, string, number)', () => {
    for (const raw of ['[1,2,3]', '"hello"', '42', 'null', 'true']) {
      window.localStorage.setItem(STORAGE_KEY, raw)
      expect(loadDefinition()).toBeNull()
    }
  })

  it('rejects a definition with a missing section', () => {
    const def = createDefaultDefinition() as unknown as Record<string, unknown>
    delete def['setting']
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(def))
    expect(loadDefinition()).toBeNull()
  })

  it('rejects an obsolete/unsupported schemaVersion', () => {
    const def = createDefaultDefinition()
    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ ...def, schemaVersion: '0.0.1' }),
    )
    expect(loadDefinition()).toBeNull()
  })

  it('rejects a numeric field stored as a string', () => {
    const def = createDefaultDefinition()
    const corrupted = { ...def, band: { ...def.band, width: '2.4' } }
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(corrupted))
    expect(loadDefinition()).toBeNull()
  })

  it('rejects non-finite numeric fields smuggled in via raw text', () => {
    const def = createDefaultDefinition()
    const raw = JSON.stringify(def).replace('"meshTolerance":0.1', '"meshTolerance":Infinity')
    window.localStorage.setItem(STORAGE_KEY, raw)
    expect(loadDefinition()).toBeNull()
  })

  it('rejects an unsupported enum value', () => {
    const def = createDefaultDefinition()
    const corrupted = { ...def, band: { ...def.band, profile: 'square' } }
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(corrupted))
    expect(loadDefinition()).toBeNull()
  })

  it('rejects a non-positive preview tolerance', () => {
    const def = createDefaultDefinition()
    const corrupted = { ...def, preview: { ...def.preview, meshTolerance: 0 } }
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(corrupted))
    expect(loadDefinition()).toBeNull()
  })

  it('saveDefinition does not throw when localStorage.setItem throws', () => {
    const original = window.localStorage.setItem.bind(window.localStorage)
    window.localStorage.setItem = () => {
      throw new DOMException('QuotaExceededError')
    }
    try {
      expect(() => saveDefinition(createDefaultDefinition())).not.toThrow()
    } finally {
      window.localStorage.setItem = original
    }
  })

  it('loadDefinition does not throw when localStorage.getItem throws', () => {
    const original = window.localStorage.getItem.bind(window.localStorage)
    window.localStorage.getItem = () => {
      throw new DOMException('SecurityError')
    }
    try {
      expect(() => loadDefinition()).not.toThrow()
      expect(loadDefinition()).toBeNull()
    } finally {
      window.localStorage.getItem = original
    }
  })
})
