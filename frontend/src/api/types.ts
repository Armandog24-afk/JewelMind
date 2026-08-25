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
