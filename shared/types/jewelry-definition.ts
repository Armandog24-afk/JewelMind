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
/**
 * The public setting family. Sprint 27 added the four Extended Setting Modes
 * families, each backed by a real registered backend generator.
 *
 * A MIRROR of `backend/jewelmind/domain/schema.py::SettingType`: this file
 * must never offer a family the backend cannot build.
 */
export type SettingType =
  | 'prong'
  | 'bezel'
  | 'channel'
  | 'bar'
  | 'flush'
  | 'tension'
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

/**
 * Gem identity vocabularies. Mirrors `backend/jewelmind/gem/models.py`.
 *
 * The backend registry is authoritative: the frontend must never define its own
 * gem entries, only reference IDs the backend already knows (brief section 11).
 */

/** What a gem material fundamentally is. `ORGANIC` exists because not every gem
 * is a mineral — a pearl has no species or variety. */
export type GemMaterialClass =
  | 'MINERAL'
  | 'ORGANIC'
  | 'NON_MINERAL'
  | 'COMPOSITE'
  | 'UNKNOWN'

/**
 * How the gem came to exist. Independent of treatment, and deliberately not a
 * boolean: a stone may be natural AND treated, or synthetic AND untreated.
 *
 * `SIMULANT` is its own value because a simulant must never identify as the
 * material it imitates — cubic zirconia is not diamond.
 */
export type GemOrigin =
  | 'NATURAL'
  | 'SYNTHETIC'
  | 'SIMULANT'
  | 'COMPOSITE'
  | 'UNKNOWN'

/** Treatment types. NOT an exhaustive list; `OTHER` carries a note. */
export type GemTreatmentType =
  | 'HEAT'
  | 'IRRADIATION'
  | 'FRACTURE_FILLING'
  | 'GLASS_FILLING'
  | 'COATING'
  | 'DIFFUSION'
  | 'DYEING'
  | 'IMPREGNATION'
  | 'RESIN_IMPREGNATION'
  | 'BLEACHING'
  | 'LASER_DRILLING'
  | 'HPHT'
  | 'OTHER'
  | 'UNKNOWN'

/** `NOT_PRESENT` is a real state: an explicit "not heated" is different
 * information from "we do not know". */
export type GemTreatmentStatus = 'PRESENT' | 'NOT_PRESENT' | 'SUSPECTED' | 'UNKNOWN'

/** Who made the treatment claim. JewelMind never invents a disclosure
 * requirement; this only records the source. */
export type GemTreatmentDisclosure =
  | 'USER_DECLARED'
  | 'VENDOR_DECLARED'
  | 'LAB_REPORT_CLAIMED'
  | 'UNDISCLOSED'
  | 'UNKNOWN'

export type GemConfidence = 'HIGH' | 'MEDIUM' | 'LOW' | 'UNKNOWN'

/** Registry entry lifecycle. A DEPRECATED entry stays resolvable. */
export type GemEntryStatus = 'CURRENT' | 'DEPRECATED' | 'CUSTOM' | 'UNKNOWN'

export type GemDataProvenance =
  | 'INTERNAL_TAXONOMY'
  | 'SOURCED'
  | 'USER_AUTHORED'
  | 'PRELIMINARY'
  | 'PROFESSIONALLY_VALIDATED'
  | 'UNKNOWN'

/** A rendering CATEGORY, never an optical claim. */
export type GemRenderCategory =
  | 'TRANSPARENT_BRILLIANT'
  | 'TRANSPARENT_COLOURED'
  | 'TRANSLUCENT'
  | 'OPAQUE'
  | 'IRIDESCENT'
  | 'PEARLESCENT'
  | 'FALLBACK'

export interface GemTreatment {
  treatment: GemTreatmentType
  status: GemTreatmentStatus
  disclosure: GemTreatmentDisclosure
  confidence: GemConfidence
  note: string | null
}

/**
 * What gem THIS stone is. Separate from every geometry field: a round stone is
 * not automatically a diamond, and the same geometry is reusable with any gem.
 *
 * `null` on a legacy document, which normalizes to `unknown` — never to
 * diamond.
 */
