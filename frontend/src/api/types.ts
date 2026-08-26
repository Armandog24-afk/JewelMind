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
    inspection: InspectionSummary
  }
  previewComponents: Record<string, PreviewComponentEntry>
  warnings: string[]
  generatedAt: string
}

// --- Geometry Inspection v2 (docs/bible/16-geometry-inspection/) ------

/** The concise inspection summary embedded in generate/metadata responses —
 * never the full GeometryInspectionReport (see GET /api/models/{id}/inspection). */
export interface InspectionSummary {
  status: 'PASS' | 'FAIL' | 'UNKNOWN' | 'NOT_APPLICABLE' | 'NOT_IMPLEMENTED' | 'ERROR'
  version: string
  componentCount: number
  productionSolidCount: number
  disconnectedProductionGroups: number
  diagnosticsCount: number
}

export interface BoundingBoxFact {
  xmin: number
  ymin: number
  zmin: number
  xmax: number
  ymax: number
  zmax: number
  sizeX: number
  sizeY: number
  sizeZ: number
  centerX: number
  centerY: number
  centerZ: number
}

export interface ComponentInspectionResult {
  componentId: string
  exists: boolean
  status: InspectionSummary['status']
  shapeType: string | null
  solidCount: number | null
  volumeMm3: number | null
  boundingBox: BoundingBoxFact | null
  shapeValid: boolean | null
  fallbackUsed: boolean
  metadata: Record<string, unknown>
}

export interface DistanceResult {
  componentA: string
  componentB: string
  minDistanceMm: number | null
  status: InspectionSummary['status']
  unit: string
  tolerance: number
}

export interface IntersectionResult {
  componentA: string
  componentB: string
  status: 'INTERSECTS' | 'TOUCHES' | 'NO_INTERSECTION' | 'UNKNOWN'
  intersectionVolumeMm3: number | null
  intersectionSolidCount: number | null
  unit: string
  tolerance: number
  note: string
}

export interface ConnectivityGraph {
  graphType: 'PRODUCTION' | 'FULL_ASSEMBLY'
  nodes: string[]
  connectedGroups: string[][]
  isFullyConnected: boolean
  disconnectedGroupCount: number
}

export interface AssemblyInspectionResult {
  requiredComponentsPresent: boolean
  missingComponentIds: string[]
  componentCount: number
  productionComponentCount: number
  referenceComponentCount: number
  totalProductionVolumeMm3: number
  assemblyBoundingBox: BoundingBoxFact
  productionConnectivity: ConnectivityGraph
  fullAssemblyConnectivity: ConnectivityGraph
  intersections: IntersectionResult[]
  distances: DistanceResult[]
  prongCount: { requestedCount: number; generatedCount: number; matches: boolean; status: string }
}

/** The full report from GET /api/models/{modelId}/inspection — the
 * concise `InspectionSummary` above is what's embedded in generate/metadata
 * responses instead. */
export interface GeometryInspectionReport {
  inspectionId: string
  inspectionVersion: string
  definitionHash: string
  status: InspectionSummary['status']
  componentResults: ComponentInspectionResult[]
  assemblyResult: AssemblyInspectionResult
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
  inspection: InspectionSummary
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

// --- Conversation Engine v1 (docs/bible/14-conversation/) --------------

export type ConversationActionType =
  | 'CREATE_DESIGN_PROPOSAL'
  | 'MODIFY_DESIGN_PROPOSAL'
  | 'ADD_INTENT'
  | 'MODIFY_INTENT'
  | 'REMOVE_INTENT'
  | 'PRESERVE_TARGET'
  | 'REQUEST_CLARIFICATION'
  | 'ANSWER_CLARIFICATION'
  | 'REPORT_UNSUPPORTED'
  | 'ACCEPT_PROPOSAL'
  | 'REJECT_PROPOSAL'
  | 'CANCEL_INTERACTION'
  | 'NO_CHANGE'

export type ConversationSessionStatus =
  | 'ACTIVE'
  | 'WAITING_FOR_CLARIFICATION'
  | 'PROPOSAL_READY'
  | 'WAITING_FOR_ACCEPTANCE'
  | 'IDLE'
  | 'CLOSED'
  | 'FAILED'

export type ClarificationStatus = 'OPEN' | 'ANSWERED' | 'CANCELLED' | 'SUPERSEDED'

export type ExpectedAnswerType = 'NUMERIC' | 'ENUM_CHOICE' | 'FREE_TEXT' | 'CONFIRMATION'

export type ConversationProposalStatus = 'ACTIVE' | 'ACCEPTED' | 'REJECTED' | 'SUPERSEDED' | 'STALE'

export interface ClarificationThread {
  clarificationId: string
  originatingTurnId: string
  question: string
  target: string | null
  expectedAnswerType: ExpectedAnswerType
  allowedChoices: string[]
  required: boolean
  status: ClarificationStatus
  createdAt: string
  resolvedAt: string | null
  answer: string | null
}

export interface ConversationProposal {
  proposalId: string
  turnId: string
  baseDefinitionHash: string
  baseIntentHash: string
  designerProposal: DesignerProposal
  status: ConversationProposalStatus
}

export interface ConversationSummary {
  acceptedDecisions: string[]
  intentThemes: string[]
  unresolvedQuestions: string[]
  rejectedDirections: string[]
  unsupportedDiscussed: string[]
}

export interface ConversationDiagnostic {
  code: 'CONVERSATION_REFERENCE_AMBIGUOUS' | 'CONVERSATION_CLARIFICATION_INVALID' | 'CONVERSATION_STATE_SYNC_FAILED'
  severity: 'info' | 'warning' | 'error'
  message: string
}

export interface ConversationTurn {
  turnId: string
  sequence: number
  role: 'user' | 'system'
  sourceText: string
  timestamp: string
  interpretedAction: ConversationActionType
  references: string[]
  technicalChanges: string[]
  intentChanges: string[]
  clarification: ClarificationThread | null
  unsupportedFeatures: string[]
  proposalId: string | null
  result: string
  accepted: boolean | null
  relatedJDLHashBefore: string
  relatedJDLHashAfter: string
  relatedIntentHashBefore: string
  relatedIntentHashAfter: string
  diagnostics: ConversationDiagnostic[]
}

export interface ConversationSession {
  sessionId: string
  sessionVersion: string
  currentJDLHash: string
  currentIntentHash: string
  turns: ConversationTurn[]
  pendingClarification: ClarificationThread | null
  activeProposal: ConversationProposal | null
  acceptedChangeHistory: string[]
  lastReferencedTarget: string | null
  summary: ConversationSummary
  status: ConversationSessionStatus
  createdAt: string
  updatedAt: string
}

export interface ConversationTurnRequest {
  text: string
  locale?: 'it' | 'en' | null
  currentJDL: JewelryDefinition
  currentDesignIntent: DesignIntent
  session?: ConversationSession | null
}

export interface ConversationResult {
  session: ConversationSession
  turn: ConversationTurn
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
