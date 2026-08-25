import { beforeEach, describe, expect, it } from 'vitest'
import type { DesignIntent, IntentStatement } from '../api/types'
import { useDesignIntentStore } from './useDesignIntentStore'

function statement(overrides: Partial<IntentStatement> = {}): IntentStatement {
  return {
    intentId: 'intent-1',
    target: 'RING',
    concept: 'VISUAL_WEIGHT',
    value: 'DELICATE',
    strength: 'PREFERRED',
    priority: 0,
    provenance: 'AI_NORMALIZED',
    confidenceClass: 'HIGH_CONFIDENCE_NORMALIZATION',
    sourceText: 'delicato',
    resolutionStatus: 'PRESERVED',
    relatedJDLPaths: [],
    diagnostics: [],
    ...overrides,
  }
}

function intent(overrides: Partial<DesignIntent> = {}): DesignIntent {
  return {
    version: '1.0.0',
    sourceText: 'text',
    statements: [],
    relationships: [],
    unresolvedDescriptors: [],
    conflicts: [],
    profile: null,
    diagnostics: [],
    ...overrides,
  }
}

describe('useDesignIntentStore', () => {
  beforeEach(() => {
    useDesignIntentStore.getState().clearIntent()
  })

  it('starts with no current intent', () => {
    expect(useDesignIntentStore.getState().currentIntent).toBeNull()
  })

  it('applyIntent replaces the current intent wholesale', () => {
    const first = intent({ statements: [statement()] })
    useDesignIntentStore.getState().applyIntent(first)
    expect(useDesignIntentStore.getState().currentIntent).toEqual(first)
  })

  it('removeStatement removes only the matching statement', () => {
    const a = statement({ intentId: 'a' })
    const b = statement({ intentId: 'b', concept: 'SIMPLICITY', value: 'MINIMAL' })
    useDesignIntentStore.getState().applyIntent(intent({ statements: [a, b] }))

    useDesignIntentStore.getState().removeStatement('a')

    const remaining = useDesignIntentStore.getState().currentIntent?.statements
    expect(remaining).toHaveLength(1)
    expect(remaining?.[0]?.intentId).toBe('b')
  })

  it('removeStatement is a no-op when there is no current intent', () => {
    useDesignIntentStore.getState().removeStatement('does-not-exist')
    expect(useDesignIntentStore.getState().currentIntent).toBeNull()
  })

  it('removeUnresolvedDescriptor removes only the matching text', () => {
    useDesignIntentStore.getState().applyIntent(intent({ unresolvedDescriptors: ['elegant', 'unique'] }))
    useDesignIntentStore.getState().removeUnresolvedDescriptor('elegant')
    expect(useDesignIntentStore.getState().currentIntent?.unresolvedDescriptors).toEqual(['unique'])
  })

  it('clearIntent resets to null', () => {
    useDesignIntentStore.getState().applyIntent(intent({ statements: [statement()] }))
    useDesignIntentStore.getState().clearIntent()
    expect(useDesignIntentStore.getState().currentIntent).toBeNull()
  })
})
