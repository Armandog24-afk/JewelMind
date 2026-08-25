import { useProjectStore } from '../store/useProjectStore'
import { computeModelState } from '../studio/modelState'
import { BackendStatus } from './BackendStatus'
import { ModelStatusBadge } from './ModelStatusBadge'
import { ProjectActions } from './ProjectActions'

export function AppHeader() {
  const generationStatus = useProjectStore((s) => s.generationStatus)
  const lastSuccessfulPreview = useProjectStore((s) => s.lastSuccessfulPreview)
  const isStale = useProjectStore((s) => s.isStale)

  const modelState = computeModelState({
    generationStatus,
    hasLastGoodPreview: lastSuccessfulPreview !== null,
    isStale,
  })

  return (
    <header className="app-header">
      <div className="app-header__brand">
        <span className="app-header__title">
          Jewel<span className="app-header__title-mark">Mind</span>
        </span>
        <span className="app-header__subtitle">Parametric jewelry CAD — technical prototype</span>
      </div>
      <ModelStatusBadge state={modelState} />
      <ProjectActions />
      <BackendStatus />
    </header>
  )
}
