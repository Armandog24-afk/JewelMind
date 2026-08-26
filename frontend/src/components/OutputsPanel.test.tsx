import { render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useProjectStore } from '../store/useProjectStore'
import { useVisionStore } from '../store/useVisionStore'
import { OutputsPanel } from './OutputsPanel'
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
    inspection: {
      status: 'PASS',
      version: '1.0.0',
      componentCount: 4,
      productionSolidCount: 3,
      disconnectedProductionGroups: 0,
      diagnosticsCount: 0,
    },
  },
  previewComponents: {},
  warnings: [],
  generatedAt: new Date().toISOString(),
}

describe('OutputsPanel', () => {
  beforeEach(() => {
    useProjectStore.getState().resetProject()
    useVisionStore.setState({ viewMode: 'technical', captureRequestToken: 0 })
  })

  it('lists all 5 current outputs: STEP, STL, JDL JSON, technical specification, and presentation PNG', () => {
    render(<OutputsPanel />)
    expect(screen.getByText('STEP')).toBeInTheDocument()
    expect(screen.getByText('STL')).toBeInTheDocument()
    expect(screen.getByText('JDL JSON')).toBeInTheDocument()
    expect(screen.getByText('Technical specification')).toBeInTheDocument()
    expect(screen.getByText('Presentation PNG')).toBeInTheDocument()
  })

  it('keeps every download action disabled until a compatible model has been generated', () => {
    render(<OutputsPanel />)
    for (const label of ['Download', 'Download', 'Download', 'Download', 'Save render']) {
      expect(screen.getAllByText(label)[0]).toBeDisabled()
    }
  })

  it('enables download actions once a model is generated and the definition is not stale', () => {
    useProjectStore.setState({ generatedModel: FAKE_MODEL, lastSuccessfulPreview: FAKE_MODEL, isStale: false })
    render(<OutputsPanel />)
    for (const button of screen.getAllByText('Download')) {
      expect(button).not.toBeDisabled()
    }
    expect(screen.getByText('Save render')).not.toBeDisabled()
  })

  it('disables download actions again once the definition becomes stale', () => {
    useProjectStore.setState({ generatedModel: FAKE_MODEL, lastSuccessfulPreview: FAKE_MODEL, isStale: true })
    render(<OutputsPanel />)
    for (const button of screen.getAllByText('Download')) {
      expect(button).toBeDisabled()
    }
    expect(screen.getByText('Save render')).toBeDisabled()
  })

  it('requesting a PNG capture switches to Presentation view and increments the capture token', () => {
    useProjectStore.setState({ generatedModel: FAKE_MODEL, lastSuccessfulPreview: FAKE_MODEL, isStale: false })
    render(<OutputsPanel />)
    screen.getByText('Save render').click()
    expect(useVisionStore.getState().viewMode).toBe('presentation')
    expect(useVisionStore.getState().captureRequestToken).toBe(1)
  })
})
