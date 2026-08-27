/**
 * Frontend mirror of the deterministic validation engine, for instant
 * feedback while the user edits the form. This is NOT authoritative — the
 * backend (backend/jewelmind/validation/engine.py) re-validates every
 * definition before generation and export, and its verdict always wins.
 * Keep the two engines in sync by hand; if they ever disagree, trust the
 * backend response.
 */

import type { JewelryDefinition } from '../types/jewelry-definition'
import { RULE_IDS, type ValidationResult } from './rules'
import { euSizeToInnerDiameter, sizingConsistency } from './sizing'

function ringRules(d: JewelryDefinition): ValidationResult[] {
  const out: ValidationResult[] = []

  if (!(d.ring.innerDiameter > 10 && d.ring.innerDiameter < 30)) {
    out.push({
      ruleId: RULE_IDS.RING_INNER_DIAMETER_RANGE,
      severity: 'error',
      message: 'Ring inner diameter must be greater than 10 mm and lower than 30 mm.',
      parameter: 'ring.innerDiameter',
    })
  }

  if (!(d.ring.size > 1 && d.ring.size < 50)) {
    out.push({
      ruleId: RULE_IDS.RING_SIZE_RANGE,
      severity: 'error',
      message: 'EU ring size must be greater than 1 and lower than 50.',
      parameter: 'ring.size',
    })
  }

  const consistency = sizingConsistency(d.ring.size, d.ring.innerDiameter)
  if (consistency !== null) {
    const implied = euSizeToInnerDiameter(d.ring.size)
    out.push({
      ruleId: RULE_IDS.RING_SIZE_DIAMETER_CONSISTENCY,
      severity: consistency,
      message: `EU size ${d.ring.size} implies an inner diameter of ${implied.toFixed(2)} mm, which differs from the stored ${d.ring.innerDiameter} mm. Sizing conventions vary; review which value should take precedence.`,
      parameter: 'ring.innerDiameter',
      suggestedValue: Math.round(implied * 100) / 100,
    })
  }

  return out
}

function bandRules(d: JewelryDefinition): ValidationResult[] {
  const out: ValidationResult[] = []

  if (d.band.width < 1.5) {
    out.push({
      ruleId: RULE_IDS.BAND_WIDTH_MIN,
      severity: 'error',
      message: 'Band width below 1.5 mm is not supported.',
      parameter: 'band.width',
      suggestedValue: 1.5,
    })
  } else if (d.band.width > 12) {
    out.push({
      ruleId: RULE_IDS.BAND_WIDTH_MAX,
      severity: 'warning',
      message: 'Band width above 12 mm is unusually wide for a solitaire band.',
      parameter: 'band.width',
    })
  }

  if (d.band.thickness < 1.4) {
    out.push({
      ruleId: RULE_IDS.BAND_THICKNESS_MIN,
      severity: 'error',
      message: 'Band thickness below 1.4 mm is not supported.',
      parameter: 'band.thickness',
      suggestedValue: 1.4,
    })
  } else if (d.band.thickness < 1.6) {
    out.push({
      ruleId: RULE_IDS.BAND_THICKNESS_MIN,
      severity: 'warning',
      message: 'Band thickness below 1.6 mm may be structurally fragile.',
      parameter: 'band.thickness',
      suggestedValue: 1.6,
    })
  }

  return out
}

function resolvedStoneLength(d: JewelryDefinition): number {
  return d.stone.shape === 'round' ? (d.stone.diameter as number) : (d.stone.length as number)
}

function resolvedStoneWidth(d: JewelryDefinition): number {
  return d.stone.shape === 'round' ? (d.stone.diameter as number) : (d.stone.width as number)
}

function stoneRules(d: JewelryDefinition): ValidationResult[] {
  // Sprint 18: STONE_DIAMETER_RANGE is ROUND_ONLY; STONE_DEPTH_RANGE is
  // SHARED, generalized to the stone's real minimum horizontal extent —
  // mirrors backend/jewelmind/validation/engine.py::_stone_rules()
  // exactly (FORGE-GOV-004). See docs/bible/20-stone/578-current-code-mapping-and-gaps.md.
  const out: ValidationResult[] = []

  if (d.stone.shape === 'round') {
    const diameter = d.stone.diameter as number
    if (!(diameter >= 2 && diameter <= 15)) {
      out.push({
        ruleId: RULE_IDS.STONE_DIAMETER_RANGE,
        severity: 'error',
        message: 'Stone diameter must be between 2 mm and 15 mm.',
        parameter: 'stone.diameter',
      })
    }
  }

  const minExtent = Math.min(resolvedStoneLength(d), resolvedStoneWidth(d))
  if (!(d.stone.depth > 0.5 && d.stone.depth < minExtent)) {
    out.push({
      ruleId: RULE_IDS.STONE_DEPTH_RANGE,
      severity: 'error',
      message: "Stone depth must be greater than 0.5 mm and lower than the stone's minimum horizontal extent.",
      parameter: 'stone.depth',
    })
  }

  return out
}

