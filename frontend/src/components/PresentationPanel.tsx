const METAL_LABELS: Record<string, string> = {
  yellow_gold_18k: 'Yellow gold 18k',
  white_gold_18k: 'White gold 18k',
  rose_gold_18k: 'Rose gold 18k',
  platinum: 'Platinum',
  silver: 'Silver',
}

interface PresentationPanelProps {
  metal: string
  onCapture: () => void
  captureDisabled: boolean
  captureDisabledReason: string | null
  isCapturing: boolean
}

export function PresentationPanel({
  metal,
  onCapture,
  captureDisabled,
  captureDisabledReason,
  isCapturing,
}: PresentationPanelProps) {
  return (
    <div className="presentation-panel">
      <div className="presentation-panel__metal">{METAL_LABELS[metal] ?? metal}</div>
      <button
        type="button"
        className="presentation-panel__capture-button"
        onClick={onCapture}
        disabled={captureDisabled}
        title={captureDisabled ? (captureDisabledReason ?? undefined) : 'Save a PNG of the current presentation view'}
      >
        {isCapturing ? 'Rendering…' : 'Save render'}
      </button>
      {captureDisabled && captureDisabledReason ? (
        <p className="presentation-panel__hint">{captureDisabledReason}</p>
      ) : null}
    </div>
  )
}
