import { render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useProjectStore } from '../store/useProjectStore'
import { ProjectActions } from './ProjectActions'
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

const FAKE_MODEL: GenerateResponse = {
  modelId: 'abc123',
  definitionHash: 'abc123',
  validation: [],
  metadata: {
    generatorVersion: '0.1.0',
    generationDurationSeconds: 0.5,
    componentVolumesMm3: { band: 1, stone_reference: 1, prongs: 1, basket_support: 1 },
    combinedMetalVolumeMm3: 3,
    boundingBoxMm: { xmin: -1, xmax: 1, ymin: -1, ymax: 1, zmin: -1, zmax: 1 },
    prongs: { requestedCount: 6, generatedCount: 6, prongRadiusMm: 0.5, centerRadiusMm: 3, positions: [] },
  },
  previewComponents: {},
  warnings: [],
  generatedAt: new Date().toISOString(),
}

describe('ProjectActions', () => {
  beforeEach(() => {
    useProjectStore.getState().resetProject()
  })

  it('disables Generate when there are validation errors', () => {
    useProjectStore.getState().updateBand({ width: 0.5 })
    render(<ProjectActions />)
    expect(screen.getByText(/Generate model/)).toBeDisabled()
  })

  it('does not disable Generate for warnings only', () => {
    useProjectStore.getState().updateBand({ width: 13 })
    render(<ProjectActions />)
    expect(screen.getByText(/Generate model/)).not.toBeDisabled()
  })

  it('keeps export buttons disabled until a compatible model has been generated', () => {
    render(<ProjectActions />)
    expect(screen.getByText('Export STEP')).toBeDisabled()
    expect(screen.getByText('Export STL')).toBeDisabled()
    expect(screen.getByText('Export JSON')).toBeDisabled()
  })

  it('enables export buttons once a model is generated and definition is not stale', () => {
    useProjectStore.setState({ generatedModel: FAKE_MODEL, isStale: false })
    render(<ProjectActions />)
    expect(screen.getByText('Export STEP')).not.toBeDisabled()
    expect(screen.getByText('Export STL')).not.toBeDisabled()
    expect(screen.getByText('Export JSON')).not.toBeDisabled()
  })

  it('disables export buttons again once the definition becomes stale', () => {
    useProjectStore.setState({ generatedModel: FAKE_MODEL, isStale: true })
    render(<ProjectActions />)
    expect(screen.getByText('Export STEP')).toBeDisabled()
  })
})
