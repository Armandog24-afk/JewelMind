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
        onChange={(event) => {
          const next = event.target.valueAsNumber
          if (!Number.isNaN(next)) onChange(next)
        }}
      />
    </div>
  )
}
