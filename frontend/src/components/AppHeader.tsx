import { BackendStatus } from './BackendStatus'
import { ProjectActions } from './ProjectActions'

export function AppHeader() {
  return (
    <header className="app-header">
      <div className="app-header__brand">
        <span className="app-header__title">
          Jewel<span className="app-header__title-mark">Mind</span>
        </span>
        <span className="app-header__subtitle">Parametric jewelry CAD — technical prototype</span>
      </div>
      <ProjectActions />
      <BackendStatus />
    </header>
  )
}
