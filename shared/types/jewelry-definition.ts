/**
 * Canonical JewelryDefinition shape, shared conceptually with the backend's
 * Pydantic schema (backend/jewelmind/domain/schema.py). This file is the
 * single TypeScript source of truth for the frontend; keep it structurally
 * in sync with the backend by hand — there is no codegen step in this
 * milestone (see docs/known-limitations.md).
 *
 * All lengths are millimeters. The backend remains the authoritative
 * validator: this type only describes shape, not the numeric business
 * rules (see docs/validation-rules.md).
 */

export const SCHEMA_VERSION = '0.1.0'

export type BandProfile = 'comfort_fit' | 'flat'
export type StoneShape = 'round'
export type SettingType = 'prong'
export type MetalType =
  | 'yellow_gold_18k'
  | 'white_gold_18k'
  | 'rose_gold_18k'
  | 'platinum'
  | 'silver'
export type ManufacturingMethod = 'lost_wax_casting' | 'direct_resin_printing'
export type RingSizeSystem = 'EU'
export type JewelryCategory = 'ring'
export type JewelryStyle = 'solitaire'

export interface ProjectInfo {
  name: string
  units: 'mm'
}

export interface JewelryInfo {
  category: JewelryCategory
  style: JewelryStyle
}

export interface RingSpec {
  sizeSystem: RingSizeSystem
  size: number
  innerDiameter: number
}

export interface BandSpec {
  width: number
  thickness: number
  profile: BandProfile
}

export interface StoneSpec {
  shape: StoneShape
  diameter: number
  depth: number
}

export interface SettingSpec {
  type: SettingType
  prongCount: number
  prongDiameter: number
  prongHeight: number
  basketHeight: number
}

export interface MaterialSpec {
  metal: MetalType
}

export interface ManufacturingSpec {
  method: ManufacturingMethod
}

export interface PreviewSpec {
  meshTolerance: number
  angularTolerance: number
}

export interface JewelryDefinition {
  schemaVersion: string
  project: ProjectInfo
  jewelry: JewelryInfo
  ring: RingSpec
  band: BandSpec
  stone: StoneSpec
  setting: SettingSpec
  material: MaterialSpec
  manufacturing: ManufacturingSpec
  preview: PreviewSpec
}

const METAL_TYPES: readonly MetalType[] = [
  'yellow_gold_18k',
  'white_gold_18k',
  'rose_gold_18k',
  'platinum',
  'silver',
]
const BAND_PROFILES: readonly BandProfile[] = ['comfort_fit', 'flat']
const MANUFACTURING_METHODS: readonly ManufacturingMethod[] = [
  'lost_wax_casting',
  'direct_resin_printing',
]

function isFiniteNumber(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value)
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

/**
 * Runtime structural check for arbitrary/untrusted data (e.g. a definition
 * loaded from localStorage) before it is trusted as a real
 * JewelryDefinition. Mirrors the backend's strictness intent — reject
 * numeric-looking-but-wrong values (strings, NaN, Infinity), reject an
 * unsupported schemaVersion, reject missing/malformed sections — without
 * needing a validation library. This only checks shape/type, not the
 * business rules in docs/validation-rules.md (those still run afterward,
 * same as for any freshly-edited definition).
 */
export function isValidJewelryDefinition(value: unknown): value is JewelryDefinition {
  if (!isPlainObject(value)) return false
  if (value['schemaVersion'] !== SCHEMA_VERSION) return false

  const project = value['project']
  if (!isPlainObject(project) || typeof project['name'] !== 'string' || project['units'] !== 'mm') {
    return false
  }

  const jewelry = value['jewelry']
  if (!isPlainObject(jewelry) || jewelry['category'] !== 'ring' || jewelry['style'] !== 'solitaire') {
    return false
  }

  const ring = value['ring']
  if (
    !isPlainObject(ring) ||
    ring['sizeSystem'] !== 'EU' ||
    !isFiniteNumber(ring['size']) ||
    !isFiniteNumber(ring['innerDiameter'])
  ) {
    return false
  }

  const band = value['band']
  if (
    !isPlainObject(band) ||
    !isFiniteNumber(band['width']) ||
    !isFiniteNumber(band['thickness']) ||
    !BAND_PROFILES.includes(band['profile'] as BandProfile)
  ) {
    return false
  }

  const stone = value['stone']
  if (
    !isPlainObject(stone) ||
    stone['shape'] !== 'round' ||
    !isFiniteNumber(stone['diameter']) ||
    !isFiniteNumber(stone['depth'])
  ) {
    return false
  }

  const setting = value['setting']
  if (
    !isPlainObject(setting) ||
    setting['type'] !== 'prong' ||
    !isFiniteNumber(setting['prongCount']) ||
    !isFiniteNumber(setting['prongDiameter']) ||
    !isFiniteNumber(setting['prongHeight']) ||
    !isFiniteNumber(setting['basketHeight'])
  ) {
    return false
  }

  const material = value['material']
  if (!isPlainObject(material) || !METAL_TYPES.includes(material['metal'] as MetalType)) {
    return false
  }

  const manufacturing = value['manufacturing']
  if (
    !isPlainObject(manufacturing) ||
    !MANUFACTURING_METHODS.includes(manufacturing['method'] as ManufacturingMethod)
  ) {
    return false
  }

  const preview = value['preview']
  if (
    !isPlainObject(preview) ||
    !isFiniteNumber(preview['meshTolerance']) ||
    preview['meshTolerance'] <= 0 ||
    !isFiniteNumber(preview['angularTolerance']) ||
    preview['angularTolerance'] <= 0
  ) {
    return false
  }

  return true
}

export function createDefaultDefinition(): JewelryDefinition {
  return {
    schemaVersion: SCHEMA_VERSION,
    project: { name: 'Solitaire Ring', units: 'mm' },
    jewelry: { category: 'ring', style: 'solitaire' },
    ring: { sizeSystem: 'EU', size: 16, innerDiameter: 17.8 },
    band: { width: 2.4, thickness: 1.8, profile: 'comfort_fit' },
    stone: { shape: 'round', diameter: 6.5, depth: 4.0 },
    setting: {
      type: 'prong',
      prongCount: 6,
      prongDiameter: 1.1,
      prongHeight: 4.8,
      basketHeight: 3.5,
    },
    material: { metal: 'yellow_gold_18k' },
    manufacturing: { method: 'lost_wax_casting' },
    preview: { meshTolerance: 0.1, angularTolerance: 0.2 },
  }
}
