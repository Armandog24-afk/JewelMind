import { describe, expect, it } from 'vitest'
import { computeModelState, describeModelState } from './modelState'

describe('computeModelState', () => {
  it('is NO_MODEL before any generation has ever succeeded', () => {
    expect(computeModelState({ generationStatus: 'idle', hasLastGoodPreview: false, isStale: false })).toBe(
      'NO_MODEL',
    )
  })

  it('is GENERATING_FIRST_MODEL while generating with no prior good preview', () => {
    expect(
      computeModelState({ generationStatus: 'generating', hasLastGoodPreview: false, isStale: false }),
    ).toBe('GENERATING_FIRST_MODEL')
  })

  it('is REGENERATING while generating with a prior good preview', () => {
    expect(computeModelState({ generationStatus: 'generating', hasLastGoodPreview: true, isStale: true })).toBe(
      'REGENERATING',
    )
  })

  it('is CURRENT after a clean success with no edits since', () => {
    expect(computeModelState({ generationStatus: 'success', hasLastGoodPreview: true, isStale: false })).toBe(
      'CURRENT',
    )
  })

  it('is STALE once a parameter changes after a successful generation', () => {
    expect(computeModelState({ generationStatus: 'success', hasLastGoodPreview: true, isStale: true })).toBe(
      'STALE',
    )
  })

  it('is FAILED_NO_MODEL when the very first generation attempt fails', () => {
    expect(computeModelState({ generationStatus: 'error', hasLastGoodPreview: false, isStale: false })).toBe(
      'FAILED_NO_MODEL',
    )
  })

  it('is FAILED_WITH_LAST_GOOD immediately after a failed regeneration', () => {
    expect(computeModelState({ generationStatus: 'error', hasLastGoodPreview: true, isStale: false })).toBe(
      'FAILED_WITH_LAST_GOOD',
    )
  })

  it('prefers STALE over FAILED_WITH_LAST_GOOD once the user edits again after a failure', () => {
    expect(computeModelState({ generationStatus: 'error', hasLastGoodPreview: true, isStale: true })).toBe(
      'STALE',
    )
  })

  it('every state has a non-empty label and detail, never relying on color alone', () => {
    const keys = [
      'NO_MODEL',
      'GENERATING_FIRST_MODEL',
      'CURRENT',
      'STALE',
      'REGENERATING',
      'FAILED_NO_MODEL',
      'FAILED_WITH_LAST_GOOD',
    ] as const
    for (const key of keys) {
      const d = describeModelState(key)
      expect(d.label.length).toBeGreaterThan(0)
      expect(d.detail.length).toBeGreaterThan(0)
    }
  })
})
