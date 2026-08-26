import { useState } from 'react'
import { useProjectStore } from '../store/useProjectStore'
import { JsonViewer } from './JsonViewer'
import { ModelInformation } from './ModelInformation'
import { OutputsPanel } from './OutputsPanel'
import { ProfessionalReviewPanel } from './ProfessionalReviewPanel'
import { TechnicalSpecification } from './TechnicalSpecification'
import { ValidationPanel } from './ValidationPanel'

type TabKey = 'validation' | 'outputs' | 'specification' | 'json' | 'model-info' | 'review'

const TABS: Array<{ key: TabKey; label: string }> = [
  { key: 'validation', label: 'Validation' },
  { key: 'outputs', label: 'Outputs' },
  { key: 'specification', label: 'Specification' },
  { key: 'json', label: 'JSON' },
  { key: 'model-info', label: 'Model info' },
  { key: 'review', label: 'Review' },
]

export function RightPanelTabs() {
  const [active, setActive] = useState<TabKey>('validation')
  const validationResults = useProjectStore((s) => s.validationResults)
  const errorCount = validationResults.filter((r) => r.severity === 'error').length

  return (
    <>
      <div className="tabs" role="tablist">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            type="button"
            role="tab"
            aria-selected={active === tab.key}
            className={`tabs__button${active === tab.key ? ' tabs__button--active' : ''}`}
            onClick={() => setActive(tab.key)}
          >
            {tab.label}
            {tab.key === 'validation' && errorCount > 0 ? ` (${errorCount})` : ''}
          </button>
        ))}
      </div>
      <div className="tab-panel" role="tabpanel">
        {active === 'validation' ? <ValidationPanel /> : null}
        {active === 'outputs' ? <OutputsPanel /> : null}
        {active === 'specification' ? <TechnicalSpecification /> : null}
        {active === 'json' ? <JsonViewer /> : null}
        {active === 'model-info' ? <ModelInformation /> : null}
        {active === 'review' ? <ProfessionalReviewPanel /> : null}
      </div>
    </>
  )
}