export interface GemIdentity {
  gemId: string
  origin: GemOrigin
  /** An EMPTY list means no treatment is RECORDED, not that the stone is
   * untreated. To assert that, record one with status `NOT_PRESENT`. */
  treatments: GemTreatment[]
  visualProfileId: string | null
  /** Required for, and only valid for, `gemId === 'custom'`. */
  customName: string | null
  note: string | null
}

/**
 * How a gem is rendered. EVERY VALUE IS A RENDERING PARAMETER, NOT A
 * MEASUREMENT — `ior` is what a renderer is handed, not a laboratory refractive
 * index, and `dispersion` drives a sparkle effect rather than describing real
 * spectral separation.
 */
export interface GemVisualProfile {
  profileId: string
  renderCategory: GemRenderCategory
  baseColor: string
  metalness: number
  roughness: number
  opacity: number
  transmission: number
  ior: number
  thickness: number
  clearcoat: number
  envMapIntensity: number
  dispersion: number
  hasVariableColour: boolean
  isFallback: boolean
  description: string
}

/** A registry entry: one KIND of gem. Type-level only — it says what a ruby is,
 * never whether a particular ruby was heated. */
export interface GemDefinition {
  gemId: string
  canonicalName: string
  displayNames: Record<string, string>
  materialClass: GemMaterialClass
  family: string | null
  species: string | null
  variety: string | null
  applicableOrigins: GemOrigin[]
  aliases: string[]
  defaultVisualProfileId: string
  status: GemEntryStatus
  provenance: GemDataProvenance
  supersededBy: string | null
  description: string
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
  /**
   * The gem this stone is made of (Sprint 21). `null` on any document written
   * before Sprint 21, which normalizes to `unknown` — never to diamond.
   *
   * Deliberately NOT a geometry field: the backend's `geometry_hash` excludes
   * it, so changing Diamond -> Sapphire reuses the built geometry.
   */
  gem: GemIdentity | null
}

export interface SettingSpec {
  type: SettingType
  prongCount: number
  prongDiameter: number
  prongHeight: number
  basketHeight: number

  /** Sprint 23. Each defaults to the pre-Sprint-23 behaviour, so a stored
   * design saved before this sprint behaves identically. */
  prongStyle: ProngStyle
  headArchitecture: HeadArchitecture
  seatMode: SeatMode
  prongTipRatio: number
  headBaseRatio: number
  /** Required by, and only read by, `PEG_HEAD`. Deliberately not defaulted to
   * a number: an invented peg size would be a construction choice the user
   * never made. */
  pegDiameter: number | null
  pegHeight: number | null
  /**
   * Bezel-family parameters (Sprint 19). Present on every definition so the
   * flat JDL shape stays backward compatible; unread when `type === 'prong'`.
   * The defaults are PRELIMINARY SOFTWARE VALUES, not professional
   * recommendations - see docs/bible/21-setting/bezel-setting-contract.md.
   */
  bezelWallThickness: number
  bezelWallHeight: number

  /**
   * Sprint 27. Window parameters, required by and only read by `OPEN_GALLERY`.
   *
   * Flat fields beside the other head parameters, deliberately: the head is its
   * own axis, already selected by `headArchitecture`, so putting them inside
   * `mode` — which declares the PRIMARY mode — would make one field carry two
   * axes.
   */
  galleryWindowCount: number
  galleryWindowSweep: number
  galleryWindowHeightFraction: number

