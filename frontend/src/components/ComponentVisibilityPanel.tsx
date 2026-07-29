const LABELS: Record<string, string> = {
  band: 'Band',
  stone_reference: 'Stone (reference)',
  prongs: 'Prongs',
  basket_support: 'Basket support',
}

interface ComponentVisibilityPanelProps {
  componentNames: string[]
  visible: Record<string, boolean>
  onToggle: (name: string) => void
}

export function ComponentVisibilityPanel({
  componentNames,
  visible,
  onToggle,
}: ComponentVisibilityPanelProps) {
  if (componentNames.length === 0) return null

  return (
    <div className="component-visibility">
      {componentNames.map((name) => (
        <label key={name}>
          <input
            type="checkbox"
            checked={visible[name] ?? true}
            onChange={() => onToggle(name)}
          />
          {LABELS[name] ?? name}
        </label>
      ))}
    </div>
  )
}
