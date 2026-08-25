import type { JewelryDefinition } from '@shared/types/jewelry-definition'
import {
  ApiError,
  type ApiErrorBody,
  type DesignerResult,
  type GenerateResponse,
  type HealthResponse,
  type ModelMetadataResponse,
  type NaturalLanguageDesignRequest,
  type ValidateResponse,
} from './types'

export const API_BASE_URL: string =
  (import.meta.env['VITE_API_BASE_URL'] as string | undefined) ?? 'http://localhost:8000'

export function resolveApiUrl(pathOrUrl: string): string {
  if (/^https?:\/\//.test(pathOrUrl)) return pathOrUrl
  return `${API_BASE_URL}${pathOrUrl}`
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
  })

  if (!response.ok) {
    const body = (await response.json()) as ApiErrorBody
    throw new ApiError(response.status, body)
  }

  return response.json() as Promise<T>
}

export async function fetchHealth(): Promise<HealthResponse> {
  return request<HealthResponse>('/api/health')
}

export async function validateDefinitionOnServer(
  definition: JewelryDefinition,
): Promise<ValidateResponse> {
  return request<ValidateResponse>('/api/models/validate', {
    method: 'POST',
    body: JSON.stringify(definition),
  })
}

export async function generateModel(definition: JewelryDefinition): Promise<GenerateResponse> {
  return request<GenerateResponse>('/api/models/generate', {
    method: 'POST',
    body: JSON.stringify(definition),
  })
}

export async function fetchModelMetadata(modelId: string): Promise<ModelMetadataResponse> {
  return request<ModelMetadataResponse>(`/api/models/${modelId}/metadata`)
}

export async function interpretDesignRequest(
  designerRequest: NaturalLanguageDesignRequest,
): Promise<DesignerResult> {
  return request<DesignerResult>('/api/designer/interpret', {
    method: 'POST',
    body: JSON.stringify(designerRequest),
  })
}

export function previewUrl(modelId: string, componentName: string): string {
  return `${API_BASE_URL}/api/models/${modelId}/preview/${componentName}`
}

async function downloadPost(
  path: string,
  payload: Record<string, unknown>,
): Promise<{ blob: Blob; filename: string }> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const body = (await response.json()) as ApiErrorBody
    throw new ApiError(response.status, body)
  }

  const disposition = response.headers.get('content-disposition') ?? ''
  const match = /filename="?([^"]+)"?/.exec(disposition)
  const filename = match?.[1] ?? 'jewelmind-export'
  const blob = await response.blob()
  return { blob, filename }
}

export async function exportStep(modelId: string, includeStoneReference: boolean) {
  return downloadPost('/api/models/export/step', { modelId, includeStoneReference })
}

export async function exportStl(modelId: string, includeStoneReference: boolean) {
  return downloadPost('/api/models/export/stl', { modelId, includeStoneReference })
}

export async function exportJson(modelId: string) {
  return downloadPost('/api/models/export/json', { modelId })
}

export async function exportSpecification(modelId: string) {
  return downloadPost('/api/models/specification', { modelId })
}

/** Fetches the specification as plain text for inline display (no download). */
export async function fetchSpecificationText(modelId: string): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/api/models/specification`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ modelId }),
  })
  if (!response.ok) {
    const body = (await response.json()) as ApiErrorBody
    throw new ApiError(response.status, body)
  }
  return response.text()
}

export function triggerBrowserDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}
