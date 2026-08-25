import { describeModelState, type ModelStateKey } from '../studio/modelState'

const TONE: Record<ModelStateKey, 'neutral' | 'success' | 'warning' | 'error' | 'progress'> = {
  NO_MODEL: 'neutral',
  GENERATING_FIRST_MODEL: 'progress',
  CURRENT: 'success',
  STALE: 'warning',
  REGENERATING: 'progress',
  FAILED_NO_MODEL: 'error',
  FAILED_WITH_LAST_GOOD: 'error',
}

interface ModelStatusBadgeProps {
  state: ModelStateKey
}

/**
 * The single, centralized "what state is my model in" indicator —
 * STUDIO-GOV-005 requires this distinction to never rely on color alone,
 * so every state always renders both a short label and a plain-language
 * detail sentence, never a bare dot or icon.
 */
export function ModelStatusBadge({ state }: ModelStatusBadgeProps) {
  const { label, detail } = describeModelState(state)
  const tone = TONE[state]
  return (
    <div className={`model-status model-status--${tone}`} role="status" aria-live="polite">
      <span className="model-status__label">{label}</span>
      <span className="model-status__detail">{detail}</span>
    </div>
  )
}
