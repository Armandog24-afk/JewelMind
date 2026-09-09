import { describe, expect, it } from 'vitest'

import { createDefaultDefinition } from '@shared/types/jewelry-definition'
import type {
  JewelryDefinition,
  SettingModeId,
  SettingModeParameters,
  SettingModeSpec,
  SettingType,
} from '@shared/types/jewelry-definition'
import { hasErrors, validateDefinition } from '@shared/validation/engine'

/**
 * The frontend Extended Setting Modes mirror (Sprint 27).
 *
 * A DELIBERATE SUBSET. The frontend does not resolve a setting mode, does not
 * know the capability registry and does not measure a stone, so
 * `JM-SETTING-009` (which parameters go unread), `JM-SETTING-011` (geometric
 * feasibility) and `JM-SETTING-013` (the mode's capability status) are
 * backend-only. What the mirror must never do is report something the backend
 * would not (FORGE-GOV-004), which is what the last test in this file asserts
 * directly.
 */

function parameters(over: Partial<SettingModeParameters> = {}): SettingModeParameters {
  return {
    openingCount: 2,
    openingSweepDeg: 40,
    openingStartAngleDeg: 90,
    collarWidthMm: 1,
    rimHeightMm: 0.4,
    gripAxisDeg: 0,
    padWidthMm: 2,
    padThicknessMm: 1.6,
    padDepthMm: 0.6,
    gripHeightMm: 1.2,
    axisDeg: 0,
    spanMm: null,
    innerWidthMm: null,
    wallThicknessMm: 0.7,
    wallHeightMm: 0.8,
    barCount: 2,
    barSpacingMm: null,
    barHeightMm: 0.8,
    barLengthMm: null,
    termination: 'OPEN',
    symmetry: 'SYMMETRIC',
    offsetXMm: 0,
    offsetYMm: 0,
    offsetZMm: 0,
    ...over,
  }
}

function mode(modeId: SettingModeId, over: Partial<SettingModeSpec> = {}): SettingModeSpec {
  return {
    modeId,
    enabled: true,
    stoneRef: 'primary',
    arrangementInstanceIds: [],
    host: 'HEAD',
    parameters: parameters(),
    label: null,
    ...over,
  }
}

function design(
  settingType: SettingType,
  over: Partial<JewelryDefinition['setting']> = {},
): JewelryDefinition {
  const definition = createDefaultDefinition()
  return {
    ...definition,
    setting: { ...definition.setting, type: settingType, ...over },
  }
}

function ruleIds(definition: JewelryDefinition): string[] {
  return validateDefinition(definition).map((r) => r.ruleId)
}

describe('setting mode family agreement (JM-SETTING-008)', () => {
  it('accepts a mode whose family matches the chosen type', () => {
    const results = validateDefinition(
      design('bezel', { mode: mode('BEZEL_PARTIAL') }),
    )
    expect(results.some((r) => r.ruleId === 'JM-SETTING-008')).toBe(false)
  })

  it('refuses a mode from another family rather than picking a winner', () => {
    const results = validateDefinition(
      design('channel', { mode: mode('BEZEL_PARTIAL') }),
    )
    const match = results.filter((r) => r.ruleId === 'JM-SETTING-008')
    expect(match).toHaveLength(1)
    expect(match[0]?.severity).toBe('error')
    expect(hasErrors(results)).toBe(true)
  })

  it('refuses a head or retention mode declared as the primary one', () => {
    for (const modeId of ['HEAD_MARTINI', 'RETENTION_SHARED_BEAD'] as SettingModeId[]) {
      const results = validateDefinition(design('prong', { mode: mode(modeId) }))
      const match = results.filter((r) => r.ruleId === 'JM-SETTING-008')
      expect(match).toHaveLength(1)
      expect(match[0]?.severity).toBe('error')
    }
  })

  it('ignores a disabled mode, which contributes nothing', () => {
    const results = validateDefinition(
      design('channel', { mode: mode('BEZEL_PARTIAL', { enabled: false }) }),
    )
    expect(results.some((r) => r.ruleId === 'JM-SETTING-008')).toBe(false)
  })

  it('says nothing when no mode is declared', () => {
    for (const type of [
      'prong',
      'bezel',
      'channel',
      'bar',
      'tension',
    ] as SettingType[]) {
      expect(ruleIds(design(type))).not.toContain('JM-SETTING-008')
    }
  })
})

