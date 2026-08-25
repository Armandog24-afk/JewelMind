import { useId, useState, type FormEvent } from 'react'
import { interpretDesignRequest } from '../api/client'
import { ApiError } from '../api/types'
import type { DesignerInteractionMode, DesignerResult, IntentStatement, ProposedField } from '../api/types'
import { useDesignIntentStore } from '../store/useDesignIntentStore'
import { useProjectStore } from '../store/useProjectStore'

/**
 * Designer v1's natural-language entry point into Studio. This is another
 * way to edit the structured design, not a chatbot replacing the
 * parameter editor — ConfigurationPanel stays visible and authoritative at
 * all times, before, during, and after a proposal review. Sprint 11 (Design
 * Intent Model) adds a second, explicitly separate review section for
 * aesthetic intent — never merged into the technical field list, and never
 * converted into a dimension. See docs/bible/12-designer/310-user-review-and-acceptance.md,
 * docs/bible/13-design-intent/357-studio-intent-review.md.
 */

const PROVENANCE_LABEL: Record<string, string> = {
  AI_INTERPRETATION: 'From your description',
  USER_EXPLICIT: 'From your description',
  USER_CONTEXT: 'From your description',
  CLARIFICATION_RESPONSE: 'From your answer',
  CURRENT_DESIGN: 'Kept from the current design',
  SYSTEM_DEFAULT: 'System default',
  DETERMINISTIC_DERIVATION: 'Derived automatically',
  UNRESOLVED: 'Not yet mapped to a technical parameter',
}

function fieldLabel(field: ProposedField): string {
  return PROVENANCE_LABEL[field.provenance] ?? field.provenance
}

const RESOLUTION_LABEL: Record<string, string> = {
  PRESERVED: 'Preserved — not yet technically resolved',
  CONFLICTING: 'Conflicting — needs your attention',
  UNRESOLVED: 'Unresolved',
  UNSUPPORTED: 'Not currently supported',
  DETERMINISTICALLY_RESOLVED: 'Resolved',
  USER_RESOLVED: 'Resolved by you',
  PROFILE_RESOLVED: 'Resolved from a profile',
}

function resolutionLabel(statement: IntentStatement): string {
  return RESOLUTION_LABEL[statement.resolutionStatus] ?? statement.resolutionStatus
}

function intentStatementLabel(statement: IntentStatement): string {
  const concept = statement.concept.replace(/_/g, ' ').toLowerCase()
  const target = statement.target.replace(/_/g, ' ').toLowerCase()
  const value = statement.value.replace(/_/g, ' ').toLowerCase()
  return `${target}: ${value} (${concept})`
}

