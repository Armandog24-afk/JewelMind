import { hasErrors } from '@shared/validation/engine'
import { useProjectStore } from '../store/useProjectStore'

export function ProjectActions() {
  const validationResults = useProjectStore((s) => s.validationResults)
  const generationStatus = useProjectStore((s) => s.generationStatus)
  const generatedModel = useProjectStore((s) => s.generatedModel)
  const isStale = useProjectStore((s) => s.isStale)
  const exportStatus = useProjectStore((s) => s.exportStatus)
  const generate = useProjectStore((s) => s.generate)
  const runExport = useProjectStore((s) => s.runExport)
  const resetProject = useProjectStore((s) => s.resetProject)

  const blockedByErrors = hasErrors(validationResults)
  const canExport = generatedModel !== null && !isStale && !blockedByErrors

  return (
    <div className="project-actions">
      <button
        type="button"
        className="btn btn--primary"
        disabled={blockedByErrors || generationStatus === 'generating'}
        onClick={() => void generate()}
      >
        {generationStatus === 'generating'
          ? 'Generating…'
          : generatedModel
            ? 'Regenerate model'
            : 'Generate model'}
      </button>

      <button
        type="button"
        className="btn"
        disabled={!canExport || exportStatus.step === 'exporting'}
        onClick={() => void runExport('step')}
      >
        Export STEP
      </button>

      <button
        type="button"
        className="btn"
        disabled={!canExport || exportStatus.stl === 'exporting'}
        onClick={() => void runExport('stl')}
      >
        Export STL
      </button>

      <button
        type="button"
        className="btn"
        disabled={!canExport || exportStatus.json === 'exporting'}
        onClick={() => void runExport('json')}
      >
        Export JSON
      </button>

      <button type="button" className="btn btn--ghost btn--danger" onClick={resetProject}>
        Reset project
      </button>
    </div>
  )
}
