import { describe, expect, it } from 'vitest'
import {
  createDefaultDefinition,
  type JewelryDefinition,
} from '@shared/types/jewelry-definition'
import { validateDefinition } from '@shared/validation/engine'
import { RULE_IDS } from '@shared/validation/rules'

/**
 * The Ring Families mirror (Sprint 28).
 *
 * FORGE-GOV-004: this mirror may only ever enforce a SUBSET of the backend, and
 * the backend's verdict always wins. Two of the five `JM-RINGFAM-*` rules are
 * mirrored, and the tests below assert both that the two work and that the
 * other three stay absent — a mirror enforcing something the backend does not
 * is the failure mode this rule exists to prevent.
 */

function withRingFamily(patch: Partial<JewelryDefinition>): JewelryDefinition {
  return { ...createDefaultDefinition(), ...patch }
}

const ids = (d: JewelryDefinition) => validateDefinition(d).map((r) => r.ruleId)

describe('ring family validation mirror', () => {
  it('stays silent on a pre-Sprint-28 document', () => {
    // Every existing design is a `solitaire` with no `ringFamily` and a
    // UNIFORM band, so the whole existing corpus must produce nothing here.
    expect(ids(createDefaultDefinition())).not.toContain(
      RULE_IDS.RING_FAMILY_VARIANT_MATCHES,
    )
    expect(ids(createDefaultDefinition())).not.toContain(
      RULE_IDS.RING_FAMILY_GEOMETRY_FEASIBLE,
    )
  })

  it('accepts a variant belonging to the declared family', () => {
    const base = createDefaultDefinition()
    const d = withRingFamily({
      jewelry: { ...base.jewelry, style: 'split_shank' },
      ringFamily: {
        variant: 'SPLIT_SHANK_TAPERED',
        enabled: true,
        params: defaultParams(),
        label: null,
      },
    })
    expect(ids(d)).not.toContain(RULE_IDS.RING_FAMILY_VARIANT_MATCHES)
  })

  it('refuses a variant belonging to another family', () => {
    const base = createDefaultDefinition()
    const d = withRingFamily({
      jewelry: { ...base.jewelry, style: 'halo' },
      ringFamily: {
        variant: 'SPLIT_SHANK_PARALLEL',
        enabled: true,
        params: defaultParams(),
        label: null,
      },
    })
    const result = validateDefinition(d).find(
      (r) => r.ruleId === RULE_IDS.RING_FAMILY_VARIANT_MATCHES,
    )
    expect(result?.severity).toBe('error')
    // Refused, never resolved by precedence — the same wording the backend
    // uses, because the reason is the same.
    expect(result?.message).toMatch(/no determinate resolution/)
    expect(result?.parameter).toBe('ringFamily.variant')
  })

  it('distinguishes the two-segment family prefixes', () => {
    // `SPLIT_SHANK_*` and `THREE_STONE_*` would both recover the wrong family
    // from a single split on `_`; the prefix table is tried longest-first.
    const base = createDefaultDefinition()
    for (const [variant, style] of [
      ['SPLIT_SHANK_PARALLEL', 'split_shank'],
      ['THREE_STONE_GRADUATED', 'three_stone'],
    ] as const) {
      const d = withRingFamily({
        jewelry: { ...base.jewelry, style },
        ringFamily: { variant, enabled: true, params: defaultParams(), label: null },
      })
      expect(ids(d)).not.toContain(RULE_IDS.RING_FAMILY_VARIANT_MATCHES)
    }
  })

  it('ignores a disabled family block', () => {
    const base = createDefaultDefinition()
    const d = withRingFamily({
      jewelry: { ...base.jewelry, style: 'halo' },
      ringFamily: {
        // Would be refused if it were enabled; disabled, the family's own
        // default variant is what gets built.
        variant: 'SPLIT_SHANK_PARALLEL',
        enabled: false,
        params: defaultParams(),
        label: null,
      },
    })
    expect(ids(d)).not.toContain(RULE_IDS.RING_FAMILY_VARIANT_MATCHES)
  })

  it('refuses a separation that leaves no rail', () => {
    const base = createDefaultDefinition()
    const d = withRingFamily({
      band: { ...base.band, width: 2.2, architecture: 'SPLIT', splitSeparation: 2.2 },
    })
    const result = validateDefinition(d).find(
      (r) => r.ruleId === RULE_IDS.RING_FAMILY_GEOMETRY_FEASIBLE,
    )
    expect(result?.severity).toBe('error')
    expect(result?.parameter).toBe('band.splitSeparation')
    // ARITHMETIC, not a threshold: the message states what the geometry leaves,
    // never how thin a rail may be.
    expect(result?.message).toMatch(/0\.0000 mm/)
    expect(result?.message).not.toMatch(/too thin|minimum|unsafe/i)
  })

  it('accepts a separation that leaves real rail', () => {
    const base = createDefaultDefinition()
    const d = withRingFamily({
      band: { ...base.band, width: 2.2, architecture: 'SPLIT', splitSeparation: 1.2 },
    })
    expect(ids(d)).not.toContain(RULE_IDS.RING_FAMILY_GEOMETRY_FEASIBLE)
  })

  it('checks the bypass separation against its own field', () => {
    const base = createDefaultDefinition()
    const d = withRingFamily({
      band: { ...base.band, width: 2.2, architecture: 'BYPASS', bypassSeparation: 3 },
    })
    const result = validateDefinition(d).find(
      (r) => r.ruleId === RULE_IDS.RING_FAMILY_GEOMETRY_FEASIBLE,
    )
    expect(result?.parameter).toBe('band.bypassSeparation')
  })

  it('leaves the separations of a UNIFORM band unchecked', () => {
    // The separations exist on every band and mean nothing until an
    // architecture reads them; checking them regardless would report an error
    // on a design that builds perfectly well.
    const base = createDefaultDefinition()
    const d = withRingFamily({
      band: { ...base.band, width: 2.2, splitSeparation: 9, bypassSeparation: 9 },
    })
    expect(ids(d)).not.toContain(RULE_IDS.RING_FAMILY_GEOMETRY_FEASIBLE)
  })

  it('mirrors no rule the backend owns alone', () => {
    // The three unmirrored rules each need something the frontend does not
    // have: the resolver's derived-path table, its `parameters_read_by()`, or
    // the capability registry. A mirror must never define a capability status
    // the backend has not.
    const published = Object.values(RULE_IDS)
    expect(published).not.toContain('JM-RINGFAM-002')
    expect(published).not.toContain('JM-RINGFAM-003')
    expect(published).not.toContain('JM-RINGFAM-005')
  })
})

/** The backend's `default_params()`, for building a spec in a test. */
function defaultParams() {
  return {
    headHeightFactor: 1.0,
    shoulderSpanDeg: 50,
    shoulderTopWidthFactor: 0.85,
    shoulderTopThicknessFactor: 0.85,
    splitSeparationMm: 1.2,
    splitJoinSpanDeg: 200,
    bypassSeparationMm: 1.0,
    bypassOverlapDeg: 60,
    signetTableLengthMm: 11,
    signetTableWidthMm: 9,
    signetTableHeightMm: 2,
    sideStoneScale: 0.55,
    sideSpacingMm: 5,
    sideGraduationFactor: 0.8,
    haloStoneCount: 16,
    haloRadiusFactor: 1.05,
    haloStoneScale: 0.22,
    paveShoulders: false,
    paveSpanDeg: 90,
    paveStoneScale: 0.1,
    symmetry: 'SYMMETRIC' as const,
  }
}
