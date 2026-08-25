const LABELS: Record<string, string> = {
  band: 'Band',
  stone_reference: 'Stone (reference)',
  prongs: 'Prongs',
  basket_support: 'Basket support',
}

const STATUS_LABELS: Record<string, string> = {
  SUCCEEDED: '',
  SUCCEEDED_WITH_FALLBACK: ' (fallback used)',
  FAILED: ' (failed)',
  EMPTY: ' (no geometry)',
}

export interface ComponentVisibilityEntry {
  name: string
  generationStatus?: string
}

interface ComponentVisibilityPanelProps {
  components: ComponentVisibilityEntry[]
  metalComponentNames: string[]
  visible: Record<string, boolean>
  onToggle: (name: string) => void
  onShowAll: () => void
  onShowMetalOnly: () => void
  selectedComponent?: string | null
  onSelect?: (name: string | null) => void
}

export function ComponentVisibilityPanel({
  components,
  metalComponentNames,
  visible,
  onToggle,
  onShowAll,
  onShowMetalOnly,
  selectedComponent,
  onSelect,
}: ComponentVisibilityPanelProps) {
  if (components.length === 0) return null

  return (
    <div className="component-visibility">
      <div className="component-visibility__quick-actions">
        <button type="button" className="component-visibility__quick-button" onClick={onShowAll}>
          Show all
        </button>
        <button type="button" className="component-visibility__quick-button" onClick={onShowMetalOnly}>
          Metal only
        </button>
      </div>
      {components.map(({ name, generationStatus }) => (
        <label
          key={name}
          className={`component-visibility__row${selectedComponent === name ? ' component-visibility__row--selected' : ''}${
            metalComponentNames.includes(name) ? '' : ' component-visibility__row--stone'
          }`}
        >
          <input type="checkbox" checked={visible[name] ?? true} onChange={() => onToggle(name)} />
          <span
            onClick={(e) => {
              e.preventDefault()
              onSelect?.(selectedComponent === name ? null : name)
            }}
          >
            {LABELS[name] ?? name}
            {generationStatus ? STATUS_LABELS[generationStatus] ?? '' : ''}
          </span>
        </label>
      ))}
    </div>
  )
}
