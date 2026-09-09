/**
 * Frontend mirror of the deterministic validation engine, for instant
 * feedback while the user edits the form. This is NOT authoritative — the
 * backend (backend/jewelmind/validation/engine.py) re-validates every
 * definition before generation and export, and its verdict always wins.
 * Keep the two engines in sync by hand; if they ever disagree, trust the
 * backend response.
 */

import type {
  JewelryDefinition,
  JewelryStyle,
  PaveDefinition,
  SettingType,
} from '../types/jewelry-definition'
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

/**
 * Multi-stone family validation (Sprint 24).
 *
 * A DELIBERATE SUBSET of `_family_rules`, and the boundary is where the
 * compiler is. The frontend checks what it can see locally — one placement
 * authority, valid roles and cardinality, resolvable references — and does NOT
 * reimplement family compilation, so `JM-FAMILY-003` (does it compile?) and
 * `JM-FAMILY-005` (the setting-coverage notice) are backend-only.
 *
 * A second local compiler would eventually disagree with the real one, and the
 * backend's verdict always wins (FORGE-GOV-004).
 */
const FAMILY_ROLE_RULES: Record<string, Record<string, number | null>> = {
  THREE_STONE: { CENTER: 1, SIDE: 2 },
  TOI_ET_MOI: { SIDE: 2 },
  CLUSTER: { CENTER: null, ACCENT: null },
  CENTER_WITH_ACCENTS: { CENTER: 1, ACCENT: null },
}

function familyRules(d: JewelryDefinition): ValidationResult[] {
  const out: ValidationResult[] = []
  const family = d.family

  if (family === null || family === undefined) {
    return out
  }

  if (d.arrangement !== null && d.arrangement !== undefined) {
    out.push({
      ruleId: RULE_IDS.FAMILY_SINGLE_PLACEMENT_AUTHORITY,
      severity: 'error',
      message:
        'This design declares both a family and an explicit arrangement. A ' +
        'family compiles into an arrangement, so only one may be present: ' +
        "remove the arrangement to keep the family's semantics, or remove the " +
        'family for full manual control.',
      parameter: 'family',
    })
    // The conflict must be resolved before anything else is meaningful, and a
    // second derived failure would obscure the real one.
    return out
  }

  const rules = FAMILY_ROLE_RULES[family.familyType] ?? {}
  const counts: Record<string, number> = {}
  for (const member of family.members) {
    counts[member.role] = (counts[member.role] ?? 0) + 1
  }

  for (const role of Object.keys(counts).sort()) {
    if (!(role in rules)) {
      out.push({
        ruleId: RULE_IDS.FAMILY_ROLES_VALID,
        severity: 'error',
        message:
          `Role '${role}' is not part of a ${family.familyType} family. ` +
          `Accepted roles: ${Object.keys(rules).sort().join(', ')}.`,
        parameter: 'family.members',
      })
      continue
    }
    const expected = rules[role]
    if (
      expected !== null &&
      expected !== undefined &&
      counts[role] !== expected &&
      family.members.length > 0
    ) {
      out.push({
        ruleId: RULE_IDS.FAMILY_ROLES_VALID,
        severity: 'error',
        message:
          `A ${family.familyType} family requires exactly ${expected} ` +
          `member(s) with role '${role}', found ${counts[role]}.`,
        parameter: 'family.members',
      })
    }
  }

  for (const member of family.members) {
    if (member.stoneRef !== 'primary') {
      out.push({
        ruleId: RULE_IDS.FAMILY_REFERENCES_RESOLVE,
        severity: 'warning',
        message:
          `Family member '${member.memberId}' references stone ` +
          `'${member.stoneRef}', but this definition declares only the primary ` +
          'stone. No geometry will be built for that member.',
        parameter: 'family.members',
      })
    }
    if (
      member.settingRef !== null &&
      member.settingRef !== undefined &&
      member.settingRef !== d.setting.type
    ) {
      out.push({
        ruleId: RULE_IDS.FAMILY_REFERENCES_RESOLVE,
        severity: 'warning',
        message:
          `Family member '${member.memberId}' requests setting ` +
          `'${member.settingRef}', but this design's setting is ` +
          `'${d.setting.type}'. Per-member settings are not generated: only ` +
          'the primary stone receives one.',
        parameter: 'family.members',
      })
    }
  }

  return out
}

