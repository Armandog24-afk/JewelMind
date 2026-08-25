import { describe, expect, it } from 'vitest'
import { computeOutputEligibility } from './outputEligibility'

const BASE = { hasModel: true, isStale: false, hasBlockingValidationErrors: false, phase: 'idle' } as const

describe('computeOutputEligibility', () => {
  it('is UNAVAILABLE before any model exists', () => {
    expect(computeOutputEligibility({ ...BASE, hasModel: false })).toBe('UNAVAILABLE')
  })

  it('is AVAILABLE for a current, valid, idle model', () => {
    expect(computeOutputEligibility(BASE)).toBe('AVAILABLE')
  })

  it('is STALE_BLOCKED when the model is stale, even if a model exists', () => {
    expect(computeOutputEligibility({ ...BASE, isStale: true })).toBe('STALE_BLOCKED')
  })

  it('is STALE_BLOCKED when blocking validation errors exist', () => {
    expect(computeOutputEligibility({ ...BASE, hasBlockingValidationErrors: true })).toBe('STALE_BLOCKED')
  })

  it('is EXPORTING while the export is in flight, regardless of other flags', () => {
    expect(computeOutputEligibility({ ...BASE, phase: 'exporting', isStale: true })).toBe('EXPORTING')
  })

  it('is FAILED after a clean (non-stale) failed attempt', () => {
    expect(computeOutputEligibility({ ...BASE, phase: 'error' })).toBe('FAILED')
  })

  it('prefers STALE_BLOCKED over FAILED once the design changes again after a failure', () => {
    expect(computeOutputEligibility({ ...BASE, phase: 'error', isStale: true })).toBe('STALE_BLOCKED')
  })

  it('prefers UNAVAILABLE over every other reason when there is no model at all', () => {
    expect(computeOutputEligibility({ ...BASE, hasModel: false, isStale: true, phase: 'error' })).toBe(
      'UNAVAILABLE',
    )
  })
})
