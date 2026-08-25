import type { JewelryDefinition } from '@shared/types/jewelry-definition'
import type { ValidationResult } from '@shared/validation/rules'

export interface HealthResponse {
  status: string
  service: string
  version: string
  cadEngine: string
  cadEngineReady: boolean
}

export interface ValidateResponse {
  results: ValidationResult[]
  hasErrors: boolean
}

export interface PreviewComponentEntry {
  vertexCount: number
  triangleCount: number
  volumeMm3: number
  boundingBox: Record<'xmin' | 'xmax' | 'ymin' | 'ymax' | 'zmin' | 'zmax', number>
  warnings: string[]
  url: string | null
  /** Explicit component identity for Vision (Sprint 8) — see
   * docs/bible/10-vision/223-atlas-to-vision-contract.md. Optional so
   * this type still matches a backend that predates this field. */
  geometryRole?: 'production_metal' | 'stone_reference' | 'support' | 'preview_only'
  productionRole?: 'included_by_default' | 'excluded_by_default' | 'never_included'
  meshSource?: 'stl'
  generationStatus?: 'SUCCEEDED' | 'SUCCEEDED_WITH_FALLBACK' | 'FAILED' | 'EMPTY'
}

export interface GenerateResponse {
  modelId: string
  definitionHash: string
  validation: ValidationResult[]
  metadata: {
    generatorVersion: string
    generationDurationSeconds: number
    componentVolumesMm3: Record<string, number>
    combinedMetalVolumeMm3: number
    boundingBoxMm: Record<'xmin' | 'xmax' | 'ymin' | 'ymax' | 'zmin' | 'zmax', number>
    prongs: {
      requestedCount: number
      generatedCount: number
      prongRadiusMm: number
      centerRadiusMm: number
      positions: Array<{ x: number; y: number }>
    }
  }
  previewComponents: Record<string, PreviewComponentEntry>
  warnings: string[]
  generatedAt: string
}

export interface ModelMetadataResponse {
  modelId: string
  definitionHash: string
  generatorVersion: string
  generatedAt: string
  generationDurationSeconds: number
  componentVolumesMm3: Record<string, number>
  combinedMetalVolumeMm3: number
  boundingBoxMm: Record<'xmin' | 'xmax' | 'ymin' | 'ymax' | 'zmin' | 'zmax', number>
  warnings: string[]
  validation: ValidationResult[]
}

// --- Designer v1 (docs/bible/12-designer/) -----------------------------

export type FieldProvenance =
  | 'USER_EXPLICIT'
  | 'USER_CONTEXT'
  | 'CURRENT_DESIGN'
  | 'SYSTEM_DEFAULT'
  | 'DETERMINISTIC_DERIVATION'
  | 'AI_INTERPRETATION'
  | 'CLARIFICATION_RESPONSE'
  | 'UNRESOLVED'

export type ConfidenceCategory = 'EXACT' | 'NORMALIZED' | 'INFERRED' | 'DEFAULTED' | 'AMBIGUOUS' | 'UNSUPPORTED'

export type AmbiguityLevel = 'LOW_IMPACT_AMBIGUITY' | 'HIGH_IMPACT_AMBIGUITY' | 'UNSUPPORTED_AMBIGUITY'

export type ProposalStatus =
  | 'COMPLETE'
  | 'NEEDS_CLARIFICATION'
  | 'PARTIALLY_SUPPORTED'
  | 'UNSUPPORTED'
  | 'INVALID'
  | 'READY_FOR_REVIEW'
  | 'ACCEPTED'
  | 'REJECTED'

export type DesignerInteractionMode = 'CREATE' | 'MODIFY'

export interface NaturalLanguageDesignRequest {
  requestId: string
  text: string
  locale?: 'it' | 'en' | null
  interactionMode: DesignerInteractionMode
  currentJDL?: JewelryDefinition | null
  currentDesignIntent?: DesignIntent | null
}

// --- Design Intent Model v1 (docs/bible/13-design-intent/) -------------

export type IntentTarget =
  | 'JEWELRY_PRODUCT'
  | 'RING'
  | 'BAND'
  | 'STONE'
  | 'SETTING'
  | 'PRONGS'
  | 'BASKET'
  | 'MATERIAL_APPEARANCE'
  | 'OVERALL_PROPORTION'
  | 'VISUAL_HIERARCHY'

export type IntentConceptCategory =
  | 'VISUAL_WEIGHT'
  | 'SIMPLICITY'
  | 'STYLE_TEMPORALITY'
  | 'VISUAL_EMPHASIS'
  | 'PROPORTIONAL_CHARACTER'
  | 'STRUCTURAL_CHARACTER'

export type IntentStrength = 'OPTIONAL' | 'PREFERRED' | 'IMPORTANT' | 'REQUIRED'

export type IntentProvenance =
  | 'USER_EXPLICIT'
  | 'USER_CONTEXT'
  | 'AI_NORMALIZED'
  | 'SYSTEM_PROFILE'
  | 'EXISTING_PROJECT'
  | 'CLARIFICATION_RESPONSE'
  | 'DERIVED_RELATION'
  | 'UNRESOLVED'