/** Which family types accept a halo that NAMES its centre.
 *
 * A MIRROR of `backend/jewelmind/halo/capability.py::HALO_COMPOSITION`, and a
 * deliberate subset of it: the backend derives the authoritative answer from
 * the real compiled instances, which the client cannot do. A toi-et-moi has no
 * CENTER member — the pair IS the design — so a halo there must anchor on the
 * design origin (`centerMemberId: null`), which encircles both stones. */
const HALO_NAMED_CENTER_SUPPORTED: Record<string, boolean> = {
  THREE_STONE: true,
  TOI_ET_MOI: false,
  CLUSTER: true,
  CENTER_WITH_ACCENTS: true,
}

function haloRules(d: JewelryDefinition): ValidationResult[] {
  const out: ValidationResult[] = []
  const halo = d.halo

  if (halo === null || halo === undefined) {
    return out
  }

  // A family/arrangement conflict is familyRules()'s finding; a second derived
  // failure here would obscure the real one.
  if (
    d.family !== null &&
    d.family !== undefined &&
    d.arrangement !== null &&
    d.arrangement !== undefined
  ) {
    return out
  }

  if (
    d.family !== null &&
    d.family !== undefined &&
    halo.centerMemberId !== null &&
    halo.centerMemberId !== undefined &&
    HALO_NAMED_CENTER_SUPPORTED[d.family.familyType] === false
  ) {
    out.push({
      ruleId: RULE_IDS.HALO_COMPOSITION_SUPPORTED,
      severity: 'error',
      message:
        `A halo cannot name a centre in a ${d.family.familyType} family, ` +
        'which has no CENTER member. Set centerMemberId to null to encircle ' +
        'the whole group instead.',
      parameter: 'halo.centerMemberId',
    })
    return out
  }

  for (const ring of halo.rings) {
    const stoneRefs = new Set<string>([ring.stoneRef])
    for (const member of ring.members) {
      stoneRefs.add(member.stoneRef)
    }
    for (const ref of Array.from(stoneRefs).sort()) {
      if (ref !== 'primary') {
        out.push({
          ruleId: RULE_IDS.HALO_REFERENCES_RESOLVE,
          severity: 'warning',
          message:
            `Halo ring '${ring.ringId}' references stone '${ref}', but this ` +
            'definition declares only the primary stone. No geometry will be ' +
            'built for those halo stones.',
          parameter: 'halo.rings',
        })
      }
    }

    const settingRefs = new Set<string>()
    if (ring.settingRef !== null && ring.settingRef !== undefined) {
      settingRefs.add(ring.settingRef)
    }
    for (const member of ring.members) {
      if (member.settingRef !== null && member.settingRef !== undefined) {
        settingRefs.add(member.settingRef)
      }
    }
    for (const ref of Array.from(settingRefs).sort()) {
      if (ref !== d.setting.type) {
        out.push({
          ruleId: RULE_IDS.HALO_REFERENCES_RESOLVE,
          severity: 'warning',
          message:
            `Halo ring '${ring.ringId}' requests setting '${ref}', but this ` +
            `design's setting is '${d.setting.type}'. No halo setting is ` +
            'generated: only the primary stone receives one.',
          parameter: 'halo.rings',
        })
      }
    }
  }

  return out
}

/** The field's column and row pitch. Mirrors
 * `backend/jewelmind/pave/compile.py::lattice_pitches`. */
function latticePitches(pave: PaveDefinition): [number, number] {
  if (pave.spec.kind === 'PAVE') {
    const pitch = pave.spec.pitchMm
    return [pitch, pave.spec.rowPitchMm ?? pitch]
  }
  const pitch = pave.spec.stoneSpacingMm
  return [pitch, pave.spec.rowSpacingMm ?? pitch]
}

