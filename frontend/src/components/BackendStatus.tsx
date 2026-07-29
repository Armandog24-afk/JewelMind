import { useProjectStore } from '../store/useProjectStore'

const LABELS = {
  checking: 'Checking backend…',
  online: 'Backend online',
  offline: 'Backend unreachable',
} as const

export function BackendStatus() {
  const status = useProjectStore((s) => s.backendStatus)
  return (
    <div className="backend-status" role="status">
      <span className={`backend-status__dot backend-status__dot--${status}`} />
      <span>{LABELS[status]}</span>
    </div>
  )
}
