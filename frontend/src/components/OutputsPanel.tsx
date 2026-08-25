import { hasErrors } from '@shared/validation/engine'
import { useProjectStore, type ExportKind } from '../store/useProjectStore'
import { useVisionStore } from '../store/useVisionStore'
import { captureBlockedReason } from '../vision/capture'
import { computeOutputEligibility, type OutputEligibilityKey } from '../studio/outputEligibility'
import { ArtifactRow } from './ArtifactRow'

const DOWNLOAD_ARTIFACTS: Array<{ kind: ExportKind; name: string; purpose: string }> = [
  { kind: 'step', name: 'STEP', purpose: 'Neutral CAD exchange for further professional CAD work.' },
  { kind: 'stl', name: 'STL', purpose: 'Tessellated mesh for 3D printing and prototyping workflows.' },
  { kind: 'json', name: 'JDL JSON', purpose: 'The editable JewelMind design definition itself.' },
  { kind: 'specification', name: 'Technical specification', purpose: 'Design and generation information, in one document.' },
]

/**
 * Studio's single, consolidated Outputs area — replaces the previously
 * scattered export buttons (header + tabs + viewport). Every artifact
 * renders through the same ArtifactRow with the same eligibility rule,
 * so the user never has to learn a different pattern per output. See
 * docs/bible/11-studio/260-output-review-experience.md.
 */
export function OutputsPanel() {
  const generatedModel = useProjectStore((s) => s.generatedModel)
  const isStale = useProjectStore((s) => s.isStale)
  const validationResults = useProjectStore((s) => s.validationResults)
  const exportStatus = useProjectStore((s) => s.exportStatus)
  const exportError = useProjectStore((s) => s.exportError)
  const runExport = useProjectStore((s) => s.runExport)

  const lastSuccessfulPreview = useProjectStore((s) => s.lastSuccessfulPreview)
  const setViewMode = useVisionStore((s) => s.setViewMode)
  const requestCapture = useVisionStore((s) => s.requestCapture)

  const hasModel = generatedModel !== null
  const blockingErrors = hasErrors(validationResults)

  function eligibilityFor(kind: ExportKind): OutputEligibilityKey {
    return computeOutputEligibility({
      hasModel,
      isStale,
      hasBlockingValidationErrors: blockingErrors,
      phase: exportStatus[kind],
    })
  }

  const pngBlockedReason = captureBlockedReason(lastSuccessfulPreview !== null, isStale)
  const pngEligibility: OutputEligibilityKey =
    pngBlockedReason === 'no_model' ? 'UNAVAILABLE' : pngBlockedReason === 'stale' ? 'STALE_BLOCKED' : 'AVAILABLE'

  return (
    <div className="outputs-panel">
      <p className="outputs-panel__intro">
        Every output below is generated on demand from the current model — nothing is pre-rendered or cached
        beyond that.
      </p>
      {DOWNLOAD_ARTIFACTS.map(({ kind, name, purpose }) => (
        <ArtifactRow
          key={kind}
          name={name}
          purpose={purpose}
          eligibility={eligibilityFor(kind)}
          actionLabel="Download"
          onAction={() => void runExport(kind)}
          errorMessage={exportError}
        />
      ))}
      <ArtifactRow
        name="Presentation PNG"
        purpose="A visual image of the generated model, captured from the Presentation view."
        eligibility={pngEligibility}
        actionLabel="Save render"
        onAction={() => {
          setViewMode('presentation')
          requestCapture()
        }}
      />
    </div>
  )
}