function paveRules(d: JewelryDefinition): ValidationResult[] {
  const out: ValidationResult[] = []
  const pave = d.pave

  if (pave === null || pave === undefined) {
    return out
  }

  if (!pave.enabled) {
    out.push({
      ruleId: RULE_IDS.PAVE_EXECUTION_BOUNDARY,
      severity: 'information',
      message:
        `Pavé '${pave.paveId}' is declared and disabled, so no stones and no ` +
        'retention metal are built. Its parameters are preserved.',
      parameter: 'pave.enabled',
    })
    return out
  }

  if (pave.stoneRef !== 'primary') {
    out.push({
      ruleId: RULE_IDS.PAVE_REFERENCES_RESOLVE,
      severity: 'warning',
      message:
        `Pavé '${pave.paveId}' references stone '${pave.stoneRef}', but this ` +
        'definition declares only the primary stone. No geometry will be ' +
        'built for its stones.',
      parameter: 'pave.stoneRef',
    })
  }

  // PURE ARITHMETIC, and the only numeric pavé rule: stones wider than the
  // pitch between their centres overlap as a matter of geometry. NOT a
  // manufacturing threshold — JewelMind states no minimum pavé spacing.
  const [pitch, rowPitch] = latticePitches(pave)
  // Reuses the existing mirror of `resolved_width_mm` rather than a second
  // copy: the stone's minimum horizontal extent, never a fabricated
  // equivalent diameter.
  const stoneWidth = resolvedStoneWidth(d) ?? null
  if (stoneWidth !== null) {
    const footprint = stoneWidth * pave.stoneScale
    const tightest = Math.min(pitch, rowPitch)
    if (footprint > tightest) {
      out.push({
        ruleId: RULE_IDS.PAVE_PITCH_CONSISTENCY,
        severity: 'warning',
        message:
          `Pavé '${pave.paveId}' sets stones ${footprint.toFixed(3)}mm across ` +
          `at a pitch of ${tightest.toFixed(3)}mm, so adjacent stones overlap ` +
          'as a matter of arithmetic. A GEOMETRIC inconsistency, not a ' +
          'manufacturing threshold: JewelMind states no minimum pavé spacing. ' +
          'Increase the pitch or reduce pave.stoneScale.',
        parameter: 'pave.stoneScale',
      })
    }
  }

  const boundary: string[] = []
  if (pave.retention.strategy === 'NONE') {
    boundary.push(
      "retention is 'NONE', so its stones are built with no metal holding them",
    )
  }
  if (pave.seat.mode === 'NONE') {
    boundary.push(
      'no recess is cut, so its stones sit against the host surface rather ' +
        'than into it',
    )
  }
  const detail = boundary.length > 0 ? ` This field ${boundary.join(', and ')}.` : ''
  out.push({
    ruleId: RULE_IDS.PAVE_EXECUTION_BOUNDARY,
    severity: 'information',
    message:
      `This ${pave.kind} field is set on the ${pave.host} surface.${detail} No ` +
      'pavé dimension, spacing or retention size in JewelMind is ' +
      'professionally validated: a qualified jewelry professional must review ' +
      'this field before production.',
    parameter: 'pave',
  })

  return out
}

/**
 * Which `setting.type` selects each setting-mode family (Sprint 27).
 *
 * A MIRROR of the backend's `PRIMARY_FAMILY_SETTING_TYPE`, kept as a mode-id
 * prefix table rather than a full copy of the mode registry: the family is
 * recoverable from the id, so this needs no per-mode row and cannot drift from
 * one. The backend remains authoritative (FORGE-GOV-004).
 */
const MODE_ID_SETTING_TYPE: Readonly<Record<string, SettingType>> = {
  PRONG: 'prong',
  BEZEL: 'bezel',
  CHANNEL: 'channel',
  BAR: 'bar',
  FLUSH: 'flush',
  TENSION: 'tension',
}

