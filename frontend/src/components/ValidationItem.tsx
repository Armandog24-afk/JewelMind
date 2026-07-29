import type { ValidationResult } from '@shared/validation/rules'

export function ValidationItem({ result }: { result: ValidationResult }) {
  return (
    <div className={`validation-item validation-item--${result.severity}`} role="listitem">
      <span className="validation-item__badge">{result.severity}</span>
      <div className="validation-item__body">
        <span>{result.message}</span>
        <span className="validation-item__rule">
          {result.ruleId} · {result.parameter}
          {result.suggestedValue !== undefined && result.suggestedValue !== null
            ? ` · suggested: ${result.suggestedValue}`
            : ''}
        </span>
      </div>
    </div>
  )
}
