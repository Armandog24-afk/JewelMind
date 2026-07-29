import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createDefaultDefinition } from '@shared/types/jewelry-definition'
import { ApiError } from '../api/types'
import type { GenerateResponse } from '../api/types'

vi.mock('../api/client', () => ({
  fetchHealth: vi.fn(),
  generateModel: vi.fn(),
  exportStep: vi.fn(),
  exportStl: vi.fn(),
  exportJson: vi.fn(),
  exportSpecification: vi.fn(),
  fetchSpecificationText: vi.fn(),
  triggerBrowserDownload: vi.fn(),
  resolveApiUrl: (p: string) => p,
  API_BASE_URL: 'http://localhost:8000',
}))

import { generateModel } from '../api/client'
import { useProjectStore } from './useProjectStore'

function fakeModel(overrides: Partial<GenerateResponse> = {}): GenerateResponse {
  return {
    modelId: 'model-1',
    definitionHash: 'model-1',
    validation: [],
    metadata: {
      generatorVersion: '0.1.0',
      generationDurationSeconds: 0.2,
      componentVolumesMm3: {},
      combinedMetalVolumeMm3: 10,
      boundingBoxMm: { xmin: -1, xmax: 1, ymin: -1, ymax: 1, zmin: -1, zmax: 1 },
      prongs: { requestedCount: 6, generatedCount: 6, prongRadiusMm: 0.5, centerRadiusMm: 3, positions: [] },
    },
    previewComponents: {},
    warnings: [],
    generatedAt: new Date().toISOString(),
    ...overrides,
  }
}

describe('useProjectStore', () => {
  beforeEach(() => {
    useProjectStore.getState().resetProject()
    vi.mocked(generateModel).mockReset()
  })

  it('reset restores the default definition', () => {
    useProjectStore.getState().updateBand({ width: 5 })
    expect(useProjectStore.getState().currentDefinition.band.width).toBe(5)

    useProjectStore.getState().resetProject()
    expect(useProjectStore.getState().currentDefinition).toEqual(createDefaultDefinition())
  })

  it('marks the definition stale after a parameter changes post-generation', async () => {
    vi.mocked(generateModel).mockResolvedValue(fakeModel())
    await useProjectStore.getState().generate()
    expect(useProjectStore.getState().isStale).toBe(false)

    useProjectStore.getState().updateStone({ diameter: 7 })
    expect(useProjectStore.getState().isStale).toBe(true)
  })

  it('sets generationStatus to generating while the request is in flight', async () => {
    let resolveFn: (value: GenerateResponse) => void = () => {}
    vi.mocked(generateModel).mockReturnValue(
      new Promise((resolve) => {
        resolveFn = resolve
      }),
    )

    const generatePromise = useProjectStore.getState().generate()
    expect(useProjectStore.getState().generationStatus).toBe('generating')

    resolveFn(fakeModel())
    await generatePromise
    expect(useProjectStore.getState().generationStatus).toBe('success')
  })

  it('keeps the last successful preview visible when a later generation fails', async () => {
    vi.mocked(generateModel).mockResolvedValueOnce(fakeModel({ modelId: 'good-model' }))
    await useProjectStore.getState().generate()
    expect(useProjectStore.getState().lastSuccessfulPreview?.modelId).toBe('good-model')

    vi.mocked(generateModel).mockRejectedValueOnce(
      new ApiError(500, {
        error: { code: 'MODEL_GENERATION_FAILED', message: 'boom', requestId: 'r1', details: [] },
      }),
    )
    await useProjectStore.getState().generate()

    expect(useProjectStore.getState().generationStatus).toBe('error')
    expect(useProjectStore.getState().lastSuccessfulPreview?.modelId).toBe('good-model')
  })
})
