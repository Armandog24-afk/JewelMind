import { fireEvent, render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it } from 'vitest'
import { useProjectStore } from '../store/useProjectStore'
import { ConfigurationPanel } from './ConfigurationPanel'
import { JsonViewer } from './JsonViewer'

describe('ConfigurationPanel', () => {
  beforeEach(() => {
    useProjectStore.getState().resetProject()
  })

  it('renders the default form values', () => {
    render(<ConfigurationPanel />)
    expect(screen.getByLabelText('Name')).toHaveValue('Solitaire Ring')
    expect(screen.getByLabelText('EU size')).toHaveValue(16)
    expect(screen.getByLabelText(/Inner diameter/)).toHaveValue(17.8)
    expect(screen.getByLabelText(/^Width/)).toHaveValue(2.4)
  })

  it('updates the JewelryDefinition (and the JSON tab) when a field changes', () => {
    render(
      <>
        <ConfigurationPanel />
        <JsonViewer />
      </>,
    )

    const widthInput = screen.getByLabelText(/^Width/)
    fireEvent.change(widthInput, { target: { value: '3.2' } })

    expect(useProjectStore.getState().currentDefinition.band.width).toBe(3.2)
    expect(screen.getByText(/"width": 3.2/)).toBeInTheDocument()
  })

  it('has accessible labels for every numeric field', () => {
    render(<ConfigurationPanel />)
    expect(screen.getByLabelText('EU size')).toBeInTheDocument()
    expect(screen.getByLabelText(/Inner diameter/)).toBeInTheDocument()
    expect(screen.getByLabelText(/^Thickness/)).toBeInTheDocument()
    expect(screen.getByLabelText(/^Diameter/)).toBeInTheDocument()
    expect(screen.getByLabelText(/^Depth/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Prong diameter/)).toBeInTheDocument()
  })
})