  /**
   * The extended setting mode this design declares (Sprint 27).
   *
   * `null` means "no mode declared", which resolves to the variant the existing
   * `type`/`prongStyle` fields already meant — so a design saved before this
   * sprint behaves identically.
   *
   * It REFINES `type`, it does not compete with it: a mode whose family
   * disagrees with `type` is refused by the backend's `JM-SETTING-008` rather
   * than resolved by precedence.
   */
  mode: SettingModeSpec | null
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

/** A stone's semantic role in a design. Mirrors
 * `backend/jewelmind/gem/models.py::StoneRole`. */
export type StoneRole = 'CENTER' | 'SIDE' | 'ACCENT' | 'HALO' | 'PAVE' | 'UNKNOWN'

/**
 * Stone Arrangement Engine v1 (Sprint 22). Mirrors
 * `backend/jewelmind/arrangement/models.py`.
 *
 * A MIRROR, with the usual obligation: the backend is authoritative, and this
 * file must never describe a placement mode, pattern kind or relation the
 * backend cannot resolve. Resolution itself is deliberately NOT mirrored — the
 * frontend reads a resolved arrangement from the backend rather than expanding
 * patterns locally, because two implementations of the same arithmetic
 * eventually disagree and the disagreement shows up as a preview that does not
 * match the exported model.
 */

/** How an instance's placement is expressed. Every mode resolves to
 * `EXPLICIT`, so a consumer of a RESOLVED arrangement never interprets one. */
export type PlacementMode = 'EXPLICIT' | 'PATTERN_MEMBER' | 'RELATIVE'

/** The frame a placement's coordinates are measured in. */
export type PlacementFrame = 'DESIGN_ORIGIN' | 'PARENT_GROUP'

/** Pattern kinds. Each is a closed-form generator, evaluated directly. */
export type ArrangementPatternKind = 'LINEAR' | 'RADIAL' | 'MIRROR'

/** The plane a MIRROR pattern reflects across, named by its normal axis. */
export type MirrorPlane = 'YZ' | 'XZ'

/** Relationship kinds. DECLARATIONS that survive editing, never constraints
 * something solves — nothing moves an instance to satisfy one. */
export type ArrangementRelationKind =
  | 'MIRRORED_PAIR'
  | 'ALIGNED_WITH'
  | 'EVENLY_SPACED_WITH'
  | 'CONCENTRIC_WITH'
  | 'SHARES_TRANSFORM_WITH'

/** Whether a resolved instance actually became geometry. The honest reporting
 * channel for the current execution boundary: multi-stone geometry is PARTIAL,
 * so an instance the pipeline did not build says so and says why. */
export type InstanceGenerationStatus = 'GENERATED' | 'NOT_GENERATED'

/** An instance's rigid placement: a translation plus a complete orientation.
 *
 * `rotationDeg` spins the instance about its own axis; `tiltDeg`/
 * `tiltAzimuthDeg` tip that axis away from vertical and say which way it leans
 * (Sprint 26, ADR-011). Together they are ZXZ Euler angles. Both tilt fields
 * are `0` on every pre-Sprint-26 document, which is the identity.
 *
 * Millimetres and degrees, like everything else. */
export interface InstanceTransform {
  xMm: number
  yMm: number
  zMm: number
  rotationDeg: number
  tiltDeg: number
  tiltAzimuthDeg: number
}

export interface InstancePlacement {
  mode: PlacementMode
  frame: PlacementFrame
  transform: InstanceTransform
  groupId: string | null
}

/** The EXPLICITLY supported per-instance deviations. A closed set: an instance
 * may scale and rotate itself and nothing else, because overriding the shape
 * would make the stone reference meaningless. `null` means inherit. */
export interface InstanceOverrides {
  scale: number | null
  orientationDeg: number | null
}

/** One occurrence of a stone. References the stone and gem rather than
 * restating them — two accents cut from one specification are two occurrences
 * of one stone, not two stones that happen to match. */
export interface StoneInstanceDef {
  instanceId: string
  stoneRef: string
  role: StoneRole
  placement: InstancePlacement
  overrides: InstanceOverrides
  gem: GemIdentity | null
  sourcePatternId: string | null
}

export interface ArrangementGroup {
  groupId: string
  label: string | null
  transform: InstanceTransform
}

export interface LinearPatternSpec {
  kind: 'LINEAR'
  count: number
  spacingMm: number
  directionDeg: number
  centered: boolean
}

export interface RadialPatternSpec {
  kind: 'RADIAL'
  count: number
  radiusMm: number
  startAngleDeg: number
  sweepDeg: number
  alignToRadius: boolean
}

export interface MirrorPatternSpec {
  kind: 'MIRROR'
  plane: MirrorPlane
  mirrorOrientation: boolean
}

export type ArrangementPatternSpec =
  | LinearPatternSpec
  | RadialPatternSpec
  | MirrorPatternSpec

export interface ArrangementPattern {
  patternId: string
  sourceInstanceId: string
  spec: ArrangementPatternSpec
  memberRole: StoneRole
  groupId: string | null
}

export interface ArrangementRelation {
  relationId: string
  kind: ArrangementRelationKind
  members: string[]
  note: string | null
}

/** The declarative arrangement. ABSENT IS NOT EMPTY: a definition with no
 * arrangement is a single-stone design and behaves exactly as before, which is
 * why the field is nullable rather than defaulting to one instance. */
export interface ArrangementDefinition {
  instances: StoneInstanceDef[]
  groups: ArrangementGroup[]
  patterns: ArrangementPattern[]
  relations: ArrangementRelation[]
}

/** One instance after resolution: an explicit position in the design frame,
 * plus whether geometry was built for it. */
export interface ResolvedInstance {
  instanceId: string
  stoneRef: string
  role: StoneRole
  transform: InstanceTransform
  overrides: InstanceOverrides
  gem: GemIdentity | null
  sourcePatternId: string | null
  groupId: string | null
  generationStatus: InstanceGenerationStatus
  generationNote: string | null
  componentName: string | null
}

/** The resolved arrangement a consumer reads. `arrangementFingerprint` is
 * SEPARATE from `definitionHash`: the same arrangement in two different rings
 * has one fingerprint and two definition hashes. */
export interface ResolvedArrangement {
  instances: ResolvedInstance[]
  relations: ArrangementRelation[]
  arrangementFingerprint: string
  resolverVersion: string
  instanceCount: number
  generatedCount: number
  patternExpandedCount: number
  notes: string[]
}

/**
 * Setting System v2 vocabularies (Sprint 23). Mirrors
 * `backend/jewelmind/setting/models.py`.
 *
 * A MIRROR: the backend is authoritative, and this file must never offer a
 * style or architecture the backend has no builder for. `TRELLIS` is
 * deliberately absent from `HeadArchitecture` for exactly that reason.
 */

/** Prong body styles with a real builder. `ROUND_PRONG` is the pre-Sprint-23
 * cylinder and remains the default, so existing designs are unchanged. */
export type ProngStyle =
  | 'ROUND_PRONG'
  | 'CLAW_PRONG'
  | 'V_PRONG'
  | 'TAPERED_PRONG'

/** The structure between the top of the band and the stone. The generated
 * component is named `basket_support` for EVERY architecture — the name is a
 * structural role, and the architecture is reported separately. */
export type HeadArchitecture =
  | 'BASKET'
  | 'PEG_HEAD'
  | 'MARTINI'
  | 'TULIP'
  /** Sprint 27. The basket wall with evenly spaced windows pierced through it.
   * Deliberately NOT called azure: azure work is arbitrary decorative
   * piercing, and this is the parametric subset of it. */
  | 'OPEN_GALLERY'

/** Whether metal is relieved where the stone sits.
 *
 * `REFERENCE_SEAT` CUTS the stone volume out of the metal — never a fuse, so
 * the stone is never part of the production body. It is reference relief, not
 * a setter's seat with a bearing shoulder. */
export type SeatMode = 'NONE' | 'REFERENCE_SEAT'

/**
 * Extended Setting Modes v1 (Sprint 27). Mirrors
 * `backend/jewelmind/setting/modes.py`.
 *
 * A MIRROR: the backend is authoritative, and this file must never offer a mode
 * the backend has no builder for. Every reserved mode — `HEAD_TRELLIS`,
 * `HEAD_AZURE`, `RETENTION_CHANNEL`, `TENSION_COMPRESSION_MODELLED` and the
 * rest — is deliberately absent for exactly that reason. See
 * `RESERVED_SETTING_MODES` for each one's real technical reason.
 */

/** Every setting mode with a real builder behind it. */
export type SettingModeId =
  // PRIMARY — how the design's own stone is held.
  | 'PRONG_ROUND'
  | 'PRONG_TAPERED'
  | 'PRONG_CLAW'
  | 'PRONG_V'
  | 'PRONG_SHARED'
  | 'BEZEL_FULL'
  | 'BEZEL_PARTIAL'
  | 'CHANNEL_LINEAR'
  | 'BAR_TRANSVERSE'
  | 'FLUSH_GYPSY'
  | 'TENSION_OPPOSED'
  // HEAD — what the setting rises from.
  | 'HEAD_BASKET'
  | 'HEAD_PEG'
  | 'HEAD_MARTINI'
  | 'HEAD_TULIP'
  | 'HEAD_OPEN_GALLERY'
  // RETENTION — how a field of small stones is held.
  | 'RETENTION_BEAD'
  | 'RETENTION_SHARED_BEAD'
  | 'RETENTION_MICRO_PRONG'
  | 'RETENTION_SHARED_PRONG'

/** How a channel or bar run ends. Neither is a professional statement about
 * how a setter finishes an edge; both are deterministic construction rules. */
export type SettingTerminationMode = 'OPEN' | 'CLOSED_ENDS'

/** Whether a run is centred on the stone or starts at it. A real geometric
 * difference, read by the CHANNEL and BAR modes. */
export type SettingModeSymmetry = 'SYMMETRIC' | 'ASYMMETRIC'

/** Which structure a mode attaches to. `HEAD` is the attachment plane the
 * category integration supplies — the only host the current families use. */
export type SettingModeHost = 'HEAD'

/**
 * Construction parameters for a setting mode.
 *
 * ONE FLAT MODEL rather than a discriminated union, mirroring the backend: a
 * discriminated union cannot be reached by a dotted-path patch, which is the
 * defect Sprint 26 hit when Designer could not create a pavé. A field a mode
 * does not read is reported as an INFORMATION result by `JM-SETTING-009`
 * rather than silently ignored.
 *
 * EVERY DEFAULT IS A CONSTRUCTION PARAMETER, never a professional
 * recommendation, a minimum, or a manufacturing tolerance.
 */
export interface SettingModeParameters {
  /** BEZEL_PARTIAL. */
  openingCount: number
  openingSweepDeg: number
  openingStartAngleDeg: number
  /** FLUSH_GYPSY. `rimHeightMm` must stay below the stone's crown height — a
   * geometric precondition, not a setting depth. */
  collarWidthMm: number
  rimHeightMm: number
  /** TENSION_OPPOSED. `padDepthMm` is a geometric robustness overlap, never a
   * grip depth: no structural behaviour is modelled. */
  gripAxisDeg: number
  padWidthMm: number
  padThicknessMm: number
  padDepthMm: number
  gripHeightMm: number
  /** CHANNEL_LINEAR and BAR_TRANSVERSE. A `null` extent means "the stone's own
   * measured extent", resolved by the backend generator. */
  axisDeg: number
  spanMm: number | null
  innerWidthMm: number | null
  wallThicknessMm: number
  wallHeightMm: number
  barCount: number
  barSpacingMm: number | null
  barHeightMm: number
  barLengthMm: number | null
  termination: SettingTerminationMode
  /** Shared. */
  symmetry: SettingModeSymmetry
  offsetXMm: number
  offsetYMm: number
  offsetZMm: number
}

/** A setting mode as a document declares it. */
export interface SettingModeSpec {
  modeId: SettingModeId
  /** `false` keeps the parameters in the document and falls back to the
   * family's default variant — a different state from declaring no mode. */
  enabled: boolean
  stoneRef: string
  /** Which arrangement instances this mode holds, when it holds more than the
   * design's own stone. Opaque ids: the arrangement stays the authority on
   * where those instances are. */
  arrangementInstanceIds: string[]
  host: SettingModeHost
  parameters: SettingModeParameters
  label: string | null
}

/**
 * Multi-Stone Families v1 (Sprint 24). Mirrors
 * `backend/jewelmind/family/models.py`.
 *
 * A MIRROR: the backend is authoritative, and this file must never offer a
 * family type the backend has no compiler for. `pave`, `eternity` and `bypass`
 * are deliberately absent for exactly that reason.
 *
 * A halo is absent from this list too, but for a different reason since
 * Sprint 25: it is not a family at all. A halo COMPOSES onto whatever placement
 * a design declares, so it lives beside `family` as its own `HaloDefinition`
 * rather than as a fifth family type. See `docs/bible/27-halo/halo-rfc.md`.
 *
 * A family describes SEMANTIC STRUCTURE. It compiles into an arrangement, which
 * remains the placement authority, and it never restates what a stone is or
 * what it is made of.
 */

/** Families with a real compiler. */
export type FamilyType =
  | 'THREE_STONE'
  | 'TOI_ET_MOI'
  | 'CLUSTER'
  | 'CENTER_WITH_ACCENTS'

/** Whether secondary members mirror about the design axis or are placed from
 * their own values. */
export type FamilySymmetry = 'SYMMETRIC' | 'ASYMMETRIC'

/** One participating stone, by role. Everything about what the stone IS lives
 * elsewhere: `stoneRef` names the specification, `gem` names the material. */
export interface FamilyMember {
  memberId: string
  role: StoneRole
  stoneRef: string
  gem: GemIdentity | null
  scale: number | null
  orientationDeg: number | null
  /** Reuses the arrangement's own transform rather than declaring a second
   * one — the value IS an arrangement transform. */
  placementOverride: InstanceTransform | null
  /** A REQUEST, not an implementation. Only the primary stone receives a
   * setting today. */
  settingRef: string | null
}

export interface ThreeStoneParams {
  kind: 'THREE_STONE'
  sideSpacingMm: number
  sideScale: number
  symmetry: FamilySymmetry
}

export interface ToiEtMoiParams {
  kind: 'TOI_ET_MOI'
  separationMm: number
  axisAngleDeg: number
  symmetry: FamilySymmetry
}

export interface ClusterParams {
  kind: 'CLUSTER'
  count: number
  radiusMm: number
  /** `null` means circular. A cluster is not necessarily circular. */
  radiusYMm: number | null
  startAngleDeg: number
  sweepDeg: number
  includeCenter: boolean
  memberScale: number
  alignToRadius: boolean
}

export interface CenterWithAccentsParams {
  kind: 'CENTER_WITH_ACCENTS'
  accentCount: number
  accentRadiusMm: number
  accentStartAngleDeg: number
  accentSweepDeg: number
  accentScale: number
  symmetry: FamilySymmetry
}

export type FamilyParams =
  | ThreeStoneParams
  | ToiEtMoiParams
  | ClusterParams
  | CenterWithAccentsParams

/** A multi-stone design's semantic structure.
 *
 * ABSENT IS NOT EMPTY: a definition with no family is a single-stone design and
 * behaves exactly as it did before this sprint. */
export interface FamilyDefinition {
  familyType: FamilyType
  params: FamilyParams
  members: FamilyMember[]
  label: string | null
}

/**
 * Halo System v1 (Sprint 25). Mirrors `backend/jewelmind/halo/models.py`.
 *
 * A MIRROR: the backend is authoritative, and this file must never offer a
 * variant the backend has no compiler for. `cushion_halo`, `floral_halo`,
 * `compass_halo`, `triple_halo` and `pave_halo` are deliberately absent —
 * each is reserved with a real reason in
 * `backend/jewelmind/halo/capability.py::RESERVED_HALO_VARIANTS`.
 */

/** Halo variants with a real compiler.
 *
 * `HIDDEN` is a structural claim, not a label: its ring must be offset BELOW
 * the centre plane, which the backend enforces. */
export type HaloVariant = 'SINGLE' | 'DOUBLE' | 'HIDDEN'

/** One concentric ring of stones.
 *
 * The ring is the unit a designer specifies; every stone in it still becomes a
 * separately identifiable arrangement instance. `members` overrides the
 * individual stones that differ, and reuses `FamilyMember` rather than
 * declaring a parallel member model. */
export interface HaloRing {
  ringId: string
  count: number
  /** A POSITION parameter, never a clearance: this layer knows no stone's
   * size, so it cannot claim two stones do not touch. */
  radiusMm: number
  /** `null` means circular. A second semi-axis gives an elliptical halo. */
  radiusYMm: number | null
  startAngleDeg: number
  /** Under 360 lays the ring on an arc — a partial halo. */
  sweepDeg: number
  /** What makes a hidden halo real rather than a label: it reaches the stone
   * solid through the arrangement's own transform. */
  zOffsetMm: number
  memberScale: number
  alignToRadius: boolean
  stoneRef: string
  gem: GemIdentity | null
  /** A REQUEST, not an implementation. No halo metal is generated today. */
  settingRef: string | null
  members: FamilyMember[]
}

/** A halo around a centre.
 *
 * ABSENT IS NOT EMPTY: a definition with no halo behaves exactly as it did
 * before this sprint. */
export interface HaloDefinition {
  variant: HaloVariant
  rings: HaloRing[]
  /** `null` anchors the halo on the design origin, which is how it encircles a
   * multi-stone centre. A named value must exist in the arrangement the halo
   * composes onto; the backend refuses it otherwise (`JM-HALO-001`) rather
   * than silently re-anchoring. */
  centerMemberId: string | null
  label: string | null
}

/**
 * Pavé & Microsetting Engine v1 (Sprint 26). Mirrors
 * `backend/jewelmind/pave/models.py`.
 *
 * A MIRROR: the backend is authoritative, and this file must never offer a
 * host, pattern or retention strategy the backend has no builder for.
 * `SETTING_SURFACE`, `BAND_INNER`, `BAND_SIDE`, `CUSTOM_SURFACE` and
 * `PRONG_SURFACE` are deliberately absent as hosts, and `SHARED_PRONG`,
 * `CHANNEL`, `GRAIN` and `THREAD_SET` as strategies — each is reserved with a
 * real reason in `backend/jewelmind/pave/capability.py`.
 */

/** The two first-class field kinds.
 *
 * `PAVE` populates a surface region at a pitch: the designer gives the area and
 * the density and the count follows. `MICROSETTING` states rows, columns and
 * spacings: the designer gives the structure and the area follows. */
export type PaveKind = 'PAVE' | 'MICROSETTING'

/** Host surfaces with a real resolver. Only these two.
 *
 * A halo plane is NOT among them: a halo has no metal, so a pavé there would
 * have nothing to fuse its beads into. */
export type PaveHost = 'BAND_OUTER' | 'HEAD_PLANE'

export type PavePattern = 'GRID' | 'STAGGERED' | 'ROW_OFFSET' | 'RADIAL' | 'EXPLICIT'

/** Retention strategies with a real builder. `NONE` is an explicit choice
 * (a stone field with no metal), not a missing capability.
 *
 * Sprint 27 added `SHARED_PRONG`: a micro prong at each SHARED lattice corner,
 * serving every stone that touches it. Sharing is a property of the anchor set
 * rather than of the solid, which is why it reaches the same builder
 * `MICRO_PRONG` does — exactly as `BEAD` and `SHARED_BEAD` already do. `CHANNEL`
 * remains absent: a rail runs the whole row, and these anchors are corners. */
export type PaveRetentionStrategy =
  | 'NONE'
  | 'BEAD'
  | 'SHARED_BEAD'
  | 'MICRO_PRONG'
  | 'SHARED_PRONG'

export type PaveContainmentPolicy = 'CLIP' | 'REJECT'
export type PaveTermination = 'FULL_STONES' | 'CENTERED'
export type PaveSymmetry = 'SYMMETRIC' | 'ASYMMETRIC'

/** How metal holds the field's stones. Every dimension is a CONSTRUCTION
 * parameter: JewelMind states no minimum bead size and none is enforced. */
export interface PaveRetention {
  strategy: PaveRetentionStrategy
  beadRadiusMm: number
  beadEmbedMm: number
  prongHeightMm: number
}

/** Whether the host metal is recessed for the stones. A CUT, never a fuse.
 * Deliberately not called a seat: it has no bearing shoulder. */
export interface PaveSeat {
  mode: 'NONE' | 'REFERENCE_RECESS'
  clearanceMm: number
}

/** One stone placed by the document rather than by the pattern. Reuses the
 * arrangement's own transform. */
export interface PaveExplicitPlacement {
  placementId: string
  transform: InstanceTransform
  gem: GemIdentity | null
  scale: number | null
}

export interface PaveSpec {
  kind: 'PAVE'
  angularSpanDeg: number
  startAngleDeg: number
  /** `null` means the host's own full extent, resolved by the backend. */
  axialSpanMm: number | null
  /** A POSITION parameter, never a clearance. */
  pitchMm: number
  rowPitchMm: number | null
  rowCount: number
  pattern: PavePattern
  rowOffsetFraction: number
  termination: PaveTermination
  symmetry: PaveSymmetry
}

export interface MicrosettingSpec {
  kind: 'MICROSETTING'
  columnCount: number
  rowCount: number
  stoneSpacingMm: number
  rowSpacingMm: number | null
  startAngleDeg: number
  axialOffsetMm: number
  pattern: PavePattern
  rowOffsetFraction: number
  termination: PaveTermination
  symmetry: PaveSymmetry
}

export type PaveFieldSpec = PaveSpec | MicrosettingSpec

/** A pavé or microsetting field.
 *
 * ABSENT IS NOT EMPTY, and `enabled: false` is a third state again: it keeps
 * the parameters and builds nothing, which is how a field is switched off
 * without losing how it was configured. */
export interface PaveDefinition {
  paveId: string
  enabled: boolean
  kind: PaveKind
  spec: PaveFieldSpec
  host: PaveHost
  stoneRef: string
  stoneScale: number
  stoneOrientationDeg: number
  gem: GemIdentity | null
  retention: PaveRetention
  seat: PaveSeat
  containment: PaveContainmentPolicy
  explicitPlacements: PaveExplicitPlacement[]
  label: string | null
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

