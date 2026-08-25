import { useId, useState, type FormEvent } from 'react'
import { interpretConversationTurn } from '../api/client'
import { ApiError } from '../api/types'
import type { ConversationResult, ConversationTurn, DesignerProposal, DesignIntent } from '../api/types'
import { useConversationStore } from '../store/useConversationStore'
import { useDesignIntentStore } from '../store/useDesignIntentStore'
import { useProjectStore } from '../store/useProjectStore'

/**
 * Conversation Engine v1's multi-turn natural-language entry point into
 * Studio — supersedes Designer's single-turn DesignerPanel as the mounted
 * "describe your design" surface (DesignerPanel itself remains a valid,
 * separately-tested component; it is simply no longer the one App.tsx
 * renders). ConfigurationPanel stays visible and authoritative at all
 * times, before, during, and after a turn.
 *
 * Every turn resolves into one structured `ConversationActionType` — this
 * component only ever displays that structure (turn history, a
 * clarification card, a proposal review card); it never treats prose as
 * the source of truth. See docs/bible/14-conversation/395-studio-integration.md
 * and CONV-GOV-005 (an unaccepted proposal never silently mutates the
 * current design).
 */

function emptyDesignIntent(): DesignIntent {
  return {
    version: '1.0.0',
    sourceText: '',
    statements: [],
    relationships: [],
    unresolvedDescriptors: [],
    conflicts: [],
    profile: null,
    diagnostics: [],
  }
}

const ACTION_LABEL: Record<string, string> = {
  CREATE_DESIGN_PROPOSAL: 'New design proposed',
  MODIFY_DESIGN_PROPOSAL: 'Change proposed',
  ADD_INTENT: 'Style preference added',
  MODIFY_INTENT: 'Style preference updated',
  REMOVE_INTENT: 'Style preference removed',
  PRESERVE_TARGET: 'Kept as-is',
  REQUEST_CLARIFICATION: 'Question',
  ANSWER_CLARIFICATION: 'Answer received',
  REPORT_UNSUPPORTED: 'Not currently supported',
  ACCEPT_PROPOSAL: 'Applied',
  REJECT_PROPOSAL: 'Discarded',
  CANCEL_INTERACTION: 'Cancelled',
  NO_CHANGE: 'No change',
}

function actionLabel(turn: ConversationTurn): string {
  return ACTION_LABEL[turn.interpretedAction] ?? turn.interpretedAction
}

function fieldLabel(path: string): string {
  return path
    .split('.')
    .join(' ')
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .toLowerCase()
}

function applyDesignerProposalResult(
  proposal: DesignerProposal,
  applyDefinition: (definition: NonNullable<DesignerProposal['candidateJDL']>) => void,
  applyIntent: (intent: DesignIntent) => void,
): void {
  // Only touch JDL/staleness when a real technical field actually
  // changed — a pure design-intent turn must never mark the current
  // model stale. See docs/bible/13-design-intent/353-intent-preservation.md
  // and CONV-GOV-011/012.
  const hasTechnicalChange = proposal.diff.some((d) => d.changed)
  if (proposal.candidateJDL && hasTechnicalChange) {
    applyDefinition(proposal.candidateJDL)
  }

  const intent = proposal.designIntent
  const hasIntentContent =
    intent.statements.length > 0 || intent.relationships.length > 0 || intent.unresolvedDescriptors.length > 0
  if (hasIntentContent) {
    applyIntent(intent)
  }
}

