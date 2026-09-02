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
/**
 * Canonical stone CUT identities. Mirrors `StoneShape` in
 * backend/jewelmind/domain/schema.py.
 *
 * A cut, never a gem species: `emerald` is the clipped-corner rectangular
 * outline, and the rhombus is named `lozenge` rather than `diamond`, precisely
 * so a shape ID can never collide with gem identity (STONEV2-GOV-008).
 *
 * `custom` and `imported` are pseudo-shapes for stones with no named cut. They
 * are real members so capability lookups are uniform, and are never offered to
 * a user as cuts to choose from.
 */
export type StoneShape =
  // Stone v1 (Sprint 18)
  | 'round'
  | 'oval'
  | 'pear'
  | 'emerald'
  | 'cushion'
  | 'princess'
  | 'marquise'
  // Stone v2 (Sprint 20) extended cuts
  | 'heart'
  | 'radiant'
  | 'asscher'
  | 'trillion'
  | 'baguette'
  | 'tapered_baguette'
  | 'triangle'
  | 'trapezoid'
  | 'lozenge'
  | 'hexagon'
  | 'kite'
  | 'shield'
  | 'half_moon'
  | 'pearl'
  // Pseudo-shapes for non-native sources
  | 'custom'
  | 'imported'

/** Where a stone's geometry comes from. Mirrors `StoneSourceMode`. */
export type StoneSourceMode =
  | 'PARAMETRIC_REFERENCE'
  | 'CUSTOM_OUTLINE'
  | 'MEASURED'
  | 'IMPORTED_CAD'

/**
 * The 3D reference profile applied to an outline. Independent of `StoneShape`,
 * which is what avoids `OVAL_CABOCHON`-style compound members.
 */
export type StoneReferenceProfile =
  | 'FACETED_REFERENCE'
  | 'CABOCHON_REFERENCE'
  | 'SPHERICAL_REFERENCE'

/** Units a caller may declare for a custom outline or an imported asset. */
export type DeclaredUnit = 'mm' | 'cm' | 'm' | 'in'
export type SettingType = 'prong' | 'bezel'
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

export type BandTaperMode = 'NONE' | 'TOWARD_BOTTOM'

export interface BandTaperSpec {
  mode: BandTaperMode
  bottomRatio: number
}

export interface BandSpec {
  width: number
  thickness: number
  profile: BandProfile
  widthTaper: BandTaperSpec
  thicknessTaper: BandTaperSpec
}

export interface OutlinePoint {
  x: number
  y: number
}

/**
 * A caller-supplied closed stone outline. The outline is closed implicitly —
 * the first point must not be repeated at the end.
 */
export interface CustomOutline {
  points: OutlinePoint[]
  unit: DeclaredUnit
  label: string | null
}

/** Provenance for a physically measured stone. Never filled in by JewelMind. */
export interface StoneMeasurement {
  measurementSource: string | null
  measurementDate: string | null
  operatorNote: string | null
}

/**
 * Reference to externally supplied stone geometry. `assetHash` is a content
 * hash, never a filesystem path, and `declaredUnit` is required rather than
 * inferred — no format JewelMind reads carries a reliable unit.
 */
export interface ImportedStoneAsset {
  assetHash: string
  assetName: string | null
  declaredUnit: DeclaredUnit
}

export interface StoneSpec {
  shape: StoneShape
  diameter: number | null
  length: number | null
  width: number | null
  depth: number
  orientation: number
  /** Narrow-end width of a tapered shape. Required for tapered_baguette/trapezoid. */
  narrowWidth: number | null
  source: StoneSourceMode
  profile: StoneReferenceProfile
  customOutline: CustomOutline | null
  measurement: StoneMeasurement | null
  importedAsset: ImportedStoneAsset | null
}

export interface SettingSpec {
  type: SettingType
  prongCount: number
  prongDiameter: number
  prongHeight: number
  basketHeight: number
  /**
   * Bezel-family parameters (Sprint 19). Present on every definition so the
   * flat JDL shape stays backward compatible; unread when `type === 'prong'`.
   * The defaults are PRELIMINARY SOFTWARE VALUES, not professional
   * recommendations - see docs/bible/21-setting/bezel-setting-contract.md.
   */
  bezelWallThickness: number
  bezelWallHeight: number
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
const SETTING_TYPES: readonly SettingType[] = ['prong', 'bezel']
const STONE_SHAPES: readonly StoneShape[] = [
  'round',
  'oval',
  'pear',
  'emerald',
  'cushion',
  'princess',
  'marquise',
]
const BAND_TAPER_MODES: readonly BandTaperMode[] = ['NONE', 'TOWARD_BOTTOM']
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

function isValidBandTaper(value: unknown): value is BandTaperSpec {
  if (!isPlainObject(value)) return false
  if (!BAND_TAPER_MODES.includes(value['mode'] as BandTaperMode)) return false
  const ratio = value['bottomRatio']
  return isFiniteNumber(ratio) && ratio > 0 && ratio <= 1
}

/**
 * Mirrors the backend's `StoneSpec` model_validator (Sprint 18):
 * `diameter` is required only for `shape === 'round'`; `length`/`width`
 * are required for every other shape.
 */
function isValidStone(value: unknown): value is StoneSpec {
  if (!isPlainObject(value)) return false
  const shape = value['shape']
  if (!STONE_SHAPES.includes(shape as StoneShape)) return false
  if (!isFiniteNumber(value['depth'])) return false
  if (!isFiniteNumber(value['orientation'])) return false

  if (shape === 'round') {
    return isFiniteNumber(value['diameter'])
  }
  return isFiniteNumber(value['length']) && isFiniteNumber(value['width'])
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
    !BAND_PROFILES.includes(band['profile'] as BandProfile) ||
    !isValidBandTaper(band['widthTaper']) ||
    !isValidBandTaper(band['thicknessTaper'])
  ) {
    return false
  }

  if (!isValidStone(value['stone'])) {
    return false
  }

  const setting = value['setting']
  if (
    !isPlainObject(setting) ||
    !SETTING_TYPES.includes(setting['type'] as SettingType) ||
    !isFiniteNumber(setting['prongCount']) ||
    !isFiniteNumber(setting['prongDiameter']) ||
    !isFiniteNumber(setting['prongHeight']) ||
    !isFiniteNumber(setting['basketHeight']) ||
    !isFiniteNumber(setting['bezelWallThickness']) ||
    !isFiniteNumber(setting['bezelWallHeight'])
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
    band: {
      width: 2.4,
      thickness: 1.8,
      profile: 'comfort_fit',
      widthTaper: { mode: 'NONE', bottomRatio: 1.0 },
      thicknessTaper: { mode: 'NONE', bottomRatio: 1.0 },
    },
    stone: {
      shape: 'round',
      diameter: 6.5,
      length: null,
      width: null,
      depth: 4.0,
      orientation: 0.0,
      narrowWidth: null,
      source: 'PARAMETRIC_REFERENCE',
      profile: 'FACETED_REFERENCE',
      customOutline: null,
      measurement: null,
      importedAsset: null,
    },
    setting: {
      type: 'prong',
      prongCount: 6,
      prongDiameter: 1.1,
      prongHeight: 4.8,
      basketHeight: 3.5,
      bezelWallThickness: 0.6,
      bezelWallHeight: 2.5,
    },
    material: { metal: 'yellow_gold_18k' },
    manufacturing: { method: 'lost_wax_casting' },
    preview: { meshTolerance: 0.1, angularTolerance: 0.2 },
  }
}
