import { hasErrors } from '@shared/validation/engine'
import { useProjectStore } from '../store/useProjectStore'

/**
 * Studio v1: the single, obvious primary generation action, plus Reset.
 * Per-artifact export actions moved to the consolidated Outputs tab
 * (see OutputsPanel.tsx) — see
 * docs/bible/11-studio/261-export-experience.md for why scattering
 * export buttons across the header was replaced.
 */
export function ProjectActions() {
  const validationResults = useProjectStore((s) => s.validationResults)
  const generationStatus = useProjectStore((s) => s.generationStatus)
  const generatedModel = useProjectStore((s) => s.generatedModel)
  const generate = useProjectStore((s) => s.generate)
  const resetProject = useProjectStore((s) => s.resetProject)

  const blockedByErrors = hasErrors(validationResults)

  function handleReset() {
    const confirmed = window.confirm(
      'Reset the current design? This discards your parameters and any generated model, and cannot be undone.',
    )
    if (confirmed) resetProject()
  }

  return (
    <div className="project-actions">
      <button
        type="button"
        className="btn btn--primary"
        disabled={blockedByErrors || generationStatus === 'generating'}
        title={
          blockedByErrors
            ? 'Resolve the blocking validation errors first'
            : 'Generate the model (shortcut: G, while not typing in a field)'
        }
        onClick={() => void generate()}
      >
        {generationStatus === 'generating'
          ? 'Generating…'
          : generatedModel
            ? 'Regenerate model'
            : 'Generate model'}
      </button>

      <button type="button" className="btn btn--ghost btn--danger" onClick={handleReset}>
        Reset project
      </button>
    </div>
  )
}
