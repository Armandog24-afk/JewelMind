import { create } from 'zustand'
import type { DesignIntent } from '../api/types'

/**
 * Design Intent state — Sprint 11 (Design Intent Model v1). Deliberately
 * separate from `useProjectStore` (JDL/design state) and `useVisionStore`
 * (visual-only state): a `DesignIntent` is neither. Applying it never
 * marks the current generated model stale and never touches
 * `currentDefinition` — see docs/bible/13-design-intent/353-intent-preservation.md
 * and INTENT-GOV-004 ("Intent and JDL must remain separate models").
 *
 * Not persisted across page reloads in v1 — a real, deliberate scope
 * limit, not an oversight; see docs/bible/13-design-intent/321 (Designer)
 * and 362 (Design Intent) gap analyses.
 */

interface DesignIntentState {
  currentIntent: DesignIntent | null

  applyIntent: (intent: DesignIntent) => void
  removeStatement: (intentId: string) => void
  removeUnresolvedDescriptor: (text: string) => void
  clearIntent: () => void
}

export const useDesignIntentStore = create<DesignIntentState>((set) => ({
  currentIntent: null,

  applyIntent: (intent) => set({ currentIntent: intent }),

  removeStatement: (intentId) =>
    set((state) => {
      if (!state.currentIntent) return state
      return {
        currentIntent: {
          ...state.currentIntent,
          statements: state.currentIntent.statements.filter((s) => s.intentId !== intentId),
        },
      }
    }),

  removeUnresolvedDescriptor: (text) =>
    set((state) => {
      if (!state.currentIntent) return state
      return {
        currentIntent: {
          ...state.currentIntent,
          unresolvedDescriptors: state.currentIntent.unresolvedDescriptors.filter((d) => d !== text),
        },
      }
    }),

  clearIntent: () => set({ currentIntent: null }),
}))
