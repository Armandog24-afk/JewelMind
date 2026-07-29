import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { useProjectStore } from '../store/useProjectStore'
import { BackendStatus } from './BackendStatus'

describe('BackendStatus', () => {
  it('shows online status', () => {
    useProjectStore.setState({ backendStatus: 'online' })
    render(<BackendStatus />)
    expect(screen.getByText('Backend online')).toBeInTheDocument()
  })

  it('shows offline status', () => {
    useProjectStore.setState({ backendStatus: 'offline' })
    render(<BackendStatus />)
    expect(screen.getByText('Backend unreachable')).toBeInTheDocument()
  })

  it('shows checking status', () => {
    useProjectStore.setState({ backendStatus: 'checking' })
    render(<BackendStatus />)
    expect(screen.getByText('Checking backend…')).toBeInTheDocument()
  })
})