export function DesignerPanel() {
  const textId = useId()
  const applyDesignerProposal = useProjectStore((s) => s.applyDesignerProposal)
  const currentDefinition = useProjectStore((s) => s.currentDefinition)
  const currentIntent = useDesignIntentStore((s) => s.currentIntent)
  const applyIntent = useDesignIntentStore((s) => s.applyIntent)
  const removeStatement = useDesignIntentStore((s) => s.removeStatement)
  const removeUnresolvedDescriptor = useDesignIntentStore((s) => s.removeUnresolvedDescriptor)

  const [text, setText] = useState('')
  const [mode, setMode] = useState<DesignerInteractionMode>('MODIFY')
  const [isLoading, setIsLoading] = useState(false)
  const [providerUnavailable, setProviderUnavailable] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<DesignerResult | null>(null)

  const runInterpret = async (requestText: string) => {
    if (!requestText.trim()) return
    setIsLoading(true)
    setError(null)
    setProviderUnavailable(false)
    try {
      const response = await interpretDesignRequest({
        requestId: `req-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        text: requestText,
        interactionMode: mode,
        // Always sent, regardless of mode: CREATE still starts from schema
        // defaults (base construction is unaffected), but the backend uses
        // this to diff the proposal against what's actually loaded right
        // now — the signal handleApply() below uses to decide whether
        // applying should mark the current model stale. See
        // docs/bible/13-design-intent/353-intent-preservation.md.
        currentJDL: currentDefinition,
        currentDesignIntent: currentIntent,
      })
      setResult(response)
    } catch (err) {
      if (err instanceof ApiError && err.code === 'DESIGNER_PROVIDER_UNAVAILABLE') {
        setProviderUnavailable(true)
      } else if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError('Could not reach the JewelMind backend.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    void runInterpret(text)
  }

  const handleClarify = (option: string) => {
    const nextText = `${text} ${option}`.trim()
    setText(nextText)
    void runInterpret(nextText)
  }

  const handleApply = () => {
    const proposal = result?.proposal
    if (!proposal) return

    // Only touch JDL/staleness when a real technical field actually
    // changed — a pure design-intent request (e.g. "make it more minimal")
    // must never mark the current model stale. See
    // docs/bible/13-design-intent/353-intent-preservation.md and
    // INTENT-GOV: "intent-only changes must not mark geometry stale."
    const hasTechnicalChange = proposal.diff.some((d) => d.changed)
    if (proposal.candidateJDL && hasTechnicalChange) {
      applyDesignerProposal(proposal.candidateJDL)
    }

    const intent = proposal.designIntent
    const hasIntentContent =
      intent.statements.length > 0 || intent.relationships.length > 0 || intent.unresolvedDescriptors.length > 0
    if (hasIntentContent) {
      applyIntent(intent)
    }

    setResult(null)
    setText('')
  }

  const handleCancel = () => {
    setResult(null)
  }

  const proposal = result?.proposal ?? null
  const forgeErrorCount = proposal?.forgeEvaluation?.results.filter((r) => r.severity === 'error').length ?? 0
  const forgeWarningCount = proposal?.forgeEvaluation?.results.filter((r) => r.severity === 'warning').length ?? 0

  return (
    <section className="designer-panel" aria-label="Describe your design">
      <h2 className="designer-panel__title">Designer</h2>
      <p className="designer-panel__hint">
        Describe your design or a change to it, in Italian or English. JewelMind proposes structured
        values for you to review — it never changes the design without your approval.
      </p>

      <form className="designer-panel__form" onSubmit={handleSubmit}>
        <label htmlFor={textId} className="sr-only">
          Describe your design or change
        </label>
        <textarea
          id={textId}
          className="designer-panel__textarea"
          placeholder="Describe your design or change…"
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={2}
          disabled={isLoading}
        />
        <div className="designer-panel__controls">
          <div className="designer-panel__mode" role="radiogroup" aria-label="Interpretation mode">
            <label>
              <input
                type="radio"
                name="designer-mode"
                checked={mode === 'MODIFY'}
                onChange={() => setMode('MODIFY')}
              />
              Modify current design
            </label>
            <label>
              <input
                type="radio"
                name="designer-mode"
                checked={mode === 'CREATE'}
                onChange={() => setMode('CREATE')}
              />
              Start new from defaults
            </label>
          </div>
          <button type="submit" className="btn btn--primary" disabled={isLoading || !text.trim()}>
            {isLoading ? 'Interpreting…' : 'Interpret'}
          </button>
        </div>
      </form>

      {providerUnavailable ? (
        <p className="designer-panel__unavailable" role="status">
          AI interpretation is unavailable in this environment (no Designer provider is configured).
          You can still describe your design manually using the parameters below.
        </p>
      ) : null}

      {error ? (
        <p className="designer-panel__error" role="alert">
          {error}
        </p>
      ) : null}

      {!proposal &&
      currentIntent &&
      (currentIntent.statements.length > 0 || currentIntent.unresolvedDescriptors.length > 0) ? (
        <div className="designer-intent-summary" role="region" aria-label="Current design intent">
          <h3>Design intent</h3>
          <ul className="designer-intent-summary__tags">
            {currentIntent.statements.map((s) => (
              <li key={s.intentId} className="designer-intent-summary__tag">
                <span>{intentStatementLabel(s)}</span>
                <button
                  type="button"
                  className="designer-intent-summary__remove"
                  aria-label={`Remove ${intentStatementLabel(s)} from design intent`}
                  onClick={() => removeStatement(s.intentId)}
                >
                  ×
                </button>
              </li>
            ))}
            {currentIntent.unresolvedDescriptors.map((d) => (
              <li key={d} className="designer-intent-summary__tag designer-intent-summary__tag--unresolved">
                <span>{d} (unresolved)</span>
                <button
                  type="button"
                  className="designer-intent-summary__remove"
                  aria-label={`Remove ${d} from design intent`}
                  onClick={() => removeUnresolvedDescriptor(d)}
                >
                  ×
                </button>
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      {proposal ? (
        <div className="designer-proposal" role="region" aria-label="Design proposal review">
          <div className="designer-proposal__section">
            <h3>You asked</h3>
            <p className="designer-proposal__source-text">&ldquo;{proposal.sourceText}&rdquo;</p>
          </div>

          {proposal.proposedFields.length > 0 ? (
            <div className="designer-proposal__section">
              <h3>JewelMind understood</h3>
              <ul className="designer-proposal__field-list">
                {proposal.proposedFields.map((field) => (
                  <li key={field.path}>
                    <span className="designer-proposal__field-path">{field.path}</span>
                    <span className="designer-proposal__field-value">{String(field.value)}</span>
                    <span className="designer-proposal__field-provenance">{fieldLabel(field)}</span>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          {proposal.designIntent.statements.length > 0 ? (
            <div className="designer-proposal__section">
              <h3>Design intent</h3>
              <ul className="designer-proposal__field-list">
                {proposal.designIntent.statements.map((s) => (
                  <li key={s.intentId}>
                    <span className="designer-proposal__field-path">{intentStatementLabel(s)}</span>
                    <span className="designer-proposal__field-provenance">{resolutionLabel(s)}</span>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          {proposal.designIntent.conflicts.length > 0 ? (
            <div className="designer-proposal__section designer-proposal__section--unsupported">
              <h3>Conflicting intent</h3>
              <ul className="designer-proposal__plain-list">
                {proposal.designIntent.conflicts.map((c) => (
                  <li key={c.conflictId}>{c.description}</li>
                ))}
              </ul>
            </div>
          ) : null}

          {proposal.designIntent.unresolvedDescriptors.length > 0 ? (
            <div className="designer-proposal__section">
              <h3>Not yet mapped to a technical parameter</h3>
              <ul className="designer-proposal__plain-list">
                {proposal.designIntent.unresolvedDescriptors.map((d) => (
                  <li key={d}>
                    &lsquo;{d}&rsquo; has been preserved as design intent. JewelMind does not currently
                    convert this subjective preference into arbitrary dimensions.
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          {proposal.clarificationQuestions.length > 0 ? (
            <div className="designer-proposal__section">
              <h3>A few questions</h3>
              {proposal.clarificationQuestions.map((q, i) => (
                <div key={`${q.field ?? 'q'}-${i}`} className="designer-proposal__clarification">
                  <p>{q.question}</p>
                  {q.options.length > 0 ? (
                    <div className="designer-proposal__clarification-options">
                      {q.options.map((option) => (
                        <button
                          key={option}
                          type="button"
                          className="btn btn--ghost"
                          onClick={() => handleClarify(option)}
                          disabled={isLoading}
                        >
                          {option}
                        </button>
                      ))}
                    </div>
                  ) : null}
                </div>
              ))}
            </div>
          ) : null}

          {proposal.unsupportedFeatures.length > 0 ? (
            <div className="designer-proposal__section designer-proposal__section--unsupported">
              <h3>Not currently supported</h3>
              <ul className="designer-proposal__plain-list">
                {proposal.unsupportedFeatures.map((f) => (
                  <li key={f.feature}>
                    {f.feature} — {f.reason}
                    {f.suggestedSupportedAlternative ? ` Consider: ${f.suggestedSupportedAlternative}.` : ''}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          {proposal.candidateJDL ? (
            <p className="designer-proposal__forge-summary">
              Design rule check: {forgeErrorCount} error{forgeErrorCount === 1 ? '' : 's'},{' '}
              {forgeWarningCount} warning{forgeWarningCount === 1 ? '' : 's'} — full detail in the
              Validation tab after applying.
            </p>
          ) : (
            <p className="designer-proposal__forge-summary" role="alert">
              The proposed values could not form a valid design. Nothing will be applied.
            </p>
          )}

          <div className="designer-proposal__actions">
            <button
              type="button"
              className="btn btn--primary"
              onClick={handleApply}
              disabled={!proposal.candidateJDL || proposal.proposalStatus === 'NEEDS_CLARIFICATION'}
            >
              Apply proposal
            </button>
            <button type="button" className="btn btn--ghost" onClick={handleCancel}>
              Cancel
            </button>
          </div>
        </div>
      ) : null}
    </section>
  )
}
