import { describe, expect, it } from 'vitest'

import { createDefaultDefinition } from '@shared/types/jewelry-definition'
import type {
  JewelryDefinition,
  MicrosettingSpec,
  PaveDefinition,
  PaveSpec,
} from '@shared/types/jewelry-definition'
import { hasErrors, validateDefinition } from '@shared/validation/engine'

/**
 * The frontend pavé mirror (Sprint 26).
 *
 * A DELIBERATE SUBSET: the frontend does not resolve a host surface and does
 * not run the pavé compiler, so `JM-PAVE-001` (does the host resolve),
 * `JM-PAVE-002` (does the compiler accept it) and `JM-PAVE-003` (how many
 * cells the surface clipped) are backend-only. What the mirror must never do
 * is report something the backend would not (FORGE-GOV-004).
 */

function paveSpec(over: Partial<PaveSpec> = {}): PaveSpec {
  return {
    kind: 'PAVE',
    angularSpanDeg: 90,
    startAngleDeg: 0,
    axialSpanMm: null,
    pitchMm: 1,
    rowPitchMm: null,
    rowCount: 1,
    pattern: 'GRID',
    rowOffsetFraction: 0.5,
    termination: 'CENTERED',
    symmetry: 'SYMMETRIC',
    ...over,
  }
}

function microSpec(over: Partial<MicrosettingSpec> = {}): MicrosettingSpec {
  return {
    kind: 'MICROSETTING',
    columnCount: 12,
    rowCount: 1,
    stoneSpacingMm: 0.8,
    rowSpacingMm: null,
    startAngleDeg: 0,
    axialOffsetMm: 0,
    pattern: 'STAGGERED',
    rowOffsetFraction: 0.5,
    termination: 'CENTERED',
    symmetry: 'SYMMETRIC',
    ...over,
  }
}

function pave(over: Partial<PaveDefinition> = {}): PaveDefinition {
  return {
    paveId: 'pave',
    enabled: true,
    kind: 'PAVE',
    spec: paveSpec(),
    host: 'BAND_OUTER',
    stoneRef: 'primary',
    stoneScale: 0.1,
    stoneOrientationDeg: 0,
    gem: null,
    retention: {
      strategy: 'SHARED_BEAD',
      beadRadiusMm: 0.18,
      beadEmbedMm: 0.06,
      prongHeightMm: 0.35,
    },
    seat: { mode: 'NONE', clearanceMm: 0.02 },
    containment: 'CLIP',
    explicitPlacements: [],
    label: null,
    ...over,
  }
}

function design(over: Partial<JewelryDefinition> = {}): JewelryDefinition {
  return { ...createDefaultDefinition(), ...over }
}

function paveRuleIds(definition: JewelryDefinition): Record<string, string> {
  const out: Record<string, string> = {}
  for (const result of validateDefinition(definition)) {
    if (result.ruleId.startsWith('JM-PAVE')) {
      out[result.ruleId] = result.severity
    }
  }
  return out
}

describe('the default definition', () => {
  it('declares no pavé, exactly as before Sprint 26', () => {
    expect(createDefaultDefinition().pave).toBeNull()
  })

  it('produces no pavé findings', () => {
    expect(paveRuleIds(createDefaultDefinition())).toEqual({})
  })
})

describe('the execution boundary is always reported', () => {
  it('states the professional-review requirement on every field', () => {
    const results = validateDefinition(design({ pave: pave() })).filter(
      (r) => r.ruleId === 'JM-PAVE-005',
    )
    expect(results).toHaveLength(1)
    expect(results[0]?.message).toContain('professionally validated')
    expect(results[0]?.message).toContain('qualified jewelry professional')
  })

  it('names retention NONE as an explicit choice', () => {
    const definition = design({
      pave: pave({
        retention: {
          strategy: 'NONE',
          beadRadiusMm: 0.18,
          beadEmbedMm: 0.06,
          prongHeightMm: 0.35,
        },
      }),
    })
    const message = validateDefinition(definition).find(
      (r) => r.ruleId === 'JM-PAVE-005',
    )?.message
    expect(message).toContain("retention is 'NONE'")
  })

  it('reports a disabled field as disabled and nothing else', () => {
    const results = paveRuleIds(design({ pave: pave({ enabled: false }) }))
    expect(Object.keys(results)).toEqual(['JM-PAVE-005'])
  })
})

describe('the pitch check is arithmetic, not a threshold', () => {
  it('warns when the stones are wider than the pitch', () => {
    const definition = design({
      pave: pave({ stoneScale: 0.3, spec: paveSpec({ pitchMm: 0.3 }) }),
    })
    expect(paveRuleIds(definition)['JM-PAVE-006']).toBe('warning')
    // A geometric inconsistency is not an error: the design is still buildable.
    expect(hasErrors(validateDefinition(definition))).toBe(false)
  })

  it('stays quiet when they fit', () => {
    const definition = design({
      pave: pave({ stoneScale: 0.05, spec: paveSpec({ pitchMm: 1.5 }) }),
    })
    expect(paveRuleIds(definition)['JM-PAVE-006']).toBeUndefined()
  })

  it('reads a microsetting spacing from its own field', () => {
    const definition = design({
      pave: pave({
        kind: 'MICROSETTING',
        stoneScale: 0.3,
        spec: microSpec({ stoneSpacingMm: 0.3 }),
      }),
    })
    expect(paveRuleIds(definition)['JM-PAVE-006']).toBe('warning')
  })

  it('never states a minimum spacing', () => {
    const definition = design({
      pave: pave({ stoneScale: 0.3, spec: paveSpec({ pitchMm: 0.3 }) }),
    })
    for (const result of validateDefinition(definition)) {
      if (!result.ruleId.startsWith('JM-PAVE')) continue
      const lowered = result.message.toLowerCase()
      expect(lowered).not.toContain('minimum spacing')
      expect(lowered).not.toContain('industry standard')
      expect(lowered).not.toContain('not manufacturable')
    }
  })
})

describe('reference resolution', () => {
  it('warns, and does not block, on an unresolved stone reference', () => {
    const definition = design({ pave: pave({ stoneRef: 'accent' }) })
    expect(paveRuleIds(definition)['JM-PAVE-004']).toBe('warning')
    expect(hasErrors(validateDefinition(definition))).toBe(false)
  })
})

describe('the mirror stays a subset', () => {
  it('never reports the backend-only rules', () => {
    const definition = design({
      pave: pave({ spec: paveSpec({ rowCount: 8 }), containment: 'REJECT' }),
    })
    const ids = Object.keys(paveRuleIds(definition))
    expect(ids).not.toContain('JM-PAVE-001')
    expect(ids).not.toContain('JM-PAVE-002')
    expect(ids).not.toContain('JM-PAVE-003')
  })
})

describe('the pavé type mirrors the backend', () => {
  it('offers only hosts the backend can resolve', () => {
    const hosts: PaveDefinition['host'][] = ['BAND_OUTER', 'HEAD_PLANE']
    for (const host of hosts) {
      expect(pave({ host }).host).toBe(host)
    }
  })

  it('offers only retention strategies with a real builder', () => {
    const strategies: PaveDefinition['retention']['strategy'][] = [
      'NONE',
      'BEAD',
      'SHARED_BEAD',
      'MICRO_PRONG',
    ]
    expect(strategies).toHaveLength(4)
  })

  it('keeps the two specs distinguishable by their discriminator', () => {
    expect(paveSpec().kind).toBe('PAVE')
    expect(microSpec().kind).toBe('MICROSETTING')
  })
})
