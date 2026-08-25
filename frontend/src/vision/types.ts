/**
 * Vision v1 pure state types. Mirrors specs/vision/v1/*.schema.json.
 * No Three.js object may appear in any of these types — see
 * docs/bible/10-vision/239-render-state-model.md.
 */

export type ViewMode = 'technical' | 'presentation'

export type CameraPresetKey = 'perspective' | 'front' | 'side' | 'top' | 'three_quarter'

/** The 4 current Atlas components. Not a closed union in code (new
 * components must not require a frontend release just to render), but
 * documented here for reference. */
export type ComponentName = 'band' | 'stone_reference' | 'prongs' | 'basket_support'

export type GeometryRole = 'production_metal' | 'stone_reference' | 'support' | 'preview_only'

export interface ComponentVisualState {
  name: string
  geometryRole: GeometryRole
  visible: boolean
  generationStatus: 'SUCCEEDED' | 'SUCCEEDED_WITH_FALLBACK' | 'FAILED' | 'EMPTY'
}

export interface CameraState {
  preset: CameraPresetKey | null
  /** Plain numeric tuples, never a THREE.Vector3 instance. */
  position: [number, number, number] | null
  target: [number, number, number] | null
}

export interface MaterialPresentation {
  metal: string
  stonePresentationEnabled: boolean
}

/** A point-in-time snapshot of Vision state, composed from useVisionStore
 * + useProjectStore at the moment it's needed (e.g. before an image
 * capture) — never a literal 1:1 mirror of either store's internal
 * shape. See docs/bible/10-vision/239-render-state-model.md. */
export interface SceneStateSnapshot {
  viewMode: ViewMode
  camera: CameraState
  components: ComponentVisualState[]
  material: MaterialPresentation
  stale: boolean
  modelId: string | null
  definitionHash: string | null
}

export interface ImageCaptureRequest {
  width: number
  height: number
  filename: string
}

export interface RenderResult {
  ok: boolean
  width: number
  height: number
  filename: string
  capturedAtDefinitionHash: string | null
  blockedReason: 'stale' | 'no_model' | null
}
