import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createDefaultDefinition } from '@shared/types/jewelry-definition'
import { ApiError } from '../api/types'
import type { DesignerResult, DesignIntent, IntentStatement } from '../api/types'
import { useDesignIntentStore } from '../store/useDesignIntentStore'
import { useProjectStore } from '../store/useProjectStore'
import { DesignerPanel } from './DesignerPanel'

const { interpretDesignRequest } = vi.hoisted(() => ({ interpretDesignRequest: vi.fn() }))

vi.mock('../api/client', () => ({
  fetchHealth: vi.fn(),
  generateModel: vi.fn(),
  exportStep: vi.fn(),
  exportStl: vi.fn(),
  exportJson: vi.fn(),
  exportSpecification: vi.fn(),
  fetchSpecificationText: vi.fn(),
  triggerBrowserDownload: vi.fn(),
  interpretDesignRequest,
  resolveApiUrl: (p: string) => p,
  API_BASE_URL: 'http://localhost:8000',
}))

function emptyDesignIntent(sourceText = ''): DesignIntent {
  return {
    version: '1.0.0',
    sourceText,
    statements: [],
    relationships: [],
    unresolvedDescriptors: [],
    conflicts: [],
    profile: null,
    diagnostics: [],
  }
}

function delicateStatement(): IntentStatement {
  return {
    intentId: 'intent-1',
    target: 'RING',
    concept: 'VISUAL_WEIGHT',
    value: 'DELICATE',
    strength: 'PREFERRED',
    priority: 0,
    provenance: 'AI_NORMALIZED',
    confidenceClass: 'HIGH_CONFIDENCE_NORMALIZATION',
    sourceText: 'delicato',
    resolutionStatus: 'PRESERVED',
    relatedJDLPaths: [],
    diagnostics: [],
  }
}

function completeResult(): DesignerResult {
  const candidateJDL = {
    ...createDefaultDefinition(),
    material: { metal: 'rose_gold_18k' as const },
  }
  return {
    requestId: 'r1',
    proposal: {
      proposalId: 'p1',
      sourceText: 'Fammi un solitario in oro rosa.',
      interactionMode: 'MODIFY',
      unresolvedIntent: [],
      unsupportedFeatures: [],
      proposedFields: [
        {
          path: 'material.metal',
          value: 'rose_gold_18k',
          provenance: 'AI_INTERPRETATION',
          confidence: 'NORMALIZED',
          sourceText: 'oro rosa',
          previousValue: 'yellow_gold_18k',
        },
      ],
      clarificationQuestions: [],
      diagnostics: [],
      candidateJDL,
      validation: [],
      forgeEvaluation: { results: [], hasErrors: false },
      diff: [
        { path: 'material.metal', previousValue: 'yellow_gold_18k', proposedValue: 'rose_gold_18k', changed: true },
      ],
      proposalStatus: 'COMPLETE',
      designIntent: emptyDesignIntent('Fammi un solitario in oro rosa.'),
    },
  }
}

