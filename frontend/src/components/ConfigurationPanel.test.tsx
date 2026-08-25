import { fireEvent, render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it } from 'vitest'
import { useProjectStore } from '../store/useProjectStore'
import { ConfigurationPanel } from './ConfigurationPanel'
import { JsonViewer } from './JsonViewer'

function openAdvancedParameters() {
  fireEvent.click(screen.getByText('Advanced / technical parameters'))
}

describe('ConfigurationPanel', () => {
  beforeEach(() => {
    useProjectStore.getState().resetProject()
  })

  it('renders the default design-parameter values', () => {
    render(<ConfigurationPanel />)
    expect(screen.getByLabelText('Name')).toHaveValue('Solitaire Ring')
    expect(screen.getByLabelText('EU size')).toHaveValue(16)
    expect(screen.getByLabelText(/^Width/)).toHaveValue(2.4)
  })

  it('keeps advanced/technical parameters collapsed by default', () => {
    render(<ConfigurationPanel />)
    const summary = screen.getByText('Advanced / technical parameters')
    const details = summary.closest('details')
    expect(details).not.toBeNull()
    expect(details?.open).toBe(false)
  })

  it('reveals advanced parameters once expanded, including the new preview-tolerance controls', () => {
    render(<ConfigurationPanel />)
    openAdvancedParameters()
    expect(screen.getByLabelText(/Inner diameter/)).toHaveValue(17.8)
    expect(screen.getByLabelText(/^Depth/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Prong diameter/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Mesh tolerance/)).toHaveValue(0.1)
    expect(screen.getByLabelText(/Angular tolerance/)).toHaveValue(0.2)
  })

  it('updates the JewelryDefinition (and the JSON tab) when a design field changes', () => {
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

  it('updates the JewelryDefinition when an advanced field changes', () => {
    render(<ConfigurationPanel />)
    openAdvancedParameters()
    const meshToleranceInput = screen.getByLabelText(/Mesh tolerance/)
    fireEvent.change(meshToleranceInput, { target: { value: '0.05' } })
    expect(useProjectStore.getState().currentDefinition.preview.meshTolerance).toBe(0.05)
  })

  it('has accessible labels for every visible design-parameter field', () => {
    render(<ConfigurationPanel />)
    expect(screen.getByLabelText('EU size')).toBeInTheDocument()
    expect(screen.getByLabelText(/^Thickness/)).toBeInTheDocument()
    expect(screen.getByLabelText(/^Diameter/)).toBeInTheDocument()
  })

  it('has accessible labels for every advanced-parameter field once expanded', () => {
    render(<ConfigurationPanel />)
    openAdvancedParameters()
    expect(screen.getByLabelText(/Inner diameter/)).toBeInTheDocument()
    expect(screen.getByLabelText(/^Depth/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Prong diameter/)).toBeInTheDocument()
  })
})
