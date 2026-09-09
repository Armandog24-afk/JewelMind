import { fireEvent, render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it } from 'vitest'
import { useProjectStore } from '../store/useProjectStore'
import { SettingModeSection } from './SettingModeSection'

/**
 * Studio controls for Extended Setting Modes (Sprint 27).
 *
 * The two things worth asserting about a capability panel: that it offers only
 * what the backend builds, and that every edit is a real design edit which
 * marks an existing model stale.
 */

function setType(type: string) {
  useProjectStore.getState().updateSetting({ type: type as never })
}

describe('SettingModeSection', () => {
  beforeEach(() => {
    useProjectStore.getState().resetProject()
  })

  it('offers the prong variants and the head architectures the backend builds', () => {
    render(<SettingModeSection />)

    const variant = screen.getByLabelText('Variant') as HTMLSelectElement
    expect([...variant.options].map((o) => o.value)).toEqual([
      'PRONG_ROUND',
      'PRONG_TAPERED',
      'PRONG_CLAW',
      'PRONG_V',
    ])

    const head = screen.getByLabelText('Head') as HTMLSelectElement
    expect([...head.options].map((o) => o.value)).toEqual([
      'BASKET',
      'PEG_HEAD',
      'MARTINI',
      'TULIP',
      'OPEN_GALLERY',
    ])
  })

  it('never offers a reserved mode', () => {
    render(<SettingModeSection />)
    const rendered = document.body.textContent ?? ''
    for (const reserved of ['Trellis', 'Azure', 'Cathedral', 'Double gallery']) {
      expect(rendered).not.toContain(reserved)
    }
  })

  it('shows only the parameters the selected family reads', () => {
    const { rerender } = render(<SettingModeSection />)
    // A prong setting reads no mode parameters at all.
    expect(screen.queryByLabelText('Wall thickness')).toBeNull()
    expect(screen.queryByLabelText('Collar width')).toBeNull()

    setType('channel')
    rerender(<SettingModeSection />)
    expect(screen.getByLabelText(/Wall thickness/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Wall height/)).toBeInTheDocument()
    expect(screen.getByLabelText('Ends')).toBeInTheDocument()
    expect(screen.queryByLabelText(/Collar width/)).toBeNull()

    setType('flush')
    rerender(<SettingModeSection />)
    expect(screen.getByLabelText(/Collar width/)).toBeInTheDocument()
    expect(screen.queryByLabelText(/Wall height/)).toBeNull()
  })

  it('reveals the partial bezel controls only for that variant', () => {
    setType('bezel')
    const { rerender } = render(<SettingModeSection />)
    expect(screen.queryByLabelText('Openings')).toBeNull()

    fireEvent.change(screen.getByLabelText('Variant'), {
      target: { value: 'BEZEL_PARTIAL' },
    })
    rerender(<SettingModeSection />)

    expect(screen.getByLabelText('Openings')).toBeInTheDocument()
    expect(useProjectStore.getState().currentDefinition.setting.mode?.modeId).toBe(
      'BEZEL_PARTIAL',
    )
  })

  it('clears the mode block when the default variant is chosen again', () => {
    setType('bezel')
    const { rerender } = render(<SettingModeSection />)
    fireEvent.change(screen.getByLabelText('Variant'), {
      target: { value: 'BEZEL_PARTIAL' },
    })
    rerender(<SettingModeSection />)
    fireEvent.change(screen.getByLabelText('Variant'), {
      target: { value: 'BEZEL_FULL' },
    })

    // A document with NO mode is the pre-Sprint-27 state, and choosing the
    // family's default variant must reach exactly that rather than storing a
    // mode that means "the default".
    expect(useProjectStore.getState().currentDefinition.setting.mode).toBeNull()
  })

  it('reveals the gallery window controls only for an open gallery', () => {
    const { rerender } = render(<SettingModeSection />)
    expect(screen.queryByLabelText('Windows')).toBeNull()

    fireEvent.change(screen.getByLabelText('Head'), {
      target: { value: 'OPEN_GALLERY' },
    })
    rerender(<SettingModeSection />)

    expect(screen.getByLabelText('Windows')).toHaveValue(4)
    expect(screen.getByLabelText(/Window height/)).toBeInTheDocument()
    expect(
      useProjectStore.getState().currentDefinition.setting.headArchitecture,
    ).toBe('OPEN_GALLERY')
  })

  it('warns that a flush setting needs relief, and stops warning once it has it', () => {
    setType('flush')
    const { rerender } = render(<SettingModeSection />)
    expect(screen.getByText(/needs the metal relieved/)).toBeInTheDocument()

    fireEvent.change(screen.getByLabelText(/Relieve metal for the stone/), {
      target: { value: 'REFERENCE_SEAT' },
    })
    rerender(<SettingModeSection />)

    expect(screen.queryByText(/needs the metal relieved/)).toBeNull()
  })

  it('states plainly what a tension setting does not model', () => {
    setType('tension')
    render(<SettingModeSection />)
    const note = screen.getByText(/does not model how a tension setting/)
    expect(note.textContent).toContain('spring-back')
    expect(note.textContent).toContain('qualified jewelry professional')
  })

  it('never claims any dimension is professionally validated', () => {
    render(<SettingModeSection />)
    const rendered = document.body.textContent ?? ''
    expect(rendered).toContain('must review this design before production')
    for (const claim of [
      'industry standard',
      'manufacturing safe',
      'jeweler approved',
      'structurally safe',
    ]) {
      expect(rendered.toLowerCase()).not.toContain(claim)
    }
  })

  it('marks an existing model stale when a mode parameter changes', () => {
    /**
     * STUDIO-GOV-004: a geometry-driving edit must set `isStale` through
     * `withUpdatedDefinition()`, exactly as every other design field does.
     */

    setType('channel')
    useProjectStore.setState({
      generatedModel: { modelId: 'm1' } as never,
      isStale: false,
    })

    render(<SettingModeSection />)
    fireEvent.change(screen.getByLabelText(/Wall height/), {
      target: { value: '1.4' },
    })

    expect(useProjectStore.getState().isStale).toBe(true)
    expect(
      useProjectStore.getState().currentDefinition.setting.mode?.parameters
        .wallHeightMm,
    ).toBe(1.4)
  })
})
