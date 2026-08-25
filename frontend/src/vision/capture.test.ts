import { describe, expect, it } from 'vitest'
import { CAPTURE_BLOCKED_MESSAGES, captureBlockedReason } from './capture'

describe('captureBlockedReason', () => {
  it('blocks capture when no model has been generated yet', () => {
    expect(captureBlockedReason(false, false)).toBe('no_model')
  })

  it('blocks capture when the model is stale, even if one exists', () => {
    expect(captureBlockedReason(true, true)).toBe('stale')
  })

  it('allows capture only when a model exists and is not stale', () => {
    expect(captureBlockedReason(true, false)).toBeNull()
  })

  it('prioritizes "no_model" when both conditions are true (nothing to regenerate)', () => {
    expect(captureBlockedReason(false, true)).toBe('no_model')
  })

  it('has a human-readable message for every non-null reason', () => {
    expect(CAPTURE_BLOCKED_MESSAGES.no_model).toBeTruthy()
    expect(CAPTURE_BLOCKED_MESSAGES.stale).toBeTruthy()
  })
})