  /** Multiple stone occurrences and their relationships (Sprint 22).
   *
   * `null` on every pre-Sprint-22 document, and that is deliberate: defaulting
   * it to a one-instance arrangement would give every stored design an
   * arrangement it never declared, changing its `definitionHash`. */
  arrangement: ArrangementDefinition | null

  /** The design's multi-stone family (Sprint 24).
   *
   * `null` on every pre-Sprint-24 document. A family compiles into an
   * arrangement, so declaring both is refused by the backend
   * (`JM-FAMILY-001`) rather than merged. */
  family: FamilyDefinition | null

  /** The design's halo (Sprint 25).
   *
   * `null` on every pre-Sprint-25 document. A halo COMPOSES onto whatever
   * placement the design declares — a family, an arrangement, or neither — so
   * it sits beside them rather than inside either. */
  halo: HaloDefinition | null

  /** The design's pavé or microsetting field (Sprint 26).
   *
   * `null` on every pre-Sprint-26 document. ONE field, not a list: two fields
   * in one document needs a rule for what happens where they meet, which does
   * not exist. */
  pave: PaveDefinition | null
}

const METAL_TYPES: readonly MetalType[] = [
  'yellow_gold_18k',
  'white_gold_18k',
  'rose_gold_18k',
  'platinum',
  'silver',
]
const BAND_PROFILES: readonly BandProfile[] = ['comfort_fit', 'flat']
const SETTING_TYPES: readonly SettingType[] = [
  'prong',
  'bezel',
  'channel',
  'bar',
  'flush',
  'tension',
]
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
      gem: null,
    },
    setting: {
      type: 'prong',
      prongCount: 6,
      prongDiameter: 1.1,
      prongHeight: 4.8,
      basketHeight: 3.5,
      // Sprint 23 defaults: exactly the pre-Sprint-23 geometry.
      prongStyle: 'ROUND_PRONG',
      headArchitecture: 'BASKET',
      seatMode: 'NONE',
      prongTipRatio: 0.6,
      headBaseRatio: 0.55,
      pegDiameter: null,
      pegHeight: null,
      bezelWallThickness: 0.6,
      bezelWallHeight: 2.5,
      // Sprint 27 defaults. The gallery window values are read only by
      // OPEN_GALLERY, and `mode: null` resolves to the variant `type` and
      // `prongStyle` already meant - so this default definition's geometry is
      // exactly what it was.
      galleryWindowCount: 4,
      galleryWindowSweep: 45,
      galleryWindowHeightFraction: 0.6,
      mode: null,
    },
    material: { metal: 'yellow_gold_18k' },
    manufacturing: { method: 'lost_wax_casting' },
    preview: { meshTolerance: 0.1, angularTolerance: 0.2 },
    // No arrangement: a single-stone design, exactly as before Sprint 22.
    arrangement: null,
    // No family: a single-stone design, exactly as before Sprint 24.
    family: null,
    // No halo: exactly as before Sprint 25.
    halo: null,
    // No pavé: exactly as before Sprint 26.
    pave: null,
  }
}
