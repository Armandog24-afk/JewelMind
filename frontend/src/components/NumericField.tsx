interface NumericFieldProps {
  id: string
  label: string
  value: number
  onChange: (value: number) => void
  min?: number
  max?: number
  step?: number
  unit?: string
  wide?: boolean
}

/**
 * A single numeric design/technical parameter control. Never silently
 * coerces an out-of-range value — the raw value is always passed through
 * to onChange (JDL/Forge remain the authoritative validators, per
 * STUDIO-GOV-001/002), but the field visibly marks itself invalid so the
 * user gets immediate local feedback without waiting for a backend
 * round-trip. See docs/bible/11-studio/257-validation-experience.md.
 */
export function NumericField({
  id,
  label,
  value,
  onChange,
  min,
  max,
  step = 0.1,
  unit,
  wide = false,
}: NumericFieldProps) {
  const outOfRange = (min !== undefined && value < min) || (max !== undefined && value > max)

  return (
    <div className={`form-field${wide ? ' form-field--wide' : ''}`}>
      <label htmlFor={id}>
        {label}
        {unit ? <span className="form-field__unit"> ({unit})</span> : null}
      </label>
      <input
        id={id}
        type="number"
        value={value}
        min={min}
        max={max}
        step={step}
        aria-invalid={outOfRange}
        aria-describedby={outOfRange ? `${id}-error` : undefined}
        className={outOfRange ? 'form-field__input--invalid' : undefined}
        onChange={(event) => {
          const next = event.target.valueAsNumber
          if (!Number.isNaN(next)) onChange(next)
        }}
      />
      {outOfRange ? (
        <span id={`${id}-error`} className="form-field__error" role="alert">
          {min !== undefined && max !== undefined
            ? `Must be between ${min} and ${max}.`
            : min !== undefined
              ? `Must be at least ${min}.`
              : `Must be at most ${max}.`}
        </span>
      ) : null}
    </div>
  )
}
