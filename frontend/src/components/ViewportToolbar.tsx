interface ViewportToolbarProps {
  onResetCamera: () => void
  onFitToView: () => void
  showGrid: boolean
  onToggleGrid: () => void
  showAxes: boolean
  onToggleAxes: () => void
}

export function ViewportToolbar({
  onResetCamera,
  onFitToView,
  showGrid,
  onToggleGrid,
  showAxes,
  onToggleAxes,
}: ViewportToolbarProps) {
  return (
    <div className="viewport-toolbar">
      <button type="button" className="viewport-toolbar__button" onClick={onResetCamera}>
        Reset camera
      </button>
      <button type="button" className="viewport-toolbar__button" onClick={onFitToView}>
        Fit to view
      </button>
      <button
        type="button"
        className={`viewport-toolbar__button${showGrid ? ' viewport-toolbar__button--active' : ''}`}
        onClick={onToggleGrid}
        aria-pressed={showGrid}
      >
        Grid
      </button>
      <button
        type="button"
        className={`viewport-toolbar__button${showAxes ? ' viewport-toolbar__button--active' : ''}`}
        onClick={onToggleAxes}
        aria-pressed={showAxes}
      >
        Axes
      </button>
    </div>
  )
}