export function ConversationPanel() {
  const textId = useId()
  const session = useConversationStore((s) => s.session)
  const setSession = useConversationStore((s) => s.setSession)
  const applyDesignerProposal = useProjectStore((s) => s.applyDesignerProposal)
  const currentDefinition = useProjectStore((s) => s.currentDefinition)
  const currentIntent = useDesignIntentStore((s) => s.currentIntent)
  const applyIntent = useDesignIntentStore((s) => s.applyIntent)

  const [text, setText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [providerUnavailable, setProviderUnavailable] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const sendTurn = async (turnText: string): Promise<ConversationResult | null> => {
    if (!turnText.trim()) return null
    setIsLoading(true)
    setError(null)
    setProviderUnavailable(false)
    try {
      const response = await interpretConversationTurn({
        text: turnText,
        currentJDL: currentDefinition,
        currentDesignIntent: currentIntent ?? emptyDesignIntent(),
        session,
      })
      setSession(response.session)
      return response
    } catch (err) {
      if (err instanceof ApiError && err.code === 'DESIGNER_PROVIDER_UNAVAILABLE') {
        setProviderUnavailable(true)
      } else if (err instanceof ApiError && err.code === 'CONVERSATION_STALE_CONTEXT') {
        setError('The design changed since this proposal was created — please describe the change again.')
      } else if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError('Could not reach the JewelMind backend.')
      }
      return null
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    const submitted = text
    setText('')
    void sendTurn(submitted)
  }

  const handleClarificationChoice = (choice: string) => {
    void sendTurn(choice)
  }

  const handleAccept = async () => {
    const proposal = session?.activeProposal
    if (!proposal || proposal.status !== 'ACTIVE') return
    const toApply = proposal.designerProposal
    const result = await sendTurn('Accept')
    if (result?.turn.interpretedAction === 'ACCEPT_PROPOSAL' && result.turn.accepted === true) {
      applyDesignerProposalResult(toApply, applyDesignerProposal, applyIntent)
    }
  }

  const handleReject = () => {
    void sendTurn('Reject')
  }

  const handleCancel = () => {
    void sendTurn('Undo')
  }

  const clarification = session?.pendingClarification?.status === 'OPEN' ? session.pendingClarification : null
  const proposal = session?.activeProposal?.status === 'ACTIVE' ? session.activeProposal : null
  const lastTurn = session?.turns[session.turns.length - 1] ?? null
  const showUnsupported = lastTurn?.interpretedAction === 'REPORT_UNSUPPORTED'

  const proposalDiff = proposal?.designerProposal.diff.filter((d) => d.changed) ?? []
  const proposalIntentStatements = proposal?.designerProposal.designIntent.statements ?? []

  return (
    <section className="conversation-panel" aria-label="Design assistant">
      <h2 className="designer-panel__title">Design assistant</h2>
      <p className="designer-panel__hint">
        Describe your design or a change to it, in Italian or English — across as many turns as you
        need. JewelMind proposes structured values for you to review — it never changes the design
        without your approval.
      </p>

      {session && session.turns.length > 0 ? (
        <ul className="conversation-panel__history" aria-label="Conversation history">
          {session.turns.map((turn) => (
            <li key={turn.turnId} className="conversation-turn">
              <p className="conversation-turn__user">
                <span className="conversation-turn__role">You</span> {turn.sourceText}
              </p>
              <p className="conversation-turn__system">
                <span className="conversation-turn__role">JewelMind</span>{' '}
                <span className="conversation-turn__action">{actionLabel(turn)}</span> — {turn.result}
              </p>
            </li>
          ))}
        </ul>
      ) : null}

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
          <button type="submit" className="btn btn--primary" disabled={isLoading || !text.trim()}>
            {isLoading ? 'Interpreting…' : 'Send'}
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

      {clarification ? (
        <div className="designer-proposal designer-proposal__clarification" role="region" aria-label="Clarification">
          <h3>JewelMind needs to know</h3>
          <p>{clarification.question}</p>
          {clarification.expectedAnswerType === 'ENUM_CHOICE' && clarification.allowedChoices.length > 0 ? (
            <div className="designer-proposal__clarification-options">
              {clarification.allowedChoices.map((choice) => (
                <button
                  key={choice}
                  type="button"
                  className="btn btn--ghost"
                  onClick={() => handleClarificationChoice(choice)}
                  disabled={isLoading}
                >
                  {choice}
                </button>
              ))}
            </div>
          ) : null}
          {clarification.expectedAnswerType === 'CONFIRMATION' ? (
            <div className="designer-proposal__clarification-options">
              <button
                type="button"
                className="btn btn--ghost"
                onClick={() => handleClarificationChoice('yes')}
                disabled={isLoading}
              >
                Yes
              </button>
              <button
                type="button"
                className="btn btn--ghost"
                onClick={() => handleClarificationChoice('no')}
                disabled={isLoading}
              >
                No
              </button>
            </div>
          ) : null}
        </div>
      ) : null}

      {showUnsupported && lastTurn ? (
        <div className="designer-proposal designer-proposal__section--unsupported" role="alert">
          <h3>Not currently supported</h3>
          <p>{lastTurn.result}</p>
        </div>
      ) : null}

      {proposal ? (
        <div className="designer-proposal" role="region" aria-label="Proposal review">
          {proposalDiff.length > 0 ? (
            <div className="designer-proposal__section">
              <h3>Proposed change</h3>
              <ul className="designer-proposal__field-list">
                {proposalDiff.map((d) => (
                  <li key={d.path}>
                    <span className="designer-proposal__field-path">{fieldLabel(d.path)}</span>
                    <span className="designer-proposal__field-value">
                      {String(d.previousValue)} → {String(d.proposedValue)}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          {proposalIntentStatements.length > 0 ? (
            <div className="designer-proposal__section">
              <h3>Design intent</h3>
              <ul className="designer-proposal__plain-list">
                {proposalIntentStatements.map((s) => (
                  <li key={s.intentId}>
                    {s.target.toLowerCase()}: {s.value.toLowerCase()} ({s.concept.toLowerCase().replace(/_/g, ' ')})
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          <div className="designer-proposal__actions">
            <button type="button" className="btn btn--primary" onClick={() => void handleAccept()} disabled={isLoading}>
              Accept
            </button>
            <button type="button" className="btn btn--ghost" onClick={handleReject} disabled={isLoading}>
              Reject
            </button>
          </div>
        </div>
      ) : null}

      {clarification || proposal ? (
        <button type="button" className="btn btn--ghost conversation-panel__cancel" onClick={handleCancel} disabled={isLoading}>
          Cancel
        </button>
      ) : null}
    </section>
  )
}
