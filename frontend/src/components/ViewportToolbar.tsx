import { CAMERA_PRESET_KEYS, CAMERA_PRESET_LABELS } from '../vision/camera'
import type { CameraPresetKey, ViewMode } from '../vision/types'

interface ViewportToolbarProps {
  viewMode: ViewMode
  onCameraPreset: (preset: CameraPresetKey) => void
  onResetCamera: () => void
  onFitToView: () => void
  showGrid: boolean
  onToggleGrid: () => void
  showAxes: boolean
  onToggleAxes: () => void
}

export function ViewportToolbar({
  viewMode,
  onCameraPreset,
  onResetCamera,
  onFitToView,
  showGrid,
  onToggleGrid,
  showAxes,
  onToggleAxes,
}: ViewportToolbarProps) {
  return (
    <div className="viewport-toolbar" role="toolbar" aria-label="Camera and viewport controls">
      {CAMERA_PRESET_KEYS.map((preset) => (
        <button
          key={preset}
          type="button"
          className="viewport-toolbar__button"
          onClick={() => onCameraPreset(preset)}
          title={`${CAMERA_PRESET_LABELS[preset]} camera`}
        >
          {CAMERA_PRESET_LABELS[preset]}
        </button>
      ))}
      <span className="viewport-toolbar__divider" aria-hidden="true" />
      <button type="button" className="viewport-toolbar__button" onClick={onFitToView} title="Fit camera to the generated model">
        Fit
      </button>
      <button type="button" className="viewport-toolbar__button" onClick={onResetCamera} title="Reset camera to the default view">
        Reset
      </button>
      {viewMode === 'technical' ? (
        <>
          <span className="viewport-toolbar__divider" aria-hidden="true" />
          <button
            type="button"
            className={`viewport-toolbar__button${showGrid ? ' viewport-toolbar__button--active' : ''}`}
            onClick={onToggleGrid}
            aria-pressed={showGrid}
            title="Toggle reference grid"
          >
            Grid
          </button>
          <button
            type="button"
            className={`viewport-toolbar__button${showAxes ? ' viewport-toolbar__button--active' : ''}`}
            onClick={onToggleAxes}
            aria-pressed={showAxes}
            title="Toggle axes helper"
          >
            Axes
          </button>
        </>
      ) : null}
    </div>
  )
}
