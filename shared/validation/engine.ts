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
  return roundLike(d) ? (d.stone.diameter as number) : (d.stone.length as number)
}

function resolvedStoneWidth(d: JewelryDefinition): number {
  return roundLike(d) ? (d.stone.diameter as number) : (d.stone.width as number)
}

/** Shapes whose single horizontal size is a diameter. Mirrors `_ROUND_LIKE`. */
function roundLike(d: JewelryDefinition): boolean {
  return d.stone.shape === 'round' || d.stone.shape === 'pearl'
}

/**
 * Whether STONE_DEPTH_RANGE's premise holds for this stone. Mirrors
 * `_stone_depth_rule_applies()` in the backend engine exactly (FORGE-GOV-004).
 *
 * A sphere's depth IS its horizontal extent, so the rule can never pass for a
 * pearl; an imported stone's true dimensions live in the asset, not in the
 * document. Both are skipped rather than evaluated against a dimension the
 * rule does not describe.
 */
function stoneDepthRuleApplies(d: JewelryDefinition): boolean {
  if (d.stone.source === 'IMPORTED_CAD') {
    return false
  }
  if (d.stone.profile === 'SPHERICAL_REFERENCE' || d.stone.shape === 'pearl') {
    return false
  }
  return true
}

/**
 * Gem identity validation. Mirrors
 * `backend/jewelmind/validation/engine.py::_gem_rules()` (FORGE-GOV-004).
 *
 * SCOPE: GEM_IDENTITY_ONLY — referential and coherence invariants only. No
 * gemological or manufacturing claim is made here, and none may be added:
 * hardness, durability, heat sensitivity, setting suitability and treatment
 * safety all require professional evidence this project does not have.
 *
 * THIS MIRROR IS DELIBERATELY A SUBSET, and says so rather than pretending
 * otherwise. The frontend has no copy of the gem registry — the backend is
 * authoritative (brief section 11) — so four of the six rules are
 * BACKEND-ONLY:
 *
 *   JM-GEM-001  entry exists          needs the registry
 *   JM-GEM-002  origin applicable     needs the registry
 *   JM-GEM-004  profile resolves      needs the profile set
 *   JM-GEM-006  entry deprecated      needs the registry
 *
 * What remains needs nothing but the identity itself, and is mirrored exactly.
 * FORGE-GOV-004 permits a mirror to enforce a subset; it must never enforce
 * something the backend does not.
 */
function gemRules(d: JewelryDefinition): ValidationResult[] {
  const out: ValidationResult[] = []
  const gem = d.stone.gem

  // A legacy document with no gem is valid and produces no results.
  if (gem === null || gem === undefined) {
    return out
  }

  if (gem.gemId === 'custom') {
    if (!gem.customName || !gem.customName.trim()) {
      out.push({
        ruleId: RULE_IDS.GEM_CUSTOM_COHERENT,
        severity: 'error',
        message: 'A custom gem requires a name describing the material.',
        parameter: 'stone.gem.customName',
      })
    }
  } else if (gem.customName !== null && gem.customName !== undefined) {
    out.push({
      ruleId: RULE_IDS.GEM_CUSTOM_COHERENT,
      severity: 'error',
      message: `A custom name is only meaningful for a custom gem; '${gem.gemId}' already has a canonical name.`,
      parameter: 'stone.gem.customName',
    })
  }

  const treatments = gem.treatments ?? []
  const seen = new Set<string>()
  for (const treatment of treatments) {
    if (seen.has(treatment.treatment)) {
      out.push({
        ruleId: RULE_IDS.GEM_TREATMENT_COHERENT,
        severity: 'warning',
        message: `Treatment '${treatment.treatment}' is recorded more than once. Duplicate records cannot be reconciled automatically, so both are preserved.`,
        parameter: 'stone.gem.treatments',
      })
    }
    seen.add(treatment.treatment)
  }

  const present = new Set(
    treatments.filter((x) => x.status === 'PRESENT').map((x) => x.treatment),
  )
  const absent = Array.from(
    new Set(treatments.filter((x) => x.status === 'NOT_PRESENT').map((x) => x.treatment)),
  ).sort()
  for (const conflict of absent) {
    if (present.has(conflict)) {
      out.push({
        ruleId: RULE_IDS.GEM_TREATMENT_COHERENT,
        severity: 'error',
        message: `Treatment '${conflict}' is recorded as both present and not present.`,
        parameter: 'stone.gem.treatments',
      })
    }
  }

  return out
}

