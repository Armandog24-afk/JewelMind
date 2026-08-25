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

  it('labels the primary action "Generate model" before any model exists', () => {
    render(<ProjectActions />)
    expect(screen.getByText('Generate model')).toBeInTheDocument()
  })

  it('relabels the primary action "Regenerate model" once a model exists', () => {
    useProjectStore.setState({ generatedModel: FAKE_MODEL, isStale: false })
    render(<ProjectActions />)
    expect(screen.getByText('Regenerate model')).toBeInTheDocument()
  })

  it('never renders a per-artifact export button — those moved to the consolidated Outputs panel', () => {
    useProjectStore.setState({ generatedModel: FAKE_MODEL, isStale: false })
    render(<ProjectActions />)
    expect(screen.queryByText(/Export STEP/)).toBeNull()
    expect(screen.queryByText(/Export STL/)).toBeNull()
    expect(screen.queryByText(/Export JSON/)).toBeNull()
  })

  it('asks for confirmation before resetting, and does not reset when the user cancels', () => {
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false)
    useProjectStore.getState().updateBand({ width: 13 })
    render(<ProjectActions />)
    screen.getByText('Reset project').click()
    expect(confirmSpy).toHaveBeenCalled()
    expect(useProjectStore.getState().currentDefinition.band.width).toBe(13)
    confirmSpy.mockRestore()
  })

  it('resets when the user confirms', () => {
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true)
    useProjectStore.getState().updateBand({ width: 13 })
    render(<ProjectActions />)
    screen.getByText('Reset project').click()
    expect(useProjectStore.getState().currentDefinition.band.width).not.toBe(13)
    confirmSpy.mockRestore()
  })
})
