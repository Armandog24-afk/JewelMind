import { describe, expect, it } from 'vitest'

import { createDefaultDefinition } from '@shared/types/jewelry-definition'
import type {
  FamilyDefinition,
  FamilyMember,
  HaloDefinition,
  HaloRing,
  JewelryDefinition,
} from '@shared/types/jewelry-definition'
import { hasErrors, validateDefinition } from '@shared/validation/engine'

/**
 * The frontend halo mirror (Sprint 25).
 *
 * A DELIBERATE SUBSET: the frontend does not reimplement halo composition, so
 * `JM-HALO-001` (does the named centre exist in the real compiled placement),
 * `JM-HALO-002` (does the real compiler accept it) and `JM-HALO-005` (the
 * metal-coverage report) are backend-only. What the mirror must never do is
 * report something the backend would not (FORGE-GOV-004).
 */

function ring(over: Partial<HaloRing> = {}): HaloRing {
  return {
    ringId: 'halo.inner',
    count: 8,
    radiusMm: 3.4,
    radiusYMm: null,
    startAngleDeg: 0,
    sweepDeg: 360,
    zOffsetMm: 0,
    memberScale: 0.25,
    alignToRadius: true,
    stoneRef: 'primary',
    gem: null,
    settingRef: null,
    members: [],
    ...over,
  }
}

function member(memberId: string, over: Partial<FamilyMember> = {}): FamilyMember {
  return {
    memberId,
    role: 'HALO',
    stoneRef: 'primary',
    gem: null,
    scale: null,
    orientationDeg: null,
    placementOverride: null,
    settingRef: null,
    ...over,
  }
}

function halo(over: Partial<HaloDefinition> = {}): HaloDefinition {
  return {
    variant: 'SINGLE',
    rings: [ring()],
    centerMemberId: 'center',
    label: null,
    ...over,
  }
}

function toiEtMoi(): FamilyDefinition {
  return {
    familyType: 'TOI_ET_MOI',
    params: {
      kind: 'TOI_ET_MOI',
      separationMm: 5,
      axisAngleDeg: 0,
      symmetry: 'SYMMETRIC',
    },
    members: [],
    label: null,
  }
}

function threeStone(): FamilyDefinition {
  return {
    familyType: 'THREE_STONE',
    params: {
      kind: 'THREE_STONE',
      sideSpacingMm: 4.6,
      sideScale: 0.6,
      symmetry: 'SYMMETRIC',
    },
    members: [],
    label: null,
  }
}

function design(over: Partial<JewelryDefinition> = {}): JewelryDefinition {
  return { ...createDefaultDefinition(), ...over }
}

function haloRuleIds(definition: JewelryDefinition): Record<string, string> {
  const out: Record<string, string> = {}
  for (const result of validateDefinition(definition)) {
    if (result.ruleId.startsWith('JM-HALO')) {
      out[result.ruleId] = result.severity
    }
  }
  return out
}

describe('the default definition', () => {
  it('declares no halo, exactly as before Sprint 25', () => {
    expect(createDefaultDefinition().halo).toBeNull()
  })

  it('produces no halo findings', () => {
    expect(haloRuleIds(createDefaultDefinition())).toEqual({})
  })
})

describe('composition support', () => {
  it('accepts a named centre in a three-stone family', () => {
    expect(haloRuleIds(design({ halo: halo(), family: threeStone() }))).toEqual({})
  })

  it('refuses a named centre in a toi-et-moi, which has no centre member', () => {
    const definition = design({ halo: halo(), family: toiEtMoi() })
    expect(haloRuleIds(definition)['JM-HALO-003']).toBe('error')
    expect(hasErrors(validateDefinition(definition))).toBe(true)
  })

  it('accepts an origin-anchored halo around a toi-et-moi pair', () => {
    const definition = design({
      halo: halo({ centerMemberId: null }),
      family: toiEtMoi(),
    })
    expect(haloRuleIds(definition)).toEqual({})
  })

  it('reports one finding for one cause', () => {
    const definition = design({ halo: halo(), family: toiEtMoi() })
    expect(Object.keys(haloRuleIds(definition))).toEqual(['JM-HALO-003'])
  })
})

describe('reference resolution', () => {
  it('warns, and does not block, on an unresolved stone reference', () => {
    const definition = design({ halo: halo({ rings: [ring({ stoneRef: 'side' })] }) })
    expect(haloRuleIds(definition)['JM-HALO-004']).toBe('warning')
    expect(hasErrors(validateDefinition(definition))).toBe(false)
  })

  it('warns on a per-stone override naming another stone', () => {
    const definition = design({
      halo: halo({ rings: [ring({ members: [member('halo.inner.a', { stoneRef: 'side' })] })] }),
    })
    expect(haloRuleIds(definition)['JM-HALO-004']).toBe('warning')
  })

  it('warns when a ring requests a setting the design does not use', () => {
    const definition = design({ halo: halo({ rings: [ring({ settingRef: 'bezel' })] }) })
    definition.setting.type = 'prong'
    expect(haloRuleIds(definition)['JM-HALO-004']).toBe('warning')
  })

  it('stays quiet when the requested setting matches', () => {
    const definition = design({ halo: halo({ rings: [ring({ settingRef: 'prong' })] }) })
    definition.setting.type = 'prong'
    expect(haloRuleIds(definition)).toEqual({})
  })
})

describe('the mirror stays a subset', () => {
  it('never reports the backend-only rules', () => {
    const definition = design({ halo: halo({ centerMemberId: 'nowhere' }) })
    const ids = Object.keys(haloRuleIds(definition))
    expect(ids).not.toContain('JM-HALO-001')
    expect(ids).not.toContain('JM-HALO-002')
    expect(ids).not.toContain('JM-HALO-005')
  })

  it('defers to the backend when a family and an arrangement conflict', () => {
    const definition = design({
      halo: halo(),
      family: threeStone(),
      arrangement: { instances: [], groups: [], patterns: [], relations: [] },
    })
    expect(haloRuleIds(definition)).toEqual({})
    const ids = validateDefinition(definition).map((r) => r.ruleId)
    expect(ids).toContain('JM-FAMILY-001')
  })
})

describe('the halo type mirrors the backend', () => {
  it('offers only variants the backend compiles', () => {
    const variants: HaloDefinition['variant'][] = ['SINGLE', 'DOUBLE', 'HIDDEN']
    for (const variant of variants) {
      expect(halo({ variant }).variant).toBe(variant)
    }
  })

  it('carries a vertical offset, which is what makes a hidden halo real', () => {
    expect(ring({ zOffsetMm: -1.4 }).zOffsetMm).toBe(-1.4)
  })

  it('reuses the family member model for per-stone overrides', () => {
    const override = member('halo.inner.crest', { scale: 0.4 })
    const [first] = ring({ members: [override] }).members
    expect(first?.role).toBe('HALO')
    expect(first?.scale).toBe(0.4)
  })
})