describe('DesignerPanel', () => {
  beforeEach(() => {
    useProjectStore.getState().resetProject()
    useDesignIntentStore.getState().clearIntent()
    interpretDesignRequest.mockReset()
  })

  it('renders the natural-language input and keeps it disabled until text is entered', () => {
    render(<DesignerPanel />)
    expect(screen.getByPlaceholderText('Describe your design or change…')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Interpret' })).toBeDisabled()
  })

  it('shows a proposal review after a successful interpretation and applies it on request', async () => {
    interpretDesignRequest.mockResolvedValue(completeResult())
    render(<DesignerPanel />)

    fireEvent.change(screen.getByPlaceholderText('Describe your design or change…'), {
      target: { value: 'Fammi un solitario in oro rosa.' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Interpret' }))

    await waitFor(() => expect(screen.getByText('JewelMind understood')).toBeInTheDocument())
    expect(screen.getByText('material.metal')).toBeInTheDocument()
    expect(screen.getByText('rose_gold_18k')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Apply proposal' }))
    expect(useProjectStore.getState().currentDefinition.material.metal).toBe('rose_gold_18k')
  })

  it('shows an "unavailable" message, without breaking manual editing, when no provider is configured', async () => {
    interpretDesignRequest.mockRejectedValue(
      new ApiError(503, {
        error: { code: 'DESIGNER_PROVIDER_UNAVAILABLE', message: 'unavailable', requestId: 'r', details: [] },
      }),
    )
    render(<DesignerPanel />)

    fireEvent.change(screen.getByPlaceholderText('Describe your design or change…'), {
      target: { value: 'Fammi un anello.' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Interpret' }))

    await waitFor(() =>
      expect(screen.getByText(/AI interpretation is unavailable/)).toBeInTheDocument(),
    )
  })

  it('surfaces unsupported features without silently dropping them', async () => {
    const result = completeResult()
    result.proposal.proposedFields = []
    result.proposal.diff = []
    result.proposal.candidateJDL = createDefaultDefinition()
    result.proposal.unsupportedFeatures = [
      {
        feature: 'halo',
        sourceText: 'halo',
        reason: 'Halo settings are not currently supported.',
        currentCapability: null,
        futureRoadmapReference: null,
        blocking: true,
        suggestedSupportedAlternative: 'a single round stone with a prong setting',
      },
    ]
    result.proposal.proposalStatus = 'UNSUPPORTED'
    interpretDesignRequest.mockResolvedValue(result)

    render(<DesignerPanel />)
    fireEvent.change(screen.getByPlaceholderText('Describe your design or change…'), {
      target: { value: 'Fammi un halo.' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Interpret' }))

    await waitFor(() => expect(screen.getByText('Not currently supported')).toBeInTheDocument())
    expect(screen.getByText(/halo — Halo settings are not currently supported/)).toBeInTheDocument()
  })

  it('shows design intent separately from technical fields and preserves it on apply', async () => {
    const result = completeResult()
    result.proposal.designIntent = {
      ...emptyDesignIntent(result.proposal.sourceText),
      statements: [delicateStatement()],
    }
    interpretDesignRequest.mockResolvedValue(result)

    render(<DesignerPanel />)
    fireEvent.change(screen.getByPlaceholderText('Describe your design or change…'), {
      target: { value: 'Fammi un solitario delicato in oro rosa.' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Interpret' }))

    await waitFor(() => expect(screen.getByText('Design intent')).toBeInTheDocument())
    expect(screen.getByText(/ring: delicate \(visual weight\)/)).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Apply proposal' }))
    expect(useDesignIntentStore.getState().currentIntent?.statements[0]?.value).toBe('DELICATE')
  })

  it('does not mark the model stale when the proposal contains only design intent', async () => {
    useProjectStore.setState({ generatedModel: { modelId: 'm1' } as never, isStale: false })
    const result = completeResult()
    result.proposal.proposedFields = []
    result.proposal.diff = [] // no technical field actually changed
    result.proposal.candidateJDL = useProjectStore.getState().currentDefinition
    result.proposal.designIntent = {
      ...emptyDesignIntent(result.proposal.sourceText),
      statements: [delicateStatement()],
    }
    interpretDesignRequest.mockResolvedValue(result)

    render(<DesignerPanel />)
    fireEvent.change(screen.getByPlaceholderText('Describe your design or change…'), {
      target: { value: 'Rendilo più delicato.' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Interpret' }))
    await waitFor(() => expect(screen.getByText('Design intent')).toBeInTheDocument())

    fireEvent.click(screen.getByRole('button', { name: 'Apply proposal' }))
    expect(useProjectStore.getState().isStale).toBe(false)
    expect(useDesignIntentStore.getState().currentIntent?.statements[0]?.value).toBe('DELICATE')
  })

  it('does mark the model stale when the proposal contains a real technical change', async () => {
    useProjectStore.setState({ generatedModel: { modelId: 'm1' } as never, isStale: false })
    interpretDesignRequest.mockResolvedValue(completeResult())

    render(<DesignerPanel />)
    fireEvent.change(screen.getByPlaceholderText('Describe your design or change…'), {
      target: { value: 'Fammi un solitario in oro rosa.' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Interpret' }))
    await waitFor(() => expect(screen.getByText('JewelMind understood')).toBeInTheDocument())

    fireEvent.click(screen.getByRole('button', { name: 'Apply proposal' }))
    expect(useProjectStore.getState().isStale).toBe(true)
  })
})
