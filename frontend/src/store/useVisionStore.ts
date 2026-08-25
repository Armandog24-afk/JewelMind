import { create } from 'zustand'
import type { ViewMode } from '../vision/types'

/**
 * Vision-only presentation state — camera mode, component visibility,
 * grid/axes toggles. Deliberately has zero import from useProjectStore
 * and never calls generate()/updateXxx(): switching view mode, toggling a
 * component, or changing a camera preset must never regenerate geometry,
 * change JDL, change definitionHash, or affect STEP/STL — see
 * VISION-GOV and docs/bible/10-vision/239-render-state-model.md.
 *
 * viewMode is the one field persisted across reloads (Sprint 9,
 * Studio v1) — a UI preference, not design intent, so it uses its own
 * storage key and never touches persistence.ts's JewelryDefinition
 * validation path. See docs/bible/11-studio/274-local-persistence-model.md.
 */

const VIEW_MODE_STORAGE_KEY = 'jewelmind:vision-view-mode:v1'

function loadStoredViewMode(): ViewMode {
  try {
    const raw = window.localStorage.getItem(VIEW_MODE_STORAGE_KEY)
    return raw === 'presentation' ? 'presentation' : 'technical'
  } catch {
    return 'technical'
  }
}

function saveViewMode(mode: ViewMode): void {
  try {
    window.localStorage.setItem(VIEW_MODE_STORAGE_KEY, mode)
  } catch {
    // Persistence is a convenience, not a correctness requirement.
  }
}

interface VisionState {
  viewMode: ViewMode
  componentVisibility: Record<string, boolean>
  selectedComponent: string | null
  showGrid: boolean
  showAxes: boolean
  /** Incremented to request a presentation-image capture from outside
   * ModelViewport (e.g. Studio's consolidated Outputs panel) without
   * either component needing a direct reference to the other. */
  captureRequestToken: number

  setViewMode: (mode: ViewMode) => void
  setComponentVisible: (name: string, visible: boolean) => void
  toggleComponentVisible: (name: string) => void
  showAllComponents: (names: string[]) => void
  showOnlyComponents: (names: string[], visibleNames: string[]) => void
  selectComponent: (name: string | null) => void
  setShowGrid: (value: boolean) => void
  setShowAxes: (value: boolean) => void
  toggleShowGrid: () => void
  toggleShowAxes: () => void
  requestCapture: () => void
}

export function isComponentVisible(state: Pick<VisionState, 'componentVisibility'>, name: string): boolean {
  return state.componentVisibility[name] ?? true
}

export const useVisionStore = create<VisionState>((set) => ({
  viewMode: loadStoredViewMode(),
  componentVisibility: {},
  selectedComponent: null,
  showGrid: true,
  showAxes: false,
  captureRequestToken: 0,

  setViewMode: (mode) => {
    saveViewMode(mode)
    set({ viewMode: mode })
  },

  setComponentVisible: (name, visible) =>
    set((state) => ({ componentVisibility: { ...state.componentVisibility, [name]: visible } })),

  toggleComponentVisible: (name) =>
    set((state) => ({
      componentVisibility: {
        ...state.componentVisibility,
        [name]: !isComponentVisible(state, name),
      },
    })),

  showAllComponents: (names) =>
    set({ componentVisibility: Object.fromEntries(names.map((name) => [name, true])) }),

  showOnlyComponents: (names, visibleNames) => {
    const visibleSet = new Set(visibleNames)
    set({ componentVisibility: Object.fromEntries(names.map((name) => [name, visibleSet.has(name)])) })
  },

  selectComponent: (name) => set({ selectedComponent: name }),

  setShowGrid: (value) => set({ showGrid: value }),
  setShowAxes: (value) => set({ showAxes: value }),
  toggleShowGrid: () => set((state) => ({ showGrid: !state.showGrid })),
  toggleShowAxes: () => set((state) => ({ showAxes: !state.showAxes })),

  requestCapture: () => set((state) => ({ captureRequestToken: state.captureRequestToken + 1 })),
}))
