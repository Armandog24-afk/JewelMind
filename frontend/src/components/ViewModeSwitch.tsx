import type { ViewMode } from '../vision/types'

interface ViewModeSwitchProps {
  viewMode: ViewMode
  onChange: (mode: ViewMode) => void
}

export function ViewModeSwitch({ viewMode, onChange }: ViewModeSwitchProps) {
  return (
    <div className="view-mode-switch" role="tablist" aria-label="Viewer mode">
      <button
        type="button"
        role="tab"
        aria-selected={viewMode === 'technical'}
        className={`view-mode-switch__button${viewMode === 'technical' ? ' view-mode-switch__button--active' : ''}`}
        onClick={() => onChange('technical')}
      >
        Technical
      </button>
      <button
        type="button"
        role="tab"
        aria-selected={viewMode === 'presentation'}
        className={`view-mode-switch__button${viewMode === 'presentation' ? ' view-mode-switch__button--active' : ''}`}
        onClick={() => onChange('presentation')}
      >
        Presentation
      </button>
    </div>
  )
}
