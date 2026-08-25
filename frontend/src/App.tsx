import { useEffect } from 'react'
import { AppHeader } from './components/AppHeader'
import { ConfigurationPanel } from './components/ConfigurationPanel'
import { ConversationPanel } from './components/ConversationPanel'
import { ModelViewport } from './components/ModelViewport'
import { ProfessionalReviewNotice } from './components/ProfessionalReviewNotice'
import { RightPanelTabs } from './components/RightPanelTabs'
import { useProjectStore } from './store/useProjectStore'

const HEALTH_POLL_INTERVAL_MS = 15_000

function App() {
  const checkBackendHealth = useProjectStore((s) => s.checkBackendHealth)

  useEffect(() => {
    void checkBackendHealth()
    const interval = window.setInterval(() => void checkBackendHealth(), HEALTH_POLL_INTERVAL_MS)
    return () => window.clearInterval(interval)
  }, [checkBackendHealth])

  return (
    <div className="app-shell">
      <AppHeader />
      <div className="app-body">
        <div className="panel panel--left">
          <ProfessionalReviewNotice />
          <ConversationPanel />
          <ConfigurationPanel />
        </div>
        <div className="panel panel--center">
          <ModelViewport />
        </div>
        <div className="panel panel--right">
          <RightPanelTabs />
        </div>
      </div>
    </div>
  )
}

export default App