function stoneRules(d: JewelryDefinition): ValidationResult[] {
  // STONE_DIAMETER_RANGE is ROUND_ONLY; STONE_DEPTH_RANGE is generalized to the
  // stone's real minimum horizontal extent, and is scoped away from spherical
  // and imported stones (Sprint 20). Mirrors
  // backend/jewelmind/validation/engine.py::_stone_rules() exactly
  // (FORGE-GOV-004). See docs/bible/22-stone-v2/code-mapping-and-gaps.md.
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

  if (stoneDepthRuleApplies(d)) {
    const minExtent = Math.min(resolvedStoneLength(d), resolvedStoneWidth(d))
    const depth = d.stone.shape === 'pearl' ? (d.stone.diameter as number) : d.stone.depth
    if (!(depth > 0.5 && depth < minExtent)) {
      out.push({
        ruleId: RULE_IDS.STONE_DEPTH_RANGE,
        severity: 'error',
        message: "Stone depth must be greater than 0.5 mm and lower than the stone's minimum horizontal extent.",
        parameter: 'stone.depth',
      })
    }
  }

  return out
}

// BEZEL_ONLY (Sprint 19). Constructibility invariants only — no minimum
// bezel wall dimension is asserted, because no sourced professional value
// exists and inventing one is forbidden (SETTING-GOV-010).
// PRONG_ONLY (Sprint 19) — mirrors backend/jewelmind/validation/engine.py
// ::_prong_rules exactly (FORGE-GOV-004). Every rule here reads a prong
// field, so none is meaningful for a bezel setting; evaluating them would
// block a valid bezel on setting.prongCount.
// BEZEL_ONLY (Sprint 19). Constructibility invariants only — no minimum
// bezel wall dimension is asserted, because no sourced professional value
// exists and inventing one is forbidden (SETTING-GOV-010).
function bezelRules(d: JewelryDefinition): ValidationResult[] {
  const out: ValidationResult[] = []

  if (d.setting.type !== 'bezel') {
    return out
  }

  if (d.setting.bezelWallThickness <= 0) {
    out.push({
      ruleId: RULE_IDS.BEZEL_WALL_THICKNESS_POSITIVE,
      severity: 'error',
      message: 'Bezel wall thickness must be positive.',
      parameter: 'setting.bezelWallThickness',
    })
  }

  if (d.setting.bezelWallHeight <= 0) {
    out.push({
      ruleId: RULE_IDS.BEZEL_WALL_HEIGHT_POSITIVE,
      severity: 'error',
      message: 'Bezel wall height must be positive.',
      parameter: 'setting.bezelWallHeight',
    })
  }

  return out
}

