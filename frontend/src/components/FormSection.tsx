import type { ReactNode } from 'react'

interface FormSectionProps {
  title: string
  children: ReactNode
}

export function FormSection({ title, children }: FormSectionProps) {
  return (
    <section className="form-section">
      <h3 className="form-section__title">{title}</h3>
      <div className="form-grid">{children}</div>
    </section>
  )
}
