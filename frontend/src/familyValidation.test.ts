import { describe, expect, it } from 'vitest'

import {
  createDefaultDefinition,
  isValidJewelryDefinition,
} from '@shared/types/jewelry-definition'
import type {
  FamilyDefinition,
  FamilyMember,
  JewelryDefinition,
} from '@shared/types/jewelry-definition'
import { hasErrors, validateDefinition } from '@shared/validation/engine'

/**
 * The frontend multi-stone family mirror (Sprint 24).
 *
 * A DELIBERATE SUBSET: the frontend does not reimplement family compilation, so
 * `JM-FAMILY-003` and `JM-FAMILY-005` are backend-only. What it must never do is
 * report something the backend would not.
 */

function member(
  memberId: string,
  role: FamilyMember['role'],
  over: Partial<FamilyMember> = {},
): FamilyMember {
  return {
    memberId,
    role,
    stoneRef: 'primary',
    gem: null,
    scale: null,
    orientationDeg: null,
    placementOverride: null,
    settingRef: null,
    ...over,
  }
}

function threeStone(members: FamilyMember[] = []): FamilyDefinition {
  return {
    familyType: 'THREE_STONE',
    params: {
      kind: 'THREE_STONE',
      sideSpacingMm: 4.6,
      sideScale: 0.6,
      symmetry: 'SYMMETRIC',
    },
    members,
    label: null,
  }
}

function withFamily(family: FamilyDefinition): JewelryDefinition {
  return { ...createDefaultDefinition(), family }
}

function familyRuleIds(definition: JewelryDefinition): Record<string, string> {
  const out: Record<string, string> = {}
  for (const result of validateDefinition(definition)) {
    if (result.ruleId.startsWith('JM-FAMILY')) {
      out[result.ruleId] = result.severity
    }
  }
  return out
}

describe('the default definition', () => {
  it('declares no family', () => {
    expect(createDefaultDefinition().family).toBeNull()
  })

  it('produces no family findings', () => {
    expect(familyRuleIds(createDefaultDefinition())).toEqual({})
  })
})

describe('single placement authority', () => {
  it('reports a family and an arrangement together as an error', () => {
    const definition = withFamily(threeStone())
    definition.arrangement = {
      instances: [
        {
          instanceId: 'center',
          stoneRef: 'primary',
          role: 'CENTER',
          placement: {
            mode: 'EXPLICIT',
            frame: 'DESIGN_ORIGIN',
            transform: { xMm: 0, yMm: 0, zMm: 0, rotationDeg: 0, tiltDeg: 0, tiltAzimuthDeg: 0 },
            groupId: null,
          },
          overrides: { scale: null, orientationDeg: null },
          gem: null,
          sourcePatternId: null,
        },
      ],
      groups: [],
      patterns: [],
      relations: [],
    }
    expect(familyRuleIds(definition)['JM-FAMILY-001']).toBe('error')
    expect(hasErrors(validateDefinition(definition))).toBe(true)
  })

  it('reports nothing else once the conflict is present', () => {
    // A second, derived failure would obscure the real one.
    const definition = withFamily(threeStone([member('h', 'HALO')]))
    definition.arrangement = {
      instances: [],
      groups: [],
      patterns: [],
      relations: [],
    }
    expect(Object.keys(familyRuleIds(definition))).toEqual(['JM-FAMILY-001'])
  })
})

describe('family roles', () => {
  it('accepts a family with no members', () => {
    // Members are derived from the parameters — that is how a twelve-stone
    // cluster is expressed without typing twelve members.
    expect(familyRuleIds(withFamily(threeStone()))).toEqual({})
  })

  it('accepts the correct role cardinality', () => {
    const definition = withFamily(
      threeStone([
        member('center', 'CENTER'),
        member('side.a', 'SIDE'),
        member('side.b', 'SIDE'),
      ]),
    )
    expect(familyRuleIds(definition)).toEqual({})
    expect(hasErrors(validateDefinition(definition))).toBe(false)
  })

  it('reports a wrong cardinality as an error', () => {
    const definition = withFamily(
      threeStone([member('center', 'CENTER'), member('side.a', 'SIDE')]),
    )
    expect(familyRuleIds(definition)['JM-FAMILY-002']).toBe('error')
  })

  it('reports a role the family does not accept', () => {
    const definition = withFamily(
      threeStone([
        member('center', 'CENTER'),
        member('side.a', 'SIDE'),
        member('side.b', 'SIDE'),
        member('halo', 'HALO'),
      ]),
    )
    expect(familyRuleIds(definition)['JM-FAMILY-002']).toBe('error')
  })
})