function prongRules(d: JewelryDefinition): ValidationResult[] {
  const out: ValidationResult[] = []

  if (d.setting.prongCount !== 4 && d.setting.prongCount !== 6) {
    out.push({
      ruleId: RULE_IDS.PRONG_COUNT,
      severity: 'error',
      message: 'Prong count must be exactly 4 or 6.',
      parameter: 'setting.prongCount',
      suggestedValue: 6,
    })
  }

  if (d.setting.prongDiameter < 0.8) {
    out.push({
      ruleId: RULE_IDS.PRONG_DIAMETER_MIN,
      severity: 'error',
      message: 'Prong diameter below 0.8 mm is not supported.',
      parameter: 'setting.prongDiameter',
      suggestedValue: 0.8,
    })
  } else if (d.setting.prongDiameter < 1.0) {
    out.push({
      ruleId: RULE_IDS.PRONG_DIAMETER_MIN,
      severity: 'warning',
      message: 'Prong diameter below 1.0 mm may be structurally fragile.',
      parameter: 'setting.prongDiameter',
      suggestedValue: 1.0,
    })
  }

  // ROUND_ONLY (Sprint 18) — see backend's identical guard and rationale.
  if (d.stone.shape === 'round' && (d.stone.diameter as number) > 8 && d.setting.prongCount === 4) {
    out.push({
      ruleId: RULE_IDS.PRONG_COUNT_VS_STONE_SIZE,
      severity: 'warning',
      message: 'Stones larger than 8 mm are typically more secure with six prongs.',
      parameter: 'setting.prongCount',
      suggestedValue: 6,
    })
  }

  if (!(d.setting.prongHeight > d.setting.basketHeight)) {
    out.push({
      ruleId: RULE_IDS.PRONG_HEIGHT_VS_BASKET,
      severity: 'error',
      message: 'Prong height must be greater than basket height.',
      parameter: 'setting.prongHeight',
    })
  }

  return out
}

function settingRules(d: JewelryDefinition): ValidationResult[] {
  const out: ValidationResult[] = []

  if (d.setting.basketHeight <= 0) {
    out.push({
      ruleId: RULE_IDS.SETTING_BASKET_HEIGHT_POSITIVE,
      severity: 'error',
      message: 'Basket height must be positive.',
      parameter: 'setting.basketHeight',
    })
  } else if (d.setting.basketHeight > 8) {
    out.push({
      ruleId: RULE_IDS.SETTING_BASKET_HEIGHT_MAX,
      severity: 'warning',
      message: 'Basket height above 8 mm is unusually tall.',
      parameter: 'setting.basketHeight',
    })
  }

  return out
}

function manufacturingRules(d: JewelryDefinition): ValidationResult[] {
  if (d.manufacturing.method !== 'direct_resin_printing') return []

  const out: ValidationResult[] = []
  const structuralParams: Array<[string, number]> = [
    ['band.thickness', d.band.thickness],
    ['band.width', d.band.width],
  ]
  for (const [parameter, value] of structuralParams) {
    if (value < 0.8) {
      out.push({
        ruleId: RULE_IDS.MANUFACTURING_MIN_FEATURE,
        severity: 'warning',
        message: `${parameter} is below 0.8 mm; direct resin printing may not reliably resolve features this thin.`,
        parameter,
        suggestedValue: 0.8,
      })
    }
  }
  return out
}

function geometryRules(d: JewelryDefinition): ValidationResult[] {
  const out: ValidationResult[] = []
  const outerDiameter = d.ring.innerDiameter + 2 * d.band.thickness

  if (d.band.thickness <= 0 || outerDiameter <= d.ring.innerDiameter) {
    out.push({
      ruleId: RULE_IDS.GEOMETRY_OUTER_BAND_POSITIVE,
      severity: 'error',
      message: 'Band thickness must produce a positive outer band dimension.',
      parameter: 'band.thickness',
    })
  }

  if (d.band.width <= 0) {
    out.push({
      ruleId: RULE_IDS.GEOMETRY_OUTER_BAND_POSITIVE,
      severity: 'error',
      message: 'Band width must be positive to produce valid band geometry.',
      parameter: 'band.width',
    })
  }

  return out
}

export function validateDefinition(definition: JewelryDefinition): ValidationResult[] {
  return [
    ...ringRules(definition),
    ...bandRules(definition),
    ...stoneRules(definition),
    ...prongRules(definition),
    ...settingRules(definition),
    ...manufacturingRules(definition),
    ...geometryRules(definition),
  ]
}

export function hasErrors(results: ValidationResult[]): boolean {
  return results.some((r) => r.severity === 'error')
}
