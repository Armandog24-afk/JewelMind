import { useId, useState } from 'react'
import { generateReviewPackage, triggerBrowserDownload } from '../api/client'
import { ApiError } from '../api/types'
import { computeOutputEligibility, type OutputEligibilityKey } from '../studio/outputEligibility'
import { useProjectStore } from '../store/useProjectStore'
import { ArtifactRow } from './ArtifactRow'

/**
 * Professional Validation Framework v1 (Sprint 13) — the small, targeted
 * Studio surface for putting the current model in front of a real
 * jewelry professional. This does not replace the ordinary Outputs tab;
 * it packages the SAME current, real artifacts (STEP/STL/JDL/technical
 * specification) alongside a Forge report, geometry metadata, and an
 * empty review form, for a reviewer who has never read the Technical
 * Bible. See docs/bible/15-professional-validation/447-studio-professional-review-mode.md.
 *
 * Gated by the exact same eligibility rule as every other export
 * (computeOutputEligibility) — a stale or invalid model can never
 * produce a review package, so a reviewer never receives files that
 * don't match what's on screen.
 */
export function ProfessionalReviewPanel() {
  const caseIdInputId = useId()
  const generatedModel = useProjectStore((s) => s.generatedModel)
  const isStale = useProjectStore((s) => s.isStale)
  const validationResults = useProjectStore((s) => s.validationResults)
  const hasBlockingValidationErrors = validationResults.some((r) => r.severity === 'error')

  const [caseId, setCaseId] = useState('')
  const [phase, setPhase] = useState<'idle' | 'exporting' | 'success' | 'error'>('idle')
  const [error, setError] = useState<string | null>(null)

  const eligibility: OutputEligibilityKey = computeOutputEligibility({
    hasModel: generatedModel !== null,
    isStale,
    hasBlockingValidationErrors,
    phase,
  })

  const handleGenerate = async () => {
    if (!generatedModel) return
    const trimmedCaseId = caseId.trim() || `JMCASE-${generatedModel.definitionHash}`
    setPhase('exporting')
    setError(null)
    try {
      const { blob, filename } = await generateReviewPackage(generatedModel.modelId, trimmedCaseId, true)
      triggerBrowserDownload(blob, filename)
      setPhase('success')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Review package generation failed unexpectedly.')
      setPhase('error')
    }
  }

  return (
    <div className="professional-review-panel">
      <p className="outputs-panel__intro">
        Generates a real package of the current model&rsquo;s artifacts — STEP, STL, the design definition,
        technical specification, geometry data, and an empty review form — for a qualified jewelry
        professional to evaluate. This is not a manufacturing-ready deliverable; JewelMind has not been
        professionally validated.
      </p>

      <div className="professional-review-panel__case">
        <label htmlFor={caseIdInputId}>Review case ID</label>
        <input
          id={caseIdInputId}
          type="text"
          placeholder="e.g. JMCASE001 (optional — a default is used if left blank)"
          value={caseId}
          onChange={(e) => setCaseId(e.target.value)}
          disabled={phase === 'exporting'}
        />
      </div>

      <ArtifactRow
        name="Professional review package"
        purpose="A ZIP with real STEP/STL/JDL/technical-specification/Forge-report artifacts plus a review form."
        eligibility={eligibility}
        actionLabel="Generate review package"
        onAction={() => void handleGenerate()}
        errorMessage={error}
      />
    </div>
  )
}
