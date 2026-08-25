import { create } from 'zustand'
import type { ConversationSession } from '../api/types'

/**
 * Conversation interaction state — Sprint 12 (Conversation Engine v1).
 * Deliberately separate from `useProjectStore` (JDL/design state) and
 * `useDesignIntentStore` (semantic intent state): a `ConversationSession`
 * is neither of those, it only ever tracks interaction/turn history (see
 * docs/bible/14-conversation/372-conversation-domain-model.md, CONV-GOV-001/002/003
 * and the Sprint 12 brief's state-ownership rule, section 55).
 *
 * The backend is stateless per request — this store is the only place the
 * full `ConversationSession` lives between turns; it round-trips through
 * the API on every call. Not persisted across page reloads in v1, the
 * same deliberate scope limit `useDesignIntentStore` already documents.
 */

interface ConversationState {
  session: ConversationSession | null

  setSession: (session: ConversationSession) => void
  resetSession: () => void
}

export const useConversationStore = create<ConversationState>((set) => ({
  session: null,

  setSession: (session) => set({ session }),

  resetSession: () => set({ session: null }),
}))
