import { beforeEach, describe, expect, it } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import { createDefaultDefinition } from '@shared/types/jewelry-definition'
import { useProjectStore } from '../store/useProjectStore'
import { RingFamilySection } from './RingFamilySection'

/**
 * What these tests are actually protecting.
 *
 * The sprint's own final test is whether a designer could use Ring Families as
 * a PARAMETRIC SYSTEM rather than a catalogue of names. In the interface that
 * question has three concrete parts, and each is asserted below on the real
 * store rather than on a mock:
 *
 * 1. Choosing a family or a variant must not overwrite the band, the stone or
 *    the head — otherwise every selection is a preset, whatever the backend
 *    does with it.
 * 2. Only the parameters the chosen variant actually READS may be offered, so a
 *    control the design ignores is never presented as though it did something.
 * 3. Every option offered must be one the backend can build — the panel carries
 *    no reserved variant and no "coming soon" entry.
 */

function reset() {
  const fresh = createDefaultDefinition()
  useProjectStore.setState({
    currentDefinition: fresh,
    generatedModel: null,
    isStale: false,
  })
}

const definition = () => useProjectStore.getState().currentDefinition

describe('RingFamilySection', () => {
  beforeEach(reset)

  it('starts on the family and variant a default document resolves to', () => {
    render(<RingFamilySection />)
    expect(screen.getByLabelText('Family')).toHaveValue('solitaire')
    expect(screen.getByLabelText('Variant')).toHaveValue('SOLITAIRE_CLASSIC')
    // A default document declares NO variant block, and selecting the default
    // one must not create one: "no variant declared" is a real state.
    expect(definition().ringFamily).toBeNull()
  })

  it('offers exactly the families the backend can build', () => {
    render(<RingFamilySection />)
    const values = Array.from(
      screen.getByLabelText('Family').querySelectorAll('option'),
    ).map((o) => o.getAttribute('value'))
    expect(values).toEqual([
      'solitaire',
      'three_stone',
      'halo',
      'split_shank',
      'bypass',
      'signet',
    ])
    // The reserved families have real technical reasons for not existing yet
    // (see RESERVED_RING_FAMILIES); an option a user can pick and the product
    // cannot build is worse than an absent one.
    expect(values).not.toContain('eternity')
    expect(values).not.toContain('toi_et_moi')
    expect(values).not.toContain('plain_band')
    expect(values).not.toContain('cluster')
  })

  it('offers no reserved variant in any family', () => {
    const reserved = [
      'SOLITAIRE_TRELLIS',
      'SPLIT_SHANK_SCULPTED',
      'BYPASS_TWIST',
      'SIGNET_ENGRAVED',
      'SIGNET_OVAL_TABLE',
    ]
    for (const family of ['solitaire', 'split_shank', 'bypass', 'signet']) {
      reset()
      useProjectStore.getState().updateJewelry({ style: family as never })
      const view = render(<RingFamilySection />)
      const select = screen.queryByLabelText('Variant')
      const values =
        select === null
          ? []
          : Array.from(select.querySelectorAll('option')).map((o) =>
              o.getAttribute('value'),
            )
      for (const name of reserved) {
        expect(values).not.toContain(name)
      }
      view.unmount()
    }
  })

  it('changing the family does not overwrite the band, stone or head', () => {
    // A designer's own values, deliberately not the defaults.
    useProjectStore.getState().updateBand({ width: 3.4, thickness: 1.9 })
    useProjectStore.getState().updateStone({ diameter: 7.2 })
    useProjectStore.getState().updateSetting({ basketHeight: 4.4 })
    useProjectStore.getState().updateRing({ size: 61 })

    render(<RingFamilySection />)
    fireEvent.change(screen.getByLabelText('Family'), {
      target: { value: 'split_shank' },
    })

    const d = definition()
    expect(d.jewelry.style).toBe('split_shank')
    // THE POINT OF THE SPRINT: a family is a relation, not a preset. The
    // designer's own dimensions survive and the new family derives from them.
    expect(d.band.width).toBe(3.4)
    expect(d.band.thickness).toBe(1.9)
    expect(d.stone.diameter).toBe(7.2)
    expect(d.setting.basketHeight).toBe(4.4)
    expect(d.ring.size).toBe(61)
  })

  it('clears the variant block when the family changes', () => {
    render(<RingFamilySection />)
    fireEvent.change(screen.getByLabelText('Variant'), {
      target: { value: 'SOLITAIRE_CATHEDRAL' },
    })
    expect(definition().ringFamily?.variant).toBe('SOLITAIRE_CATHEDRAL')

    fireEvent.change(screen.getByLabelText('Family'), {
      target: { value: 'halo' },
    })
    // Carrying a solitaire variant into the halo family would be refused by the
    // backend's JM-RINGFAM-001; the UI must not be able to construct it.
    expect(definition().ringFamily).toBeNull()
    expect(definition().jewelry.style).toBe('halo')
  })

  it('returning to the default variant clears the block rather than storing it', () => {
    render(<RingFamilySection />)
    const variant = screen.getByLabelText('Variant')
    fireEvent.change(variant, { target: { value: 'SOLITAIRE_ELEVATED' } })
    expect(definition().ringFamily?.variant).toBe('SOLITAIRE_ELEVATED')

    fireEvent.change(variant, { target: { value: 'SOLITAIRE_CLASSIC' } })
    expect(definition().ringFamily).toBeNull()
  })

  it('shows only the parameters the chosen variant reads', () => {
    render(<RingFamilySection />)

    // CLASSIC reads the shared head factor and nothing structural.
    expect(screen.getByLabelText(/Head height/)).toBeInTheDocument()
    expect(screen.queryByLabelText(/Shoulder reach/)).toBeNull()
    expect(screen.queryByLabelText(/Rail separation/)).toBeNull()
    expect(screen.queryByLabelText(/Halo stones/)).toBeNull()

    fireEvent.change(screen.getByLabelText('Variant'), {
      target: { value: 'SOLITAIRE_CATHEDRAL' },
    })
    expect(screen.getByLabelText(/Shoulder reach/)).toBeInTheDocument()
    expect(screen.queryByLabelText(/Rail separation/)).toBeNull()
  })

  it('shows the split-shank parameters for the split-shank family', () => {
    useProjectStore.getState().updateJewelry({ style: 'split_shank' })
    render(<RingFamilySection />)
    expect(screen.getByLabelText(/Rail separation/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Joined span/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Shoulder reach/)).toBeInTheDocument()
    expect(screen.queryByLabelText(/Table length/)).toBeNull()
  })

  it('describes the halo radius as a relation to the stone, not a millimetre value', () => {
    useProjectStore.getState().updateJewelry({ style: 'halo' })
    render(<RingFamilySection />)
    // The unit is what tells a designer the halo follows the stone. A halo
    // whose radius were absolute would go stale the moment the stone changed.
    expect(screen.getByLabelText(/Halo radius \(× stone\)/)).toBeInTheDocument()
  })

  it('records a parameter edit as a design change on the real document', () => {
    render(<RingFamilySection />)
    fireEvent.change(screen.getByLabelText(/Head height/), {
      target: { value: '1.3' },
    })
    expect(definition().ringFamily?.params.headHeightFactor).toBe(1.3)
    // Seeding the block must use the family's default variant, never an
    // arbitrary one.
    expect(definition().ringFamily?.variant).toBe('SOLITAIRE_CLASSIC')
    expect(definition().ringFamily?.enabled).toBe(true)
  })

  it('marks an existing model stale after a family change', () => {
    useProjectStore.setState({
      generatedModel: { any: true } as never,
      isStale: false,
    })
    render(<RingFamilySection />)
    fireEvent.change(screen.getByLabelText('Family'), {
      target: { value: 'signet' },
    })
    // STUDIO-GOV-004: a geometry-driving edit must mark the model stale.
    expect(useProjectStore.getState().isStale).toBe(true)
  })

  it('states what is missing for a variant the backend reports PARTIAL', () => {
    useProjectStore.getState().updateJewelry({ style: 'halo' })
    const view = render(<RingFamilySection />)
    expect(screen.getByText(/No metal is generated to hold them/)).toBeInTheDocument()
    view.unmount()

    reset()
    useProjectStore.getState().updateJewelry({ style: 'signet' })
    render(<RingFamilySection />)
    expect(screen.getByText(/no engraving, relief or texture/)).toBeInTheDocument()
  })

  it('claims no manufacturing readiness', () => {
    render(<RingFamilySection />)
    expect(
      screen.getByText(/qualified jewelry professional must review/),
    ).toBeInTheDocument()
  })

  it('offers only the pavé span once pavé shoulders are enabled', () => {
    render(<RingFamilySection />)
    expect(screen.queryByLabelText(/Pavé coverage/)).toBeNull()
    fireEvent.change(screen.getByLabelText('Pavé shoulders'), {
      target: { value: 'yes' },
    })
    expect(definition().ringFamily?.params.paveShoulders).toBe(true)
    expect(screen.getByLabelText(/Pavé coverage/)).toBeInTheDocument()
  })
})
