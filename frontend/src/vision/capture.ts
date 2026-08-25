/**
 * Pure gating logic for presentation image capture — kept separate from
 * ModelViewport so it is unit-testable without a WebGL context. See
 * docs/bible/10-vision/240-stale-and-last-good-preview.md: capture is
 * blocked outright for a stale model rather than silently labeling the
 * output, per that document's stated preference.
 */

export type CaptureBlockedReason = 'no_model' | 'stale' | null

export function captureBlockedReason(hasModel: boolean, isStale: boolean): CaptureBlockedReason {
  if (!hasModel) return 'no_model'
  if (isStale) return 'stale'
  return null
}

export const CAPTURE_BLOCKED_MESSAGES: Record<Exclude<CaptureBlockedReason, null>, string> = {
  no_model: 'Generate a model before capturing a presentation image.',
  stale: 'Parameters changed — regenerate the model before capturing a presentation image.',
}
