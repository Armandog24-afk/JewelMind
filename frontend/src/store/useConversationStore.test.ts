import { beforeEach, describe, expect, it } from 'vitest'
import type { ConversationSession } from '../api/types'
import { useConversationStore } from './useConversationStore'

function session(overrides: Partial<ConversationSession> = {}): ConversationSession {
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

describe('useConversationStore', () => {
  beforeEach(() => {
    useConversationStore.getState().resetSession()
  })

  it('starts with no current session', () => {
    expect(useConversationStore.getState().session).toBeNull()
  })

  it('setSession replaces the session wholesale', () => {
    const s = session({ status: 'PROPOSAL_READY' })
    useConversationStore.getState().setSession(s)
    expect(useConversationStore.getState().session).toEqual(s)
  })

  it('resetSession clears back to null', () => {
    useConversationStore.getState().setSession(session())
    useConversationStore.getState().resetSession()
    expect(useConversationStore.getState().session).toBeNull()
  })
})