describe('flush relief is a precondition (JM-SETTING-010)', () => {
  it('errors when a flush setting has no relief', () => {
    const results = validateDefinition(design('flush', { seatMode: 'NONE' }))
    const match = results.filter((r) => r.ruleId === 'JM-SETTING-010')
    expect(match).toHaveLength(1)
    expect(match[0]?.severity).toBe('error')
    expect(match[0]?.suggestedValue).toBe('REFERENCE_SEAT')
  })

  it('is silent once relief is switched on', () => {
    const results = validateDefinition(
      design('flush', { seatMode: 'REFERENCE_SEAT' }),
    )
    expect(results.some((r) => r.ruleId === 'JM-SETTING-010')).toBe(false)
    expect(hasErrors(results)).toBe(false)
  })

  it('never fires for another family with no relief', () => {
    for (const type of ['prong', 'bezel', 'channel', 'bar'] as SettingType[]) {
      expect(ruleIds(design(type, { seatMode: 'NONE' }))).not.toContain(
        'JM-SETTING-010',
      )
    }
  })
})

describe('professional review (JM-SETTING-012)', () => {
  it('warns for a tension setting and says what is not modelled', () => {
    const results = validateDefinition(design('tension'))
    const match = results.filter((r) => r.ruleId === 'JM-SETTING-012')
    expect(match).toHaveLength(1)
    expect(match[0]?.severity).toBe('warning')
    expect(match[0]?.message).toContain('spring-back')
    // A REVIEW REQUIREMENT IS NOT A VERDICT: it must never block generation.
    expect(hasErrors(results)).toBe(false)
  })

  it('fires for no other family', () => {
    for (const type of [
      'prong',
      'bezel',
      'channel',
      'bar',
      'flush',
    ] as SettingType[]) {
      const definition =
        type === 'flush'
          ? design(type, { seatMode: 'REFERENCE_SEAT' })
          : design(type)
      expect(ruleIds(definition)).not.toContain('JM-SETTING-012')
    }
  })
})

describe('the mirror stays a subset of the backend', () => {
  it('never reports a rule the backend does not own', () => {
    /**
     * FORGE-GOV-004. The three mirrored rules are the only setting-mode rules
     * this engine may emit; the backend owns 009, 011 and 013 because each
     * needs something the frontend does not have — the parameter table, the
     * stone's resolved dimensions, or the capability registry.
     */

    const emitted = new Set<string>()
    for (const type of [
      'prong',
      'bezel',
      'channel',
      'bar',
      'flush',
      'tension',
    ] as SettingType[]) {
      for (const seatMode of ['NONE', 'REFERENCE_SEAT'] as const) {
        for (const result of validateDefinition(design(type, { seatMode }))) {
          if (result.ruleId.startsWith('JM-SETTING-0')) {
            emitted.add(result.ruleId)
          }
        }
      }
    }

    const settingModeRules = [...emitted].filter(
      (id) => Number(id.slice('JM-SETTING-'.length)) >= 8,
    )
    expect(new Set(settingModeRules)).toEqual(
      new Set(['JM-SETTING-010', 'JM-SETTING-012']),
    )
  })

  it('leaves every default family free of errors', () => {
    for (const type of [
      'prong',
      'bezel',
      'channel',
      'bar',
      'tension',
    ] as SettingType[]) {
      expect(hasErrors(validateDefinition(design(type)))).toBe(false)
    }
    expect(
      hasErrors(validateDefinition(design('flush', { seatMode: 'REFERENCE_SEAT' }))),
    ).toBe(false)
  })
})

describe('the default definition is unchanged in meaning', () => {
  it('declares no setting mode, which is the pre-Sprint-27 state', () => {
    const definition = createDefaultDefinition()
    expect(definition.setting.mode).toBeNull()
    expect(definition.setting.type).toBe('prong')
    expect(definition.setting.headArchitecture).toBe('BASKET')
    expect(definition.setting.seatMode).toBe('NONE')
  })

  it('carries the gallery window defaults without an open gallery', () => {
    const definition = createDefaultDefinition()
    expect(definition.setting.galleryWindowCount).toBe(4)
    expect(definition.setting.galleryWindowHeightFraction).toBeLessThan(1)
  })
})
