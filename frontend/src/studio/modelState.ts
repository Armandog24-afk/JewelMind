/**
 * Pure model-state computation for Studio v1. No React, no store import —
 * takes plain booleans/strings so it is testable in isolation and so the
 * exact same logic can back both a visible status badge and any future
 * consumer (e.g. an export-eligibility check). See
 * docs/bible/11-studio/259-model-state-experience.md.
 */

export type ModelStateKey =
  | 'NO_MODEL'
  | 'GENERATING_FIRST_MODEL'
  | 'CURRENT'
  | 'STALE'
  | 'REGENERATING'
  | 'FAILED_NO_MODEL'
  | 'FAILED_WITH_LAST_GOOD'

export interface ModelStateInput {
  generationStatus: 'idle' | 'generating' | 'success' | 'error'
  hasLastGoodPreview: boolean
  isStale: boolean
}

export interface ModelStateDescriptor {
  key: ModelStateKey
  label: string
  /** A short, plain-language explanation shown alongside the label —
   * the badge must never rely on color alone (STUDIO-GOV-005). */
  detail: string
}

const DESCRIPTORS: Record<ModelStateKey, Omit<ModelStateDescriptor, 'key'>> = {
  NO_MODEL: { label: 'No model yet', detail: 'Configure your design and generate a model to begin.' },
  GENERATING_FIRST_MODEL: { label: 'Generating…', detail: 'Building the first model for this design.' },
  CURRENT: { label: 'Current model', detail: 'This preview matches your current parameters.' },
  STALE: { label: 'Design changed', detail: 'Parameters changed since this model was generated — regenerate to update it.' },
  REGENERATING: { label: 'Regenerating…', detail: 'Your last successful model remains visible while this completes.' },
  FAILED_NO_MODEL: { label: 'Generation failed', detail: 'No model is available yet. Check the parameters and try again.' },
  FAILED_WITH_LAST_GOOD: {
    label: 'Regeneration failed',
    detail: 'The last successful model is still shown below. Check the parameters and try again.',
  },
}

/** The single source of truth for "what state is the model in", per
 * STUDIO-GOV-005/006: a stale model must never be presented as current,
 * and the last successful model may remain visible after a failure. */
export function computeModelState(input: ModelStateInput): ModelStateKey {
  const { generationStatus, hasLastGoodPreview, isStale } = input

  if (generationStatus === 'generating') {
    return hasLastGoodPreview ? 'REGENERATING' : 'GENERATING_FIRST_MODEL'
  }
  if (!hasLastGoodPreview) {
    return generationStatus === 'error' ? 'FAILED_NO_MODEL' : 'NO_MODEL'
  }
  // A new edit always supersedes a stale reading of a past failure — the
  // user is now iterating on parameters the failed attempt never saw.
  if (isStale) {
    return 'STALE'
  }
  if (generationStatus === 'error') {
    return 'FAILED_WITH_LAST_GOOD'
  }
  return 'CURRENT'
}

export function describeModelState(key: ModelStateKey): ModelStateDescriptor {
  return { key, ...DESCRIPTORS[key] }
}
