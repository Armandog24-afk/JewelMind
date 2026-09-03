interface TextFieldProps {
  id: string
  label: string
  value: string
  onChange: (value: string) => void
  placeholder?: string
  maxLength?: number
  /** When true, an empty value is marked invalid with an inline message. */
  required?: boolean
  wide?: boolean
}

/**
 * A single free-text design parameter control.
 *
 * Introduced in Sprint 21 for the custom gem's material name — the first field
 * in JewelMind whose value is genuinely a user's own words rather than a number
 * or an enum choice.
 *
 * Mirrors `NumericField`'s discipline exactly: the raw value is ALWAYS passed
 * through to `onChange` and never silently coerced or trimmed, because JDL and
 * Forge remain the authoritative validators (STUDIO-GOV-001/002). The field
 * marks itself invalid for immediate local feedback, without waiting for a
 * backend round trip, and without pretending its own check is the real one.
 *
 * A real, labelled, keyboard-focusable input with an explicit `htmlFor`
 * association, per the accessibility contract (STUDIO-GOV-014).
 */
export function TextField({
  id,
  label,
  value,
  onChange,
  placeholder,
  maxLength = 120,
  required = false,
  wide = false,
}: TextFieldProps) {
  const missing = required && value.trim().length === 0

  return (
    <div className={`form-field${wide ? ' form-field--wide' : ''}`}>
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        type="text"
        value={value}
        placeholder={placeholder}
        maxLength={maxLength}
        aria-invalid={missing}
        aria-describedby={missing ? `${id}-error` : undefined}
        className={missing ? 'form-field__input--invalid' : undefined}
        onChange={(event) => onChange(event.target.value)}
      />
      {missing ? (
        <span id={`${id}-error`} className="form-field__error" role="alert">
          This field is required.
        </span>
      ) : null}
    </div>
  )
}
