import { fireEvent, render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it } from 'vitest'
import { useProjectStore } from '../store/useProjectStore'
import { ConfigurationPanel } from './ConfigurationPanel'

/**
 * The Studio gem controls (Sprint 21, brief section 33).
 *
 * Asserted through the real store rather than by inspecting props, so each test
 * covers what a user's click actually writes into the design.
 */

function openAdvancedParameters() {
  fireEvent.click(screen.getByText('Advanced / technical parameters'))
}

function gem() {
  return useProjectStore.getState().currentDefinition.stone.gem
}

describe('gem identity controls', () => {
  beforeEach(() => {
    useProjectStore.getState().resetProject()
  })

  it('offers a gem control and starts from an unspecified gem', () => {
    render(<ConfigurationPanel />)
    expect(screen.getByLabelText('Gem')).toHaveValue('unknown')
    // A design that has never named a gem carries none at all — not a default
    // diamond.
    expect(gem()).toBeNull()
  })

  it('writes a canonical registry ID, never a display name', () => {
    render(<ConfigurationPanel />)
    fireEvent.change(screen.getByLabelText('Gem'), {
      target: { value: 'corundum.ruby' },
    })
    expect(gem()?.gemId).toBe('corundum.ruby')
  })

  it('reveals an origin control only once a gem is named', () => {
    render(<ConfigurationPanel />)
    expect(screen.queryByLabelText('Origin')).toBeNull()
    fireEvent.change(screen.getByLabelText('Gem'), {
      target: { value: 'corundum.ruby' },
    })
    expect(screen.getByLabelText('Origin')).toBeInTheDocument()
  })

  it('never offers an origin the backend would refuse', () => {
    render(<ConfigurationPanel />)
    fireEvent.change(screen.getByLabelText('Gem'), {
      target: { value: 'simulant.cubic_zirconia' },
    })
    const options = Array.from(
      screen.getByLabelText('Origin').querySelectorAll('option'),
    ).map((option) => option.getAttribute('value'))
    // JM-GEM-002 rejects a NATURAL cubic zirconia, so the UI must not present
    // it as a choice.
    expect(options).not.toContain('NATURAL')
    expect(options).toContain('SIMULANT')
  })

  it('drops a carried origin the new gem cannot accept', () => {
    render(<ConfigurationPanel />)
    fireEvent.change(screen.getByLabelText('Gem'), {
      target: { value: 'corundum.ruby' },
    })
    fireEvent.change(screen.getByLabelText('Origin'), {
      target: { value: 'NATURAL' },
    })
    expect(gem()?.origin).toBe('NATURAL')

    fireEvent.change(screen.getByLabelText('Gem'), {
      target: { value: 'simulant.cubic_zirconia' },
    })
    expect(gem()?.origin).toBe('SIMULANT')
  })

  it('asks for a material name when the gem is custom', () => {
    render(<ConfigurationPanel />)
    expect(screen.queryByLabelText('Material name')).toBeNull()
    fireEvent.change(screen.getByLabelText('Gem'), {
      target: { value: 'custom' },
    })
    const field = screen.getByLabelText('Material name')
    fireEvent.change(field, { target: { value: 'meteorite inlay' } })
    expect(gem()?.customName).toBe('meteorite inlay')
  })

  it('keeps "not recorded" and "declared untreated" as separate choices', () => {
    render(<ConfigurationPanel />)
    openAdvancedParameters()
    const control = screen.getByLabelText('Gem treatment')
    expect(control).toHaveValue('NONE_RECORDED')

    fireEvent.change(control, { target: { value: 'DECLARED_UNTREATED' } })
    // An assertion that the stone is untreated: one record, status NOT_PRESENT.
    expect(gem()?.treatments).toHaveLength(1)
    expect(gem()?.treatments[0]?.status).toBe('NOT_PRESENT')

    fireEvent.change(control, { target: { value: 'NONE_RECORDED' } })
    // Nothing recorded is a DIFFERENT state: an empty list, not a claim.
    expect(gem()?.treatments).toEqual([])
  })

  it('records a named treatment as present and user-declared', () => {
    render(<ConfigurationPanel />)
    openAdvancedParameters()
    fireEvent.change(screen.getByLabelText('Gem treatment'), {
      target: { value: 'HEAT' },
    })
    const treatments = gem()?.treatments ?? []
    expect(treatments).toHaveLength(1)
    expect(treatments[0]?.treatment).toBe('HEAT')
    expect(treatments[0]?.status).toBe('PRESENT')
    expect(treatments[0]?.disclosure).toBe('USER_DECLARED')
  })

  it('leaves every geometry field untouched when the gem changes', () => {
    render(<ConfigurationPanel />)
    const before = useProjectStore.getState().currentDefinition
    fireEvent.change(screen.getByLabelText('Gem'), {
      target: { value: 'corundum.ruby' },
    })
    const after = useProjectStore.getState().currentDefinition
    expect(after.stone.shape).toBe(before.stone.shape)
    expect(after.stone.diameter).toBe(before.stone.diameter)
    expect(after.stone.depth).toBe(before.stone.depth)
    expect(after.band).toEqual(before.band)
    expect(after.setting).toEqual(before.setting)
  })
})