describe('member references', () => {
  it('warns on an unresolvable stone reference rather than erroring', () => {
    const definition = withFamily(
      threeStone([
        member('center', 'CENTER'),
        member('side.a', 'SIDE', { stoneRef: 'accent' }),
        member('side.b', 'SIDE'),
      ]),
    )
    expect(familyRuleIds(definition)['JM-FAMILY-004']).toBe('warning')
    expect(hasErrors(validateDefinition(definition))).toBe(false)
  })

  it('warns when a member requests a setting the design does not use', () => {
    const definition = withFamily(
      threeStone([
        member('center', 'CENTER'),
        member('side.a', 'SIDE', { settingRef: 'bezel' }),
        member('side.b', 'SIDE'),
      ]),
    )
    expect(familyRuleIds(definition)['JM-FAMILY-004']).toBe('warning')
  })

  it('says nothing when a member requests the design’s own setting', () => {
    const definition = withFamily(
      threeStone([
        member('center', 'CENTER'),
        member('side.a', 'SIDE', { settingRef: 'prong' }),
        member('side.b', 'SIDE'),
      ]),
    )
    expect(familyRuleIds(definition)).toEqual({})
  })
})

describe('the mirror does not reimplement compilation', () => {
  it('never reports the compile or setting-coverage rules', () => {
    // A second local compiler would eventually disagree with the real one.
    const definition = withFamily(threeStone())
    const ids = Object.keys(familyRuleIds(definition))
    expect(ids).not.toContain('JM-FAMILY-003')
    expect(ids).not.toContain('JM-FAMILY-005')
  })
})

describe('backward compatibility', () => {
  it('accepts a stored design saved before families existed', () => {
    const stored: Record<string, unknown> = { ...createDefaultDefinition() }
    delete stored['family']
    expect(isValidJewelryDefinition(stored)).toBe(true)
  })

  it('validates a definition whose family key is simply absent', () => {
    const stored: Record<string, unknown> = { ...createDefaultDefinition() }
    delete stored['family']
    const definition = stored as unknown as JewelryDefinition
    expect(familyRuleIds(definition)).toEqual({})
    expect(hasErrors(validateDefinition(definition))).toBe(false)
  })
})

describe('no invented jewelry threshold', () => {
  it('never judges spacing, proportion or stone count', () => {
    const forbidden = [
      'too close',
      'minimum spacing',
      'proportion',
      'not manufacturable',
      'industry standard',
      'too many stones',
    ]
    const families: FamilyDefinition[] = [
      threeStone(),
      {
        familyType: 'CLUSTER',
        params: {
          kind: 'CLUSTER',
          count: 40,
          radiusMm: 0.5,
          radiusYMm: null,
          startAngleDeg: 0,
          sweepDeg: 360,
          includeCenter: true,
          memberScale: 0.4,
          alignToRadius: true,
        },
        members: [],
        label: null,
      },
      {
        familyType: 'TOI_ET_MOI',
        params: {
          kind: 'TOI_ET_MOI',
          separationMm: 0.2,
          axisAngleDeg: 0,
          symmetry: 'SYMMETRIC',
        },
        members: [],
        label: null,
      },
    ]
    for (const family of families) {
      for (const result of validateDefinition(withFamily(family))) {
        for (const term of forbidden) {
          expect(result.message.toLowerCase()).not.toContain(term)
        }
      }
    }
  })
})
