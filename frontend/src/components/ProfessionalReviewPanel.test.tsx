import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ApiError } from '../api/types'
import { useProjectStore } from '../store/useProjectStore'
import { ProfessionalReviewPanel } from './ProfessionalReviewPanel'

const { generateReviewPackage, triggerBrowserDownload } = vi.hoisted(() => ({
  generateReviewPackage: vi.fn(),
  triggerBrowserDownload: vi.fn(),
}))

vi.mock('../api/client', () => ({
  fetchHealth: vi.fn(),
  generateModel: vi.fn(),
  exportStep: vi.fn(),
  exportStl: vi.fn(),
  exportJson: vi.fn(),
  exportSpecification: vi.fn(),
  fetchSpecificationText: vi.fn(),
  generateReviewPackage,
  triggerBrowserDownload,
  resolveApiUrl: (p: string) => p,
  API_BASE_URL: 'http://localhost:8000',
}))

function setGeneratedModel() {
  useProjectStore.setState({
    generatedModel: {
      modelId: 'model-1',
      definitionHash: 'hash-1',
      metadata: {
        generatorVersion: '0.1.0',
        generationDurationSeconds: 0.1,
        componentVolumesMm3: {},
        combinedMetalVolumeMm3: 1,
        boundingBoxMm: { xmin: 0, xmax: 1, ymin: 0, ymax: 1, zmin: 0, zmax: 1 },
        prongs: { requestedCount: 6, generatedCount: 6, prongRadiusMm: 0.5, centerRadiusMm: 3, positions: [] },
      },
      previewComponents: {},
      warnings: [],
      generatedAt: '2026-01-01T00:00:00Z',
    } as never,
    isStale: false,
    validationResults: [],
  })
}

describe('ProfessionalReviewPanel', () => {
  beforeEach(() => {
    useProjectStore.getState().resetProject()
    generateReviewPackage.mockReset()
    triggerBrowserDownload.mockReset()
  })

  it('shows "generate a model first" when no model has been generated', () => {
    render(<ProfessionalReviewPanel />)
    expect(screen.getByText('Generate a model first')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Generate review package' })).toBeDisabled()
  })

  it('is blocked when the model is stale', () => {
    setGeneratedModel()
    useProjectStore.setState({ isStale: true })
    render(<ProfessionalReviewPanel />)
    expect(screen.getByText('Design changed — regenerate first')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Generate review package' })).toBeDisabled()
  })

  it('is blocked when there are blocking validation errors', () => {
    setGeneratedModel()
    useProjectStore.setState({
      validationResults: [{ ruleId: 'X', severity: 'error', message: 'bad', parameter: 'x' } as never],
    })
    render(<ProfessionalReviewPanel />)
    expect(screen.getByText('Design changed — regenerate first')).toBeInTheDocument()
  })

  it('generates and downloads a review package with the entered case ID', async () => {
    setGeneratedModel()
    generateReviewPackage.mockResolvedValue({ blob: new Blob(['zip']), filename: 'review.zip' })
    render(<ProfessionalReviewPanel />)

    fireEvent.change(screen.getByLabelText('Review case ID'), { target: { value: 'JMCASE001' } })
    fireEvent.click(screen.getByRole('button', { name: 'Generate review package' }))

    await waitFor(() => expect(generateReviewPackage).toHaveBeenCalledWith('model-1', 'JMCASE001', true))
    expect(triggerBrowserDownload).toHaveBeenCalledWith(expect.any(Blob), 'review.zip')
  })

  it('falls back to a definition-hash-based case ID when left blank', async () => {
    setGeneratedModel()
    generateReviewPackage.mockResolvedValue({ blob: new Blob(['zip']), filename: 'review.zip' })
    render(<ProfessionalReviewPanel />)

    fireEvent.click(screen.getByRole('button', { name: 'Generate review package' }))

    await waitFor(() =>
      expect(generateReviewPackage).toHaveBeenCalledWith('model-1', 'JMCASE-hash-1', true),
    )
  })

  it('shows an error message when generation fails', async () => {
    setGeneratedModel()
    generateReviewPackage.mockRejectedValue(
      new ApiError(500, { error: { code: 'X', message: 'boom', requestId: 'r', details: [] } }),
    )
    render(<ProfessionalReviewPanel />)

    fireEvent.click(screen.getByRole('button', { name: 'Generate review package' }))
    await waitFor(() => expect(screen.getByText('boom')).toBeInTheDocument())
  })
})
