import { create } from 'zustand'
import {
  createDefaultDefinition,
  type BandSpec,
  type JewelryDefinition,
  type ManufacturingSpec,
  type MaterialSpec,
  type PreviewSpec,
  type ProjectInfo,
  type RingSpec,
  type SettingSpec,
  type StoneSpec,
} from '@shared/types/jewelry-definition'
import { hasErrors, validateDefinition } from '@shared/validation/engine'
import type { ValidationResult } from '@shared/validation/rules'
import {
  exportJson,
  exportSpecification,
  exportStep,
  exportStl,
  fetchHealth,
  generateModel,
  triggerBrowserDownload,
} from '../api/client'
import { ApiError } from '../api/types'
import type { GenerateResponse } from '../api/types'
import { clearDefinition, loadDefinition, saveDefinition } from './persistence'

export type GenerationStatus = 'idle' | 'generating' | 'success' | 'error'
export type BackendStatus = 'checking' | 'online' | 'offline'
export type ExportKind = 'step' | 'stl' | 'json' | 'specification'
export type ExportPhase = 'idle' | 'exporting' | 'success' | 'error'

interface ProjectState {
  currentDefinition: JewelryDefinition
  validationResults: ValidationResult[]
  generatedModel: GenerateResponse | null
  lastSuccessfulPreview: GenerateResponse | null
  generationStatus: GenerationStatus
  generationError: string | null
  isStale: boolean
  backendStatus: BackendStatus
  exportStatus: Record<ExportKind, ExportPhase>
  exportError: string | null
  includeStoneReferenceInExport: boolean

  updateProject: (patch: Partial<ProjectInfo>) => void
  updateRing: (patch: Partial<RingSpec>) => void
  updateBand: (patch: Partial<BandSpec>) => void
  updateStone: (patch: Partial<StoneSpec>) => void
  updateSetting: (patch: Partial<SettingSpec>) => void
  updateMaterial: (patch: Partial<MaterialSpec>) => void
  updateManufacturing: (patch: Partial<ManufacturingSpec>) => void
  updatePreview: (patch: Partial<PreviewSpec>) => void
  setIncludeStoneReferenceInExport: (value: boolean) => void

  resetProject: () => void
  checkBackendHealth: () => Promise<void>
  generate: () => Promise<void>
  runExport: (kind: ExportKind) => Promise<void>
}

function withUpdatedDefinition(
  state: ProjectState,
  next: JewelryDefinition,
): Pick<ProjectState, 'currentDefinition' | 'validationResults' | 'isStale'> {
  saveDefinition(next)
  return {
    currentDefinition: next,
    validationResults: validateDefinition(next),
    isStale: state.generatedModel !== null,
  }
}

const initialDefinition = loadDefinition() ?? createDefaultDefinition()

export const useProjectStore = create<ProjectState>((set, get) => ({
  currentDefinition: initialDefinition,
  validationResults: validateDefinition(initialDefinition),
  generatedModel: null,
  lastSuccessfulPreview: null,
  generationStatus: 'idle',
  generationError: null,
  isStale: false,
  backendStatus: 'checking',
  exportStatus: { step: 'idle', stl: 'idle', json: 'idle', specification: 'idle' },
  exportError: null,
  includeStoneReferenceInExport: false,

  updateProject: (patch) =>
    set((state) =>
      withUpdatedDefinition(state, {
        ...state.currentDefinition,
        project: { ...state.currentDefinition.project, ...patch },
      }),
    ),

  updateRing: (patch) =>
    set((state) =>
      withUpdatedDefinition(state, {
        ...state.currentDefinition,
        ring: { ...state.currentDefinition.ring, ...patch },
      }),
    ),

  updateBand: (patch) =>
    set((state) =>
      withUpdatedDefinition(state, {
        ...state.currentDefinition,
        band: { ...state.currentDefinition.band, ...patch },
      }),
    ),

  updateStone: (patch) =>
    set((state) =>
      withUpdatedDefinition(state, {
        ...state.currentDefinition,
        stone: { ...state.currentDefinition.stone, ...patch },
      }),
    ),

  updateSetting: (patch) =>
    set((state) =>
      withUpdatedDefinition(state, {
        ...state.currentDefinition,
        setting: { ...state.currentDefinition.setting, ...patch },
      }),
    ),

  updateMaterial: (patch) =>
    set((state) =>
      withUpdatedDefinition(state, {
        ...state.currentDefinition,
        material: { ...state.currentDefinition.material, ...patch },
      }),
    ),

  updateManufacturing: (patch) =>
    set((state) =>
      withUpdatedDefinition(state, {
        ...state.currentDefinition,
        manufacturing: { ...state.currentDefinition.manufacturing, ...patch },
      }),
    ),

  updatePreview: (patch) =>
    set((state) =>
      withUpdatedDefinition(state, {
        ...state.currentDefinition,
        preview: { ...state.currentDefinition.preview, ...patch },
      }),
    ),

  setIncludeStoneReferenceInExport: (value) => set({ includeStoneReferenceInExport: value }),

  resetProject: () => {
    clearDefinition()
    const fresh = createDefaultDefinition()
    saveDefinition(fresh)
    set({
      currentDefinition: fresh,
      validationResults: validateDefinition(fresh),
      generatedModel: null,
      lastSuccessfulPreview: null,
      generationStatus: 'idle',
      generationError: null,
      isStale: false,
      exportStatus: { step: 'idle', stl: 'idle', json: 'idle', specification: 'idle' },
      exportError: null,
    })
  },

  checkBackendHealth: async () => {
    set({ backendStatus: 'checking' })
    try {
      const health = await fetchHealth()
      set({ backendStatus: health.status === 'ok' && health.cadEngineReady ? 'online' : 'offline' })
    } catch {
      set({ backendStatus: 'offline' })
    }
  },

  generate: async () => {
    const { currentDefinition } = get()
    set({ generationStatus: 'generating', generationError: null })
    try {
      const result = await generateModel(currentDefinition)
      set({
        generatedModel: result,
        lastSuccessfulPreview: result,
        validationResults: result.validation,
        generationStatus: 'success',
        isStale: false,
      })
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : 'Could not reach the JewelMind backend.'
      if (err instanceof ApiError && err.code === 'VALIDATION_BLOCKED') {
        set({
          generationStatus: 'error',
          generationError: message,
          validationResults: (err.details as ValidationResult[]) ?? get().validationResults,
        })
      } else {
        set({ generationStatus: 'error', generationError: message })
      }
    }
  },

  runExport: async (kind) => {
    const { generatedModel, includeStoneReferenceInExport, isStale, validationResults } = get()
    if (!generatedModel || isStale || hasErrors(validationResults)) {
      return
    }
    set((state) => ({
      exportStatus: { ...state.exportStatus, [kind]: 'exporting' },
      exportError: null,
    }))
    try {
      const { blob, filename } = await (async () => {
        switch (kind) {
          case 'step':
            return exportStep(generatedModel.modelId, includeStoneReferenceInExport)
          case 'stl':
            return exportStl(generatedModel.modelId, includeStoneReferenceInExport)
          case 'json':
            return exportJson(generatedModel.modelId)
          case 'specification':
            return exportSpecification(generatedModel.modelId)
        }
      })()
      triggerBrowserDownload(blob, filename)
      set((state) => ({ exportStatus: { ...state.exportStatus, [kind]: 'success' } }))
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Export failed unexpectedly.'
      set((state) => ({
        exportStatus: { ...state.exportStatus, [kind]: 'error' },
        exportError: message,
      }))
    }
  },
}))
