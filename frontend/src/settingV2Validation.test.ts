import { describe, expect, it } from 'vitest'

import { createDefaultDefinition } from '@shared/types/jewelry-definition'
import type { JewelryDefinition } from '@shared/types/jewelry-definition'
import { hasErrors, validateDefinition } from '@shared/validation/engine'

/**
 * The frontend Setting v2 mirror (Sprint 23).
 *
 * Unlike the arrangement mirror, this one is COMPLETE: every backend check is
 * local and structural, so there is no backend-only remainder. What it must
 * never do is report something the backend would not.
 */

function settingRuleIds(definition: JewelryDefinition): Record<string, string> {
  const out: Record<string, string> = {}
  for (const result of validateDefinition(definition)) {
    if (['JM-SETTING-005', 'JM-SETTING-006', 'JM-SETTING-007'].includes(result.ruleId)) {
      out[result.ruleId] = result.severity
    }
  }
  return out
}

describe('the default definition', () => {
  it('starts on the pre-Sprint-23 behaviour', () => {
    const setting = createDefaultDefinition().setting
    expect(setting.prongStyle).toBe('ROUND_PRONG')
    expect(setting.headArchitecture).toBe('BASKET')
    expect(setting.seatMode).toBe('NONE')
    expect(setting.pegDiameter).toBeNull()
    expect(setting.pegHeight).toBeNull()
  })

  it('produces no advanced-setting findings', () => {
    expect(settingRuleIds(createDefaultDefinition())).toEqual({})
  })
})

describe('head parameter completeness', () => {
  it('reports a PEG_HEAD with no peg dimensions as an error', () => {
    const definition = createDefaultDefinition()
    definition.setting.headArchitecture = 'PEG_HEAD'
    expect(settingRuleIds(definition)['JM-SETTING-005']).toBe('error')
    expect(hasErrors(validateDefinition(definition))).toBe(true)
  })

  it('reports a peg taller than the head as an error', () => {
    const definition = createDefaultDefinition()
    definition.setting.headArchitecture = 'PEG_HEAD'
    definition.setting.pegDiameter = 1.6
    definition.setting.pegHeight = 4.0
    expect(settingRuleIds(definition)['JM-SETTING-005']).toBe('error')
  })

  it('accepts a complete PEG_HEAD', () => {
    const definition = createDefaultDefinition()
    definition.setting.headArchitecture = 'PEG_HEAD'
    definition.setting.pegDiameter = 1.6
    definition.setting.pegHeight = 1.2
    expect(settingRuleIds(definition)).toEqual({})
    expect(hasErrors(validateDefinition(definition))).toBe(false)
  })

  it('reports a non-positive peg dimension', () => {
    const definition = createDefaultDefinition()
    definition.setting.headArchitecture = 'PEG_HEAD'
    definition.setting.pegDiameter = 0
    definition.setting.pegHeight = 1.2
    expect(settingRuleIds(definition)['JM-SETTING-005']).toBe('error')
  })
})

describe('unread fields', () => {
  it('reports a prong style on a bezel as information, not a warning', () => {
    // The design is perfectly valid; the value simply has no effect.
    const definition = createDefaultDefinition()
    definition.setting.type = 'bezel'
    definition.setting.prongStyle = 'CLAW_PRONG'
    expect(settingRuleIds(definition)['JM-SETTING-006']).toBe('information')
    expect(hasErrors(validateDefinition(definition))).toBe(false)
  })

  it('reports peg fields on a non-peg head', () => {
    const definition = createDefaultDefinition()
    definition.setting.pegDiameter = 1.6
    expect(settingRuleIds(definition)['JM-SETTING-006']).toBe('information')
  })

  it('says nothing about a prong style on a prong setting', () => {
    const definition = createDefaultDefinition()
    definition.setting.prongStyle = 'V_PRONG'
    expect(settingRuleIds(definition)).toEqual({})
  })
})

describe('seat feasibility', () => {
  it('warns when relief is requested for an imported stone', () => {
    const definition = createDefaultDefinition()
    definition.setting.seatMode = 'REFERENCE_SEAT'
    definition.stone.source = 'IMPORTED_CAD'
    expect(settingRuleIds(definition)['JM-SETTING-007']).toBe('warning')
    expect(hasErrors(validateDefinition(definition))).toBe(false)
  })

  it('says nothing for relief on a parametric stone', () => {
    const definition = createDefaultDefinition()
    definition.setting.seatMode = 'REFERENCE_SEAT'
    expect(settingRuleIds(definition)).toEqual({})
  })
})

describe('backward compatibility', () => {
  it('validates a stored design saved before the new fields existed', () => {
    const stored = { ...createDefaultDefinition() }
    const setting = { ...stored.setting } as Record<string, unknown>
    for (const key of [
      'prongStyle',
      'headArchitecture',
      'seatMode',
      'prongTipRatio',
      'headBaseRatio',
      'pegDiameter',
      'pegHeight',
    ]) {
      delete setting[key]
    }
    const definition = {
      ...stored,
      setting,
    } as unknown as JewelryDefinition
    // A missing `headArchitecture` must not be read as PEG_HEAD, and a missing
    // `prongStyle` must not trip the unread-field rule.
    expect(settingRuleIds(definition)).toEqual({})
    expect(hasErrors(validateDefinition(definition))).toBe(false)
  })
})

describe('no invented professional threshold', () => {
  it('never judges thickness, castability or security', () => {
    const forbidden = [
      'too thin',
      'minimum thickness',
      'not castable',
      'not manufacturable',
      'industry standard',
      'will hold',
      'secure',
    ]
    const definitions: JewelryDefinition[] = []
    for (const over of [
      { headArchitecture: 'MARTINI' as const, headBaseRatio: 0.1 },
      { prongStyle: 'V_PRONG' as const, prongTipRatio: 0.1 },
      { seatMode: 'REFERENCE_SEAT' as const },
      { headArchitecture: 'PEG_HEAD' as const },
    ]) {
      const definition = createDefaultDefinition()
      Object.assign(definition.setting, over)
      definitions.push(definition)
    }
    for (const definition of definitions) {
      for (const result of validateDefinition(definition)) {
        for (const term of forbidden) {
          expect(result.message.toLowerCase()).not.toContain(term)
        }
      }
    }
  })
})
