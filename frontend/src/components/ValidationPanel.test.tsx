import { render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it } from 'vitest'
import { useProjectStore } from '../store/useProjectStore'
import { ValidationPanel } from './ValidationPanel'

describe('ValidationPanel', () => {
  beforeEach(() => {
    useProjectStore.getState().resetProject()
  })

  it('shows an empty state when there are no findings', () => {
    render(<ValidationPanel />)
    expect(screen.getByText(/looks good/)).toBeInTheDocument()
  })

  it('renders error messages for an invalid definition', () => {
    useProjectStore.getState().updateBand({ width: 0.5 })
    render(<ValidationPanel />)
    expect(screen.getByText(/Band width below 1.5 mm/)).toBeInTheDocument()
    expect(screen.getByText(/JM-BAND-001/)).toBeInTheDocument()
  })

  it('renders warnings distinctly from errors', () => {
    useProjectStore.getState().updateBand({ width: 13 })
    render(<ValidationPanel />)
    expect(screen.getByText(/unusually wide/)).toBeInTheDocument()
  })
})
