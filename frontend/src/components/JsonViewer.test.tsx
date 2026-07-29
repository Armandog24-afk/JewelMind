import { render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it } from 'vitest'
import { useProjectStore } from '../store/useProjectStore'
import { JsonViewer } from './JsonViewer'

describe('JsonViewer', () => {
  beforeEach(() => {
    useProjectStore.getState().resetProject()
  })

  it('reflects the current definition', () => {
    render(<JsonViewer />)
    expect(screen.getByText(/"name": "Solitaire Ring"/)).toBeInTheDocument()
  })

  it('updates immediately when the definition changes', () => {
    const { rerender } = render(<JsonViewer />)
    useProjectStore.getState().updateProject({ name: 'My Custom Ring' })
    rerender(<JsonViewer />)
    expect(screen.getByText(/"name": "My Custom Ring"/)).toBeInTheDocument()
  })
})
