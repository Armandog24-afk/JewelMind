import { describe, expect, it } from 'vitest'

import {
  createDefaultDefinition,
  isValidJewelryDefinition,
} from '@shared/types/jewelry-definition'
import type {
  ArrangementDefinition,
  JewelryDefinition,
} from '@shared/types/jewelry-definition'
import { hasErrors, validateDefinition } from '@shared/validation/engine'

/**
 * The frontend arrangement mirror (Sprint 22).
 *
 * A DELIBERATE SUBSET of the backend's rules: the frontend does not
 * reimplement pattern resolution, so `JM-ARRANGE-004` and `JM-ARRANGE-006` are
 * backend-only. What it must never do is report something the backend would
 * not, or miss something it claims to check.
 */

function withArrangement(arrangement: ArrangementDefinition): JewelryDefinition {
  return { ...createDefaultDefinition(), arrangement }
}

function instance(
  instanceId: string,
  over: Partial<ArrangementDefinition['instances'][number]> = {},
) {
  return {
    instanceId,
    stoneRef: 'primary',
    role: 'CENTER' as const,
    placement: {
      mode: 'EXPLICIT' as const,
      frame: 'DESIGN_ORIGIN' as const,
      transform: { xMm: 0, yMm: 0, zMm: 0, rotationDeg: 0 },
      groupId: null,
    },
    overrides: { scale: null, orientationDeg: null },
    gem: null,
    sourcePatternId: null,
    ...over,
  }
}

function arrangementRuleIds(definition: JewelryDefinition): string[] {
  return validateDefinition(definition)
    .filter((result) => result.ruleId.startsWith('JM-ARRANGE'))
    .map((result) => result.ruleId)
}

describe('the default definition', () => {
  it('declares no arrangement', () => {
    // Defaulting to a one-instance arrangement would give every stored design
    // an arrangement it never declared.
    expect(createDefaultDefinition().arrangement).toBeNull()
  })

  it('produces no arrangement findings', () => {
    expect(arrangementRuleIds(createDefaultDefinition())).toEqual([])
  })
})

describe('backward compatibility', () => {
  it('accepts a stored definition saved before arrangements existed', () => {
    const stored: Record<string, unknown> = {
      ...createDefaultDefinition(),
    }
    delete stored['arrangement']
    expect(isValidJewelryDefinition(stored)).toBe(true)
  })

  it('validates a definition whose arrangement key is simply absent', () => {
    const stored = { ...createDefaultDefinition() } as Record<string, unknown>
    delete stored['arrangement']
    const definition = stored as unknown as JewelryDefinition
    expect(arrangementRuleIds(definition)).toEqual([])
    expect(hasErrors(validateDefinition(definition))).toBe(false)
  })
})

describe('arrangement structural rules', () => {
  it('accepts a single-instance arrangement silently', () => {
    const definition = withArrangement({
      instances: [instance('center')],
      groups: [],
      patterns: [],
      relations: [],
    })
    expect(arrangementRuleIds(definition)).toEqual([])
  })

  it('reports a duplicate instance id as an error', () => {
    const definition = withArrangement({
      instances: [instance('center'), instance('center', { role: 'SIDE' })],
      groups: [],
      patterns: [],
      relations: [],
    })
    expect(arrangementRuleIds(definition)).toContain('JM-ARRANGE-001')
    expect(hasErrors(validateDefinition(definition))).toBe(true)
  })

  it('reports a placement naming an undeclared group', () => {
    const definition = withArrangement({
      instances: [
        instance('center', {
          placement: {
            mode: 'EXPLICIT',
            frame: 'PARENT_GROUP',
            transform: { xMm: 0, yMm: 0, zMm: 0, rotationDeg: 0 },
            groupId: 'ghost',
          },
        }),
      ],
      groups: [],
      patterns: [],
      relations: [],
    })
    expect(arrangementRuleIds(definition)).toContain('JM-ARRANGE-002')
  })

  it('reports a pattern repeating an undeclared instance', () => {
    const definition = withArrangement({
      instances: [instance('center')],
      groups: [],
      patterns: [
        {
          patternId: 'halo',
          sourceInstanceId: 'ghost',
          spec: {
            kind: 'RADIAL',
            count: 6,
            radiusMm: 4.6,
            startAngleDeg: 0,
            sweepDeg: 360,
            alignToRadius: true,
          },
          memberRole: 'HALO',
          groupId: null,
        },
      ],
      relations: [],
    })
    expect(arrangementRuleIds(definition)).toContain('JM-ARRANGE-002')
  })

  it('warns rather than errors on an unresolvable stone reference', () => {
    // The document is structurally valid and still generates; only that
    // instance produces no geometry, so blocking the design would be wrong.
    const definition = withArrangement({
      instances: [instance('center', { stoneRef: 'accent' })],
      groups: [],
      patterns: [],
      relations: [],
    })
    expect(arrangementRuleIds(definition)).toContain('JM-ARRANGE-003')
    expect(hasErrors(validateDefinition(definition))).toBe(false)
  })

  it('warns when more than one instance claims the CENTER role', () => {
    const definition = withArrangement({
      instances: [instance('a'), instance('b')],
      groups: [],
      patterns: [],
      relations: [],
    })
    expect(arrangementRuleIds(definition)).toContain('JM-ARRANGE-005')
  })

  it('does not reimplement resolution', () => {
    // `JM-ARRANGE-004` (does it resolve?) and `JM-ARRANGE-006` (the generation
    // notice) are backend-only. A local resolver would eventually disagree
    // with the real one, and the backend's verdict always wins.
    const definition = withArrangement({
      instances: [instance('center')],
      groups: [],
      patterns: [
        {
          patternId: 'halo',
          sourceInstanceId: 'center',
          spec: {
            kind: 'RADIAL',
            count: 8,
            radiusMm: 4.6,
            startAngleDeg: 0,
            sweepDeg: 360,
            alignToRadius: true,
          },
          memberRole: 'HALO',
          groupId: null,
        },
      ],
      relations: [],
    })
    const ids = arrangementRuleIds(definition)
    expect(ids).not.toContain('JM-ARRANGE-004')
    expect(ids).not.toContain('JM-ARRANGE-006')
  })

  it('reports no jewelry judgment about spacing or proportion', () => {
    const forbidden = [
      'too close',
      'minimum spacing',
      'clearance',
      'not manufacturable',
      'recommend',
      'industry standard',
    ]
    const definition = withArrangement({
      instances: [
        instance('a'),
        instance('b', {
          role: 'ACCENT',
          placement: {
            mode: 'EXPLICIT',
            frame: 'DESIGN_ORIGIN',
            transform: { xMm: 0.001, yMm: 0, zMm: 0, rotationDeg: 0 },
            groupId: null,
          },
        }),
      ],
      groups: [],
      patterns: [],
      relations: [],
    })
    for (const result of validateDefinition(definition)) {
      for (const term of forbidden) {
        expect(result.message.toLowerCase()).not.toContain(term)
      }
    }
  })
})

describe('validation result integrity', () => {
  it('reports each rule at most once for a clean default design', () => {
    // Pins the fix for a real defect: `bezelRules` was registered twice, so
    // every bezel finding was reported in duplicate.
    const definition = createDefaultDefinition()
    definition.setting.type = 'bezel'
    definition.setting.bezelWallThickness = 0
    const ids = validateDefinition(definition).map((result) => result.ruleId)
    expect(ids.length).toBe(new Set(ids).size)
  })
})
