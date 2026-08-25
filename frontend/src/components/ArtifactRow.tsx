import { OUTPUT_ELIGIBILITY_LABELS, type OutputEligibilityKey } from '../studio/outputEligibility'

interface ArtifactRowProps {
  name: string
  purpose: string
  eligibility: OutputEligibilityKey
  actionLabel: string
  onAction: () => void
  errorMessage?: string | null
}

/**
 * One row in Studio's consolidated Outputs area — every current
 * artifact type (STEP, STL, JSON, technical specification, presentation
 * PNG) renders through this same component, so eligibility wording and
 * button behavior can never drift between artifacts. See
 * docs/bible/11-studio/260-output-review-experience.md and
 * 261-export-experience.md.
 */
export function ArtifactRow({ name, purpose, eligibility, actionLabel, onAction, errorMessage }: ArtifactRowProps) {
  const disabled = eligibility === 'UNAVAILABLE' || eligibility === 'EXPORTING' || eligibility === 'STALE_BLOCKED'
  return (
    <div className={`artifact-row artifact-row--${eligibility.toLowerCase()}`}>
      <div className="artifact-row__info">
        <span className="artifact-row__name">{name}</span>
        <span className="artifact-row__purpose">{purpose}</span>
      </div>
      <div className="artifact-row__action">
        <button type="button" className="btn" disabled={disabled} onClick={onAction}>
          {eligibility === 'EXPORTING' ? 'Preparing…' : actionLabel}
        </button>
        <span className="artifact-row__status">{OUTPUT_ELIGIBILITY_LABELS[eligibility]}</span>
      </div>
      {eligibility === 'FAILED' && errorMessage ? (
        <p className="artifact-row__error" role="alert">
          {errorMessage}
        </p>
      ) : null}
    </div>
  )
}