// PRONG_ONLY (Sprint 19) — mirrors backend/jewelmind/validation/engine.py
// ::_prong_rules exactly (FORGE-GOV-004). Every rule here reads a prong
// field, so none is meaningful for a bezel setting; evaluating them would
// block a valid bezel on setting.prongCount.
function prongRules(d: JewelryDefinition): ValidationResult[] {
  const out: ValidationResult[] = []

  if (d.setting.type !== 'prong') {
    return out
  }

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

/**
 * Arrangement structural validation (Sprint 22).
 *
 * A DELIBERATE SUBSET of `backend/jewelmind/validation/engine.py::_arrangement_rules`,
 * and the boundary is where the resolver is. The frontend checks what it can
 * see locally — duplicate ids, references that name nothing, an unresolvable
 * stone, an ambiguous CENTER — and does NOT reimplement pattern expansion, so
 * `JM-ARRANGE-004` (does the arrangement actually resolve?) and
 * `JM-ARRANGE-006` (the generation notice) are backend-only.
 *
 * A second local resolver would eventually disagree with the real one, and the
 * backend's verdict always wins (FORGE-GOV-004). This mirror never reports
 * something the backend would not.
 */
function arrangementRules(d: JewelryDefinition): ValidationResult[] {
  const out: ValidationResult[] = []
  const arrangement = d.arrangement

  // A design with no arrangement is a single-stone design, not a broken one.
  if (arrangement === null || arrangement === undefined) {
    return out
  }

  const seen = new Set<string>()
  for (const instance of arrangement.instances) {
    if (seen.has(instance.instanceId)) {
      out.push({
        ruleId: RULE_IDS.ARRANGEMENT_INSTANCE_IDS_UNIQUE,
        severity: 'error',
        message:
          `Stone instance id '${instance.instanceId}' is declared more than once. ` +
          'Instance ids are the authoritative identity, so a duplicate makes every ' +
          'reference to it ambiguous.',
        parameter: 'arrangement.instances',
      })
    }
    seen.add(instance.instanceId)
  }

  const groupIds = new Set(arrangement.groups.map((group) => group.groupId))
  for (const instance of arrangement.instances) {
    const groupId = instance.placement.groupId
    if (groupId !== null && groupId !== undefined && !groupIds.has(groupId)) {
      out.push({
        ruleId: RULE_IDS.ARRANGEMENT_REFERENCES_RESOLVE,
        severity: 'error',
        message:
          `Stone instance '${instance.instanceId}' belongs to group '${groupId}', ` +
          'which is not declared in this arrangement.',
        parameter: 'arrangement.instances',
      })
    }
  }

  for (const pattern of arrangement.patterns) {
    if (!seen.has(pattern.sourceInstanceId)) {
      out.push({
        ruleId: RULE_IDS.ARRANGEMENT_REFERENCES_RESOLVE,
        severity: 'error',
        message:
          `Pattern '${pattern.patternId}' repeats stone instance ` +
          `'${pattern.sourceInstanceId}', which is not declared in this arrangement.`,
        parameter: 'arrangement.patterns',
      })
    }
    if (
      pattern.groupId !== null &&
      pattern.groupId !== undefined &&
      !groupIds.has(pattern.groupId)
    ) {
      out.push({
        ruleId: RULE_IDS.ARRANGEMENT_REFERENCES_RESOLVE,
        severity: 'error',
        message:
          `Pattern '${pattern.patternId}' places its members in group ` +
          `'${pattern.groupId}', which is not declared.`,
        parameter: 'arrangement.patterns',
      })
    }
  }

  for (const instance of arrangement.instances) {
    if (instance.stoneRef !== 'primary') {
      out.push({
        ruleId: RULE_IDS.ARRANGEMENT_STONE_REFERENCE_RESOLVES,
        severity: 'warning',
        message:
          `Stone instance '${instance.instanceId}' references stone ` +
          `'${instance.stoneRef}', but this definition declares only the primary ` +
          'stone. No geometry will be built for that instance.',
        parameter: 'arrangement.instances',
      })
    }
  }

  const centers = arrangement.instances
    .filter((instance) => instance.role === 'CENTER')
    .map((instance) => instance.instanceId)
  if (centers.length > 1) {
    out.push({
      ruleId: RULE_IDS.ARRANGEMENT_ROLE_COHERENT,
      severity: 'warning',
      message:
        `${centers.length} stone instances claim the CENTER role ` +
        `(${[...centers].sort().join(', ')}). The lowest id is treated as the ` +
        'primary stone; give the others a different role to make the intent explicit.',
      parameter: 'arrangement.instances',
    })
  }

  return out
}

/**
 * Advanced head and prong validation (Sprint 23).
 *
 * Mirrors `_setting_v2_rules` in full: every check is local and structural, so
 * unlike the arrangement mirror there is no backend-only remainder. The
 * backend's verdict still wins (FORGE-GOV-004).
 */
function settingV2Rules(d: JewelryDefinition): ValidationResult[] {
  const out: ValidationResult[] = []
  const setting = d.setting

  if (setting.headArchitecture === 'PEG_HEAD') {
    const missing: string[] = []
    if (setting.pegDiameter === null || setting.pegDiameter === undefined) {
      missing.push('pegDiameter')
    }
    if (setting.pegHeight === null || setting.pegHeight === undefined) {
      missing.push('pegHeight')
    }
    if (missing.length > 0) {
      out.push({
        ruleId: RULE_IDS.SETTING_HEAD_PARAMETERS_COMPLETE,
        severity: 'error',
        message:
          'A PEG_HEAD requires ' +
          missing.map((name) => `setting.${name}`).join(' and ') +
          '. No default is applied, because an invented peg size would be a ' +
          'construction choice you did not make.',
        parameter: `setting.${missing[0]}`,
      })
    } else {
      for (const [name, value] of [
        ['pegDiameter', setting.pegDiameter],
        ['pegHeight', setting.pegHeight],
      ] as const) {
        if (value !== null && value !== undefined && value <= 0) {
          out.push({
            ruleId: RULE_IDS.SETTING_HEAD_PARAMETERS_COMPLETE,
            severity: 'error',
            message: `setting.${name} must be greater than 0 mm.`,
            parameter: `setting.${name}`,
          })
        }
      }
      if (
        setting.pegHeight !== null &&
        setting.pegHeight !== undefined &&
        setting.pegHeight >= setting.basketHeight
      ) {
        out.push({
          ruleId: RULE_IDS.SETTING_HEAD_PARAMETERS_COMPLETE,
          severity: 'error',
          message:
            `setting.pegHeight (${setting.pegHeight} mm) must be less than ` +
            `setting.basketHeight (${setting.basketHeight} mm); otherwise no ` +
            'head wall remains above the peg.',
          parameter: 'setting.pegHeight',
        })
      }
    }
  }

  // An unread field is reported rather than silently ignored. INFORMATION, not
  // a warning: the design is valid, the value simply has no effect.
  if (setting.type !== 'prong' && setting.prongStyle !== 'ROUND_PRONG') {
    out.push({
      ruleId: RULE_IDS.SETTING_FIELD_APPLICABLE,
      severity: 'information',
      message:
        `setting.prongStyle '${setting.prongStyle}' is not read by a ` +
        `'${setting.type}' setting and has no effect on the generated geometry.`,
      parameter: 'setting.prongStyle',
    })
  }
  if (
    setting.headArchitecture !== 'PEG_HEAD' &&
    ((setting.pegDiameter !== null && setting.pegDiameter !== undefined) ||
      (setting.pegHeight !== null && setting.pegHeight !== undefined))
  ) {
    out.push({
      ruleId: RULE_IDS.SETTING_FIELD_APPLICABLE,
      severity: 'information',
      message:
        'setting.pegDiameter/pegHeight are read only by a PEG_HEAD; this ' +
        `design uses '${setting.headArchitecture}', so they have no effect.`,
      parameter: 'setting.pegDiameter',
    })
  }

  if (setting.seatMode !== 'NONE' && d.stone.source === 'IMPORTED_CAD') {
    out.push({
      ruleId: RULE_IDS.SETTING_SEAT_FEASIBLE,
      severity: 'warning',
      message:
        `Seat relief '${setting.seatMode}' cuts the stone volume out of the ` +
        'metal, which requires the stone to parse as a solid. An imported ' +
        'asset may be a mesh, in which case no relief can be cut and ' +
        'generation will report the failure rather than silently skipping it.',
      parameter: 'setting.seatMode',
    })
  }

  return out
}

export function validateDefinition(definition: JewelryDefinition): ValidationResult[] {
  return [
    ...ringRules(definition),
    ...bandRules(definition),
    ...stoneRules(definition),
    ...gemRules(definition),
    ...arrangementRules(definition),
    ...prongRules(definition),
    ...bezelRules(definition),
    ...settingRules(definition),
    ...settingV2Rules(definition),
    ...manufacturingRules(definition),
    ...geometryRules(definition),
  ]
}

export function hasErrors(results: ValidationResult[]): boolean {
  return results.some((r) => r.severity === 'error')
}
