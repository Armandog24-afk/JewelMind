import { useProjectStore } from '../store/useProjectStore'
import { ValidationItem } from './ValidationItem'

export function ValidationPanel() {
  const results = useProjectStore((s) => s.validationResults)

  if (results.length === 0) {
    return <p className="validation-empty">No validation findings — this definition looks good.</p>
  }

  const ordered = [...results].sort((a, b) => {
    const rank = { error: 0, warning: 1, information: 2 } as const
    return rank[a.severity] - rank[b.severity]
  })

  return (
    <div className="validation-list" role="list">
      {ordered.map((result, index) => (
        <ValidationItem key={`${result.ruleId}-${result.parameter}-${index}`} result={result} />
      ))}
    </div>
  )
}
