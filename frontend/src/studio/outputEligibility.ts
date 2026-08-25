/**
 * Pure output/artifact eligibility computation for Studio v1's
 * consolidated Outputs area. See
 * docs/bible/11-studio/261-export-experience.md.
 */

export type OutputEligibilityKey = 'AVAILABLE' | 'UNAVAILABLE' | 'EXPORTING' | 'FAILED' | 'STALE_BLOCKED'

export interface OutputEligibilityInput {
  hasModel: boolean
  isStale: boolean
  hasBlockingValidationErrors: boolean
  phase: 'idle' | 'exporting' | 'success' | 'error'
}

/** Same precedence for every artifact type (STEP, STL, JSON, technical
 * specification, presentation PNG) — a single rule, not one ad hoc
 * check per button, so the Outputs panel can never show two artifacts
 * disagreeing about whether "now" is a safe time to export. */
export function computeOutputEligibility(input: OutputEligibilityInput): OutputEligibilityKey {
  const { hasModel, isStale, hasBlockingValidationErrors, phase } = input

  if (phase === 'exporting') return 'EXPORTING'
  if (!hasModel) return 'UNAVAILABLE'
  if (isStale || hasBlockingValidationErrors) return 'STALE_BLOCKED'
  if (phase === 'error') return 'FAILED'
  return 'AVAILABLE'
}

export const OUTPUT_ELIGIBILITY_LABELS: Record<OutputEligibilityKey, string> = {
  AVAILABLE: 'Available',
  UNAVAILABLE: 'Generate a model first',
  EXPORTING: 'Preparing…',
  FAILED: 'Last attempt failed — try again',
  STALE_BLOCKED: 'Design changed — regenerate first',
}
