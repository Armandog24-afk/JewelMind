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