/**
 * Extended Setting Modes validation (Sprint 27) — the mirrored SUBSET.
 *
 * Three checks, each answerable from the document alone. See
 * `shared/validation/rules.ts` for exactly which backend rules are NOT mirrored
 * here and why.
 *
 * NOTHING HERE IS A PROFESSIONAL JUDGMENT. There is no check on whether a
 * channel wall is thick enough or a tension setting safe; JM-SETTING-012 says a
 * professional must LOOK, which is the opposite of a verdict.
 */
function settingModeRules(d: JewelryDefinition): ValidationResult[] {
  const out: ValidationResult[] = []
  const setting = d.setting
  const mode = setting.mode

  if (mode !== null && mode !== undefined && mode.enabled) {
    const family = mode.modeId.split('_')[0] ?? ''
    const expected = MODE_ID_SETTING_TYPE[family]
    if (expected === undefined) {
      // A HEAD or RETENTION mode declared on the PRIMARY axis. The head
      // architecture is chosen by setting.headArchitecture and field retention
      // by the pavé's own strategy; declaring one here would be a second
      // authority over an axis that already has one.
      out.push({
        ruleId: RULE_IDS.SETTING_MODE_FAMILY_MATCHES,
        severity: 'error',
        message:
          `setting.mode '${mode.modeId}' is not a PRIMARY setting mode. The ` +
          'head architecture is chosen by setting.headArchitecture and field ' +
          "retention by the pavé's own retention strategy.",
        parameter: 'setting.mode.modeId',
      })
    } else if (expected !== setting.type) {
      out.push({
        ruleId: RULE_IDS.SETTING_MODE_FAMILY_MATCHES,
        severity: 'error',
        message:
          `setting.mode '${mode.modeId}' belongs to the ${family} family, ` +
          `which is selected by setting.type '${expected}', but setting.type ` +
          `is '${setting.type}'. Refused rather than resolved by precedence: ` +
          'two authorities over one setting have no determinate resolution.',
        parameter: 'setting.mode.modeId',
      })
    }
  }

  // A flush setting's recess IS half its geometry, so relief is a precondition
  // rather than an option: without it the collar occupies the stone's whole
  // volume.
  if (setting.type === 'flush' && setting.seatMode === 'NONE') {
    out.push({
      ruleId: RULE_IDS.SETTING_MODE_REQUIREMENTS_MET,
      severity: 'error',
      message:
        "A flush setting requires setting.seatMode = 'REFERENCE_SEAT'. " +
        "Without the recess the collar occupies the stone's whole volume, and " +
        'the result is a solid mass with the stone buried inside it rather ' +
        'than a flush setting.',
      parameter: 'setting.seatMode',
      suggestedValue: 'REFERENCE_SEAT',
    })
  }

  // The brief's PROFESSIONAL REVIEW category, carried as a warning because the
  // three severities are a published contract.
  if (setting.type === 'tension') {
    out.push({
      ruleId: RULE_IDS.SETTING_MODE_PROFESSIONAL_REVIEW,
      severity: 'warning',
      message:
        'A tension setting requires review by a qualified jewelry ' +
        'professional. JewelMind generates the two opposing supports as real ' +
        'geometry and models none of the structural behaviour that makes a ' +
        'tension setting hold a stone — no force, no spring-back, no ' +
        'retention claim.',
      parameter: 'setting.type',
    })
  }

  return out
}

/**
 * Which family each ring-family variant belongs to (Sprint 28).
 *
 * A MIRROR of the backend's `VARIANT_FAMILY`, kept as a variant-id PREFIX table
 * rather than a per-variant row: the family is recoverable from the id, so this
 * cannot drift from a list of variants the way a full copy would. Reserved
 * variants are absent from the mirrored `RingFamilyVariantId` type, so they can
 * never reach here. The backend remains authoritative (FORGE-GOV-004).
 */
