import { useEffect, useState } from 'react'
import { fetchSpecificationText } from '../api/client'
import { useProjectStore } from '../store/useProjectStore'

export function TechnicalSpecification() {
  const generatedModel = useProjectStore((s) => s.generatedModel)
  const [text, setText] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!generatedModel) {
      setText(null)
      return
    }
    let cancelled = false
    setError(null)
    fetchSpecificationText(generatedModel.modelId)
      .then((value) => {
        if (!cancelled) setText(value)
      })
      .catch(() => {
        if (!cancelled) setError('Could not load the technical specification from the backend.')
      })
    return () => {
      cancelled = true
    }
  }, [generatedModel])

  if (!generatedModel) {
    return <p className="empty-state">Generate a model to view its technical specification.</p>
  }

  if (error) {
    return <p className="empty-state">{error}</p>
  }

  if (text === null) {
    return <p className="empty-state">Loading specification…</p>
  }

  return <pre className="spec-viewer">{text}</pre>
}