export type IntentConfidence = 'EXACT' | 'HIGH_CONFIDENCE_NORMALIZATION' | 'AMBIGUOUS' | 'INFERRED' | 'UNRESOLVED'

export type IntentResolutionStatus =
  | 'UNRESOLVED'
  | 'PRESERVED'
  | 'DETERMINISTICALLY_RESOLVED'
  | 'USER_RESOLVED'
  | 'PROFILE_RESOLVED'
  | 'UNSUPPORTED'
  | 'CONFLICTING'

export type IntentConflictType =
  | 'EXPLICIT_CONTRADICTION'
  | 'SOFT_TENSION'
  | 'TARGET_CONFLICT'
  | 'PRIORITY_CONFLICT'
  | 'RESOLUTION_CONFLICT'

export type RelationPredicate =
  | 'NARROWER_THAN'
  | 'BROADER_THAN'
  | 'DOMINANT_OVER'
  | 'SUBORDINATE_TO'
  | 'DISCREET_RELATIVE_TO'
  | 'BALANCED_WITH'

export interface IntentStatement {
  intentId: string
  target: IntentTarget
  concept: IntentConceptCategory
  value: string
  strength: IntentStrength
  priority: number
  provenance: IntentProvenance
  confidenceClass: IntentConfidence
  sourceText: string
  resolutionStatus: IntentResolutionStatus
  relatedJDLPaths: string[]
  diagnostics: string[]
}

export interface IntentRelation {
  relationId: string
  subject: IntentTarget
  predicate: RelationPredicate
  object: IntentTarget
  strength: IntentStrength
  provenance: IntentProvenance
  resolutionStatus: IntentResolutionStatus
  sourceText: string
}

export interface IntentConflict {
  conflictId: string
  type: IntentConflictType
  statementIds: string[]
  description: string
}

export interface IntentDiagnostic {
  code:
    | 'INTENT_UNKNOWN_DESCRIPTOR'
    | 'INTENT_AMBIGUOUS_DESCRIPTOR'
    | 'INTENT_CONFLICT'
    | 'INTENT_UNSUPPORTED_TARGET'
    | 'INTENT_NO_DETERMINISTIC_RESOLUTION'
    | 'INTENT_PROFILE_UNAVAILABLE'
    | 'INTENT_RESOLUTION_REQUIRES_CONFIRMATION'
    | 'INTENT_INVALID_RELATION'
    | 'INTENT_PRESERVED_UNRESOLVED'
  severity: 'info' | 'warning' | 'error'
  message: string
  statementId: string | null
}

export interface DesignIntent {
  version: string
  sourceText: string
  statements: IntentStatement[]
  relationships: IntentRelation[]
  unresolvedDescriptors: string[]
  conflicts: IntentConflict[]
  profile: string | null
  diagnostics: IntentDiagnostic[]
}

export interface ProposedField {
  path: string
  value: string | number | boolean
  provenance: FieldProvenance
  confidence: ConfidenceCategory
  sourceText: string | null
  previousValue: string | number | boolean | null
}

export interface ClarificationQuestion {
  field: string | null
  question: string
  options: string[]
  ambiguityLevel: AmbiguityLevel
}

export interface UnsupportedFeature {
  feature: string
  sourceText: string
  reason: string
  currentCapability: string | null
  futureRoadmapReference: string | null
  blocking: boolean
  suggestedSupportedAlternative: string | null
}

export interface DesignerDiagnostic {
  code:
    | 'DESIGNER_UNSUPPORTED_FEATURE'
    | 'DESIGNER_AMBIGUOUS_REQUEST'
    | 'DESIGNER_CLARIFICATION_REQUIRED'
    | 'DESIGNER_PROPOSAL_INVALID'
    | 'DESIGNER_CAPABILITY_MISMATCH'
  severity: 'info' | 'warning' | 'error'
  message: string
  field: string | null
}

export interface FieldDiff {
  path: string
  previousValue: string | number | boolean | null
  proposedValue: string | number | boolean | null
  changed: boolean
}

export interface ForgeEvaluationSummary {
  results: ValidationResult[]
  hasErrors: boolean
}

export interface DesignerProposal {
  proposalId: string
  sourceText: string
  interactionMode: DesignerInteractionMode
  unresolvedIntent: string[]
  unsupportedFeatures: UnsupportedFeature[]
  proposedFields: ProposedField[]
  clarificationQuestions: ClarificationQuestion[]
  diagnostics: DesignerDiagnostic[]
  candidateJDL: JewelryDefinition | null
  validation: ValidationResult[]
  forgeEvaluation: ForgeEvaluationSummary | null
  diff: FieldDiff[]
  proposalStatus: ProposalStatus
  designIntent: DesignIntent
}

export interface DesignerResult {
  requestId: string
  proposal: DesignerProposal
}

export interface ApiErrorBody {
  error: {
    code: string
    message: string
    requestId: string
    details: unknown[]
  }
}

export class ApiError extends Error {
  code: string
  requestId: string
  details: unknown[]
  status: number

  constructor(status: number, body: ApiErrorBody) {
    super(body.error.message)
    this.name = 'ApiError'
    this.status = status
    this.code = body.error.code
    this.requestId = body.error.requestId
    this.details = body.error.details
  }
}
