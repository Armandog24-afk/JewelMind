import { beforeEach, describe, expect, it } from 'vitest'
import { useProjectStore } from './useProjectStore'
import { isComponentVisible, useVisionStore } from './useVisionStore'

const COMPONENTS = ['band', 'stone_reference', 'prongs', 'basket_support']

function resetVisionStore() {
  useVisionStore.setState({
    viewMode: 'technical',
    componentVisibility: {},
    selectedComponent: null,
    showGrid: true,
    showAxes: false,
  })
}

beforeEach(() => {
  resetVisionStore()
})

describe('useVisionStore', () => {
  it('defaults every component to visible', () => {
    for (const name of COMPONENTS) {
      expect(isComponentVisible(useVisionStore.getState(), name)).toBe(true)
    }
  })

  it('toggles a single component without affecting the others', () => {
    useVisionStore.getState().toggleComponentVisible('stone_reference')
    const state = useVisionStore.getState()
    expect(isComponentVisible(state, 'stone_reference')).toBe(false)
    expect(isComponentVisible(state, 'band')).toBe(true)
  })

  it('"show all" makes every listed component visible again', () => {
    useVisionStore.getState().toggleComponentVisible('band')
    useVisionStore.getState().showAllComponents(COMPONENTS)
    const state = useVisionStore.getState()
    for (const name of COMPONENTS) expect(isComponentVisible(state, name)).toBe(true)
  })

  it('"metal only" hides exactly the non-metal components', () => {
    useVisionStore.getState().showOnlyComponents(COMPONENTS, ['band', 'prongs', 'basket_support'])
    const state = useVisionStore.getState()
    expect(isComponentVisible(state, 'stone_reference')).toBe(false)
    expect(isComponentVisible(state, 'band')).toBe(true)
    expect(isComponentVisible(state, 'prongs')).toBe(true)
    expect(isComponentVisible(state, 'basket_support')).toBe(true)
  })

  it('switching view mode never touches project/geometry state (no regeneration trigger)', () => {
    const before = {
      definitionHash: useProjectStore.getState().generatedModel?.definitionHash ?? null,
      isStale: useProjectStore.getState().isStale,
      generationStatus: useProjectStore.getState().generationStatus,
    }
    useVisionStore.getState().setViewMode('presentation')
    useVisionStore.getState().setViewMode('technical')
    const after = {
      definitionHash: useProjectStore.getState().generatedModel?.definitionHash ?? null,
      isStale: useProjectStore.getState().isStale,
      generationStatus: useProjectStore.getState().generationStatus,
    }
    expect(after).toEqual(before)
  })

  it('camera-preset and visibility changes are independent of view mode', () => {
    useVisionStore.getState().setViewMode('presentation')
    useVisionStore.getState().toggleComponentVisible('prongs')
    expect(isComponentVisible(useVisionStore.getState(), 'prongs')).toBe(false)
    expect(useVisionStore.getState().viewMode).toBe('presentation')
  })
})
