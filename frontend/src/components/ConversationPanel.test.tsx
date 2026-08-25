import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createDefaultDefinition } from '@shared/types/jewelry-definition'
import { ApiError } from '../api/types'
import type {
  ClarificationThread,
  ConversationProposal,
  ConversationResult,
  ConversationSession,
  ConversationTurn,
  DesignIntent,
} from '../api/types'
import { useConversationStore } from '../store/useConversationStore'
import { useDesignIntentStore } from '../store/useDesignIntentStore'
import { useProjectStore } from '../store/useProjectStore'
import { ConversationPanel } from './ConversationPanel'

const { interpretConversationTurn } = vi.hoisted(() => ({ interpretConversationTurn: vi.fn() }))

vi.mock('../api/client', () => ({
  fetchHealth: vi.fn(),
  generateModel: vi.fn(),
  exportStep: vi.fn(),
  exportStl: vi.fn(),
  exportJson: vi.fn(),
  exportSpecification: vi.fn(),
  fetchSpecificationText: vi.fn(),
  triggerBrowserDownload: vi.fn(),
  interpretConversationTurn,
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

function baseSession(overrides: Partial<ConversationSession> = {}): ConversationSession {
  return {
    sessionId: 'session-1',
    sessionVersion: '1.0.0',
    currentJDLHash: 'hash-jdl',
    currentIntentHash: 'hash-intent',
    turns: [],
    pendingClarification: null,
    activeProposal: null,
    acceptedChangeHistory: [],
    lastReferencedTarget: null,
    summary: {
      acceptedDecisions: [],
      intentThemes: [],
      unresolvedQuestions: [],
      rejectedDirections: [],
      unsupportedDiscussed: [],
    },
    status: 'IDLE',
    createdAt: '2026-01-01T00:00:00Z',
    updatedAt: '2026-01-01T00:00:00Z',
    ...overrides,
  }
}

function baseTurn(overrides: Partial<ConversationTurn> = {}): ConversationTurn {
  return {
    turnId: 'turn-1',
    sequence: 1,
    role: 'user',
    sourceText: 'Fammi un solitario in oro rosa.',
    timestamp: '2026-01-01T00:00:00Z',
    interpretedAction: 'MODIFY_DESIGN_PROPOSAL',
    references: [],
    technicalChanges: [],
    intentChanges: [],
    clarification: null,
    unsupportedFeatures: [],
    proposalId: null,
    result: 'Proposal ready.',
    accepted: null,
    relatedJDLHashBefore: 'hash-jdl',
    relatedJDLHashAfter: 'hash-jdl',
    relatedIntentHashBefore: 'hash-intent',
    relatedIntentHashAfter: 'hash-intent',
    diagnostics: [],
    ...overrides,
  }
}

function baseProposal(overrides: Partial<ConversationProposal> = {}): ConversationProposal {
  const candidateJDL = { ...createDefaultDefinition(), material: { metal: 'rose_gold_18k' as const } }
  return {
    proposalId: 'conv-proposal-1',
    turnId: 'turn-1',
    baseDefinitionHash: 'hash-jdl',
    baseIntentHash: 'hash-intent',
    designerProposal: {
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
    status: 'ACTIVE',
    ...overrides,
  }
}

function baseClarification(overrides: Partial<ClarificationThread> = {}): ClarificationThread {
  return {
    clarificationId: 'clarification-1',
    originatingTurnId: 'turn-1',
    question: 'What width would you like?',
    target: 'band.width',
    expectedAnswerType: 'NUMERIC',
    allowedChoices: [],
    required: true,
    status: 'OPEN',
    createdAt: '2026-01-01T00:00:00Z',
    resolvedAt: null,
    answer: null,
    ...overrides,
  }
}

function proposalReadyResult(): ConversationResult {
  const proposal = baseProposal()
  const turn = baseTurn({
    interpretedAction: 'MODIFY_DESIGN_PROPOSAL',
    technicalChanges: ['material.metal'],
    proposalId: proposal.proposalId,
    result: 'Proposal ready: 1 technical change(s), 0 intent statement(s).',
  })
  return {
    session: baseSession({ status: 'PROPOSAL_READY', activeProposal: proposal, turns: [turn] }),
    turn,
  }
}

describe('ConversationPanel', () => {
  beforeEach(() => {
    useProjectStore.getState().resetProject()
    useDesignIntentStore.getState().clearIntent()
    useConversationStore.getState().resetSession()
    interpretConversationTurn.mockReset()
  })

  it('renders the natural-language input and keeps Send disabled until text is entered', () => {
    render(<ConversationPanel />)
    expect(screen.getByPlaceholderText('Describe your design or change…')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Send' })).toBeDisabled()
  })

  it('shows a proposal review after a turn and applies it to the stores on Accept', async () => {
    interpretConversationTurn.mockResolvedValueOnce(proposalReadyResult())
    render(<ConversationPanel />)

    fireEvent.change(screen.getByPlaceholderText('Describe your design or change…'), {
      target: { value: 'Fammi un solitario in oro rosa.' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Send' }))

    await waitFor(() => expect(screen.getByText('Proposed change')).toBeInTheDocument())
    expect(screen.getByText(/yellow_gold_18k → rose_gold_18k/)).toBeInTheDocument()

    const accepted = proposalReadyResult()
    accepted.session = baseSession({
      status: 'ACTIVE',
      turns: [...accepted.session.turns, baseTurn({ turnId: 'turn-2', sourceText: 'Accept', interpretedAction: 'ACCEPT_PROPOSAL', accepted: true })],
    })
    accepted.turn = baseTurn({ turnId: 'turn-2', sourceText: 'Accept', interpretedAction: 'ACCEPT_PROPOSAL', accepted: true })
    interpretConversationTurn.mockResolvedValueOnce(accepted)

    fireEvent.click(screen.getByRole('button', { name: 'Accept' }))
    await waitFor(() => expect(useProjectStore.getState().currentDefinition.material.metal).toBe('rose_gold_18k'))
  })

  it('does not apply anything to the stores on Reject', async () => {
    interpretConversationTurn.mockResolvedValueOnce(proposalReadyResult())
    render(<ConversationPanel />)

    fireEvent.change(screen.getByPlaceholderText('Describe your design or change…'), {
      target: { value: 'Fammi un solitario in oro rosa.' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Send' }))
    await waitFor(() => expect(screen.getByText('Proposed change')).toBeInTheDocument())

    const rejected: ConversationResult = {
      session: baseSession({ status: 'IDLE', turns: [proposalReadyResult().turn] }),
      turn: baseTurn({ turnId: 'turn-2', sourceText: 'Reject', interpretedAction: 'REJECT_PROPOSAL', accepted: false }),
    }
    interpretConversationTurn.mockResolvedValueOnce(rejected)

    fireEvent.click(screen.getByRole('button', { name: 'Reject' }))
    await waitFor(() => expect(screen.queryByText('Proposed change')).not.toBeInTheDocument())
    expect(useProjectStore.getState().currentDefinition.material.metal).not.toBe('rose_gold_18k')
  })

  it('shows an "unavailable" message, without breaking manual editing, when no provider is configured', async () => {
    interpretConversationTurn.mockRejectedValue(
      new ApiError(503, {
        error: { code: 'DESIGNER_PROVIDER_UNAVAILABLE', message: 'unavailable', requestId: 'r', details: [] },
      }),
    )
    render(<ConversationPanel />)

    fireEvent.change(screen.getByPlaceholderText('Describe your design or change…'), {
      target: { value: 'Fammi un anello.' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Send' }))

    await waitFor(() => expect(screen.getByText(/AI interpretation is unavailable/)).toBeInTheDocument())
  })

  it('shows a clarification card with enum choices, and sends the chosen option as the next turn', async () => {
    const clarification = baseClarification({ expectedAnswerType: 'ENUM_CHOICE', allowedChoices: ['rose_gold_18k', 'platinum'] })
    const turn = baseTurn({ interpretedAction: 'REQUEST_CLARIFICATION', clarification, result: clarification.question })
    interpretConversationTurn.mockResolvedValueOnce({
      session: baseSession({ status: 'WAITING_FOR_CLARIFICATION', pendingClarification: clarification, turns: [turn] }),
      turn,
    })
    render(<ConversationPanel />)

    fireEvent.change(screen.getByPlaceholderText('Describe your design or change…'), {
      target: { value: 'Cambia metallo.' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Send' }))
    await waitFor(() => expect(screen.getByText('What width would you like?')).toBeInTheDocument())

    interpretConversationTurn.mockResolvedValueOnce(proposalReadyResult())
    fireEvent.click(screen.getByRole('button', { name: 'rose_gold_18k' }))

    await waitFor(() =>
      expect(interpretConversationTurn).toHaveBeenLastCalledWith(expect.objectContaining({ text: 'rose_gold_18k' })),
    )
  })

  it('surfaces unsupported features without silently dropping them', async () => {
    const turn = baseTurn({
      interpretedAction: 'REPORT_UNSUPPORTED',
      unsupportedFeatures: ['halo'],
      result: 'Halo settings are not currently supported.',
    })
    interpretConversationTurn.mockResolvedValueOnce({
      session: baseSession({ status: 'ACTIVE', turns: [turn] }),
      turn,
    })
    render(<ConversationPanel />)

    fireEvent.change(screen.getByPlaceholderText('Describe your design or change…'), {
      target: { value: 'Fammi un halo.' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Send' }))

    await waitFor(() => expect(screen.getByRole('heading', { name: 'Not currently supported' })).toBeInTheDocument())
    expect(screen.getByText('Halo settings are not currently supported.')).toBeInTheDocument()
  })

  it('renders multi-turn history compactly, differentiating request from interpretation', async () => {
    const turn1 = baseTurn({ sourceText: 'Fammi un solitario in oro rosa.', result: 'Proposal ready.' })
    const turn2 = baseTurn({
      turnId: 'turn-2',
      sequence: 2,
      sourceText: 'ok',
      interpretedAction: 'ACCEPT_PROPOSAL',
      result: 'Proposal accepted.',
      accepted: true,
    })
    interpretConversationTurn.mockResolvedValueOnce({
      session: baseSession({ status: 'ACTIVE', turns: [turn1, turn2] }),
      turn: turn2,
    })
    render(<ConversationPanel />)

    fireEvent.change(screen.getByPlaceholderText('Describe your design or change…'), {
      target: { value: 'ok' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Send' }))

    await waitFor(() => expect(screen.getByText(/Fammi un solitario in oro rosa\./)).toBeInTheDocument())
    expect(screen.getByText(/Proposal ready\./)).toBeInTheDocument()
    expect(screen.getByText(/Proposal accepted\./)).toBeInTheDocument()
  })
})
