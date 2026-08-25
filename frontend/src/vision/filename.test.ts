import { describe, expect, it } from 'vitest'
import { buildCaptureFilename, sanitizeForFilename } from './filename'

describe('sanitizeForFilename', () => {
  it('collapses unsafe characters to underscores', () => {
    expect(sanitizeForFilename('My Ring #1')).toBe('My_Ring_1')
  })

  it('falls back to the default when nothing usable remains', () => {
    expect(sanitizeForFilename('   ')).toBe('jewelmind-render')
    expect(sanitizeForFilename('...')).toBe('jewelmind-render')
  })

  it('strips path-traversal-like leading dots/dashes', () => {
    expect(sanitizeForFilename('../../etc/passwd').startsWith('.')).toBe(false)
  })

  it('caps length at 120 characters', () => {
    expect(sanitizeForFilename('a'.repeat(500)).length).toBe(120)
  })
})

describe('buildCaptureFilename', () => {
  it('embeds the sanitized project name, view mode, and an ISO-derived timestamp', () => {
    const name = buildCaptureFilename('My Ring', 'presentation', Date.UTC(2026, 0, 1, 12, 0, 0))
    expect(name).toMatch(/^jewelmind-My_Ring-presentation-2026-01-01T12-00-00-000Z\.png$/)
  })

  it('never leaks a raw model ID or internal identifier into the filename', () => {
    const name = buildCaptureFilename('My Ring', 'technical', 0)
    expect(name).not.toMatch(/[0-9a-f]{16,}/)
  })
})