const VARIANT_ID_FAMILY: Readonly<Record<string, JewelryStyle>> = {
  SOLITAIRE: 'solitaire',
  THREE_STONE: 'three_stone',
  HALO: 'halo',
  SPLIT_SHANK: 'split_shank',
  BYPASS: 'bypass',
  SIGNET: 'signet',
}

/** The variant ids of the families whose name is itself two segments, so a
 * single split on `_` would recover `SPLIT` or `THREE` rather than the family.
 * Ordered longest-first so `SPLIT_SHANK` is tried before `SPLIT`. */
const VARIANT_ID_PREFIXES: readonly string[] = Object.keys(VARIANT_ID_FAMILY).sort(
  (a, b) => b.length - a.length,
)

/**
 * Ring Families validation (Sprint 28) — the mirrored SUBSET.
 *
 * Two checks, each answerable from the document alone. See
 * `shared/validation/rules.ts` for exactly which backend rules are NOT mirrored
 * here and why.
 *
 * NOTHING HERE IS A PROFESSIONAL JUDGMENT. There is no check on whether a rail
 * is strong enough, a shoulder castable, a signet table thick enough or a
 * bypass sound. Each needs sourced professional evidence this project does not
 * have, so none exists — on either side of the mirror.
 */
function ringFamilyRules(d: JewelryDefinition): ValidationResult[] {
  const out: ValidationResult[] = []
  const spec = d.ringFamily

  if (spec !== null && spec !== undefined && spec.enabled) {
    const prefix = VARIANT_ID_PREFIXES.find((p) => spec.variant.startsWith(`${p}_`))
    const family = prefix === undefined ? undefined : VARIANT_ID_FAMILY[prefix]
    if (family !== undefined && family !== d.jewelry.style) {
      out.push({
        ruleId: RULE_IDS.RING_FAMILY_VARIANT_MATCHES,
        severity: 'error',
        message:
          `ringFamily.variant '${spec.variant}' belongs to the ${family} ` +
          `family, but jewelry.style is '${d.jewelry.style}'. Refused rather ` +
          'than resolved by precedence: two authorities over one design have ' +
          'no determinate resolution.',
        parameter: 'ringFamily.variant',
      })
    }
  }

  // GEOMETRIC FEASIBILITY, and a MATHEMATICAL CONSTRAINT rather than a
  // threshold: two rails SHARE the band's width, so a separation at or above it
  // leaves no rail between them. Arithmetic, not a statement about how thin a
  // rail may be.
  //
  // Read from `band.architecture`, which is what the builder dispatches on —
  // rather than from the variant, which would need the resolver's own
  // derivation table.
  if (d.band.architecture === 'SPLIT' || d.band.architecture === 'BYPASS') {
    const separation =
      d.band.architecture === 'SPLIT' ? d.band.splitSeparation : d.band.bypassSeparation
    const railWidth = (d.band.width - separation) / 2
    if (railWidth <= 0) {
      out.push({
        ruleId: RULE_IDS.RING_FAMILY_GEOMETRY_FEASIBLE,
        severity: 'error',
        message:
          `A separation of ${separation} mm leaves ${railWidth.toFixed(4)} mm ` +
          `of rail in a ${d.band.width} mm band. The rails share the band's ` +
          'width, so a wider separation narrows them rather than widening the ' +
          'ring.',
        parameter:
          d.band.architecture === 'SPLIT' ? 'band.splitSeparation' : 'band.bypassSeparation',
      })
    }
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
    ...familyRules(definition),
    ...haloRules(definition),
    ...paveRules(definition),
    ...prongRules(definition),
    ...bezelRules(definition),
    ...settingRules(definition),
    ...settingV2Rules(definition),
    ...settingModeRules(definition),
    ...ringFamilyRules(definition),
    ...manufacturingRules(definition),
    ...geometryRules(definition),
  ]
}

export function hasErrors(results: ValidationResult[]): boolean {
  return results.some((r) => r.severity === 'error')
}
