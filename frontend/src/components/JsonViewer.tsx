import { useProjectStore } from '../store/useProjectStore'

export function JsonViewer() {
  const definition = useProjectStore((s) => s.currentDefinition)
  return <pre className="json-viewer">{JSON.stringify(definition, null, 2)}</pre>
}
