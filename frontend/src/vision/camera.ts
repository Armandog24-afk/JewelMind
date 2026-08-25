import type { CameraPresetKey } from './types'

/**
 * Pure camera math for Vision. No THREE.* import here on purpose — every
 * function takes/returns plain numbers/tuples so this module is testable
 * without a WebGL context and has no risk of holding a stale reference to
 * a disposed Three.js object.
 *
 * Coordinate mapping: the viewport applies a fixed -90 degree rotation
 * around the local X axis to the whole model group (see ModelViewport.tsx),
 * converting Atlas's backend coordinates (Y = finger-hole axis, Z = toward
 * the stone — see docs/bible/07-atlas/123-coordinate-system-and-orientation.md)
 * into this scene's coordinates: (x, y, z)_backend -> (x, z, -y)_scene.
 * `backendBoundingBoxToScene` is the one place that mapping is expressed,
 * so it is never duplicated or allowed to drift between the fit-to-model
 * logic and the camera presets.
 */

export interface BoundingBoxMm {
  xmin: number
  xmax: number
  ymin: number
  ymax: number
  zmin: number
  zmax: number
}

export interface Vec3 {
  x: number
  y: number
  z: number
}

const FALLBACK_BBOX: BoundingBoxMm = { xmin: -10, xmax: 10, ymin: -10, ymax: 10, zmin: -10, zmax: 10 }
const MIN_SCENE_SIZE = 5
const FIT_DISTANCE_MARGIN = 1.6

export function backendBoundingBoxToScene(bbox: BoundingBoxMm): { center: Vec3; size: number; minY: number } {
  const min = { x: bbox.xmin, y: bbox.zmin, z: -bbox.ymax }
  const max = { x: bbox.xmax, y: bbox.zmax, z: -bbox.ymin }
  const center: Vec3 = {
    x: (min.x + max.x) / 2,
    y: (min.y + max.y) / 2,
    z: (min.z + max.z) / 2,
  }
  const dx = max.x - min.x
  const dy = max.y - min.y
  const dz = max.z - min.z
  const size = Math.max(Math.sqrt(dx * dx + dy * dy + dz * dz), MIN_SCENE_SIZE)
  return { center, size, minY: min.y }
}

/** Direction vectors, in scene coordinates, for each named preset — see
 * docs/bible/10-vision/229-camera-system.md for how each was chosen from
 * the real coordinate convention rather than assumed. */
const PRESET_DIRECTIONS: Record<CameraPresetKey, Vec3> = {
  perspective: { x: 1, y: 0.75, z: 1 },
  three_quarter: { x: 1, y: 0.8, z: 1 },
  front: { x: 1, y: 0.12, z: 0.001 },
  side: { x: 0.001, y: 0.12, z: 1 },
  top: { x: 0.0001, y: 1, z: 0.0002 },
}

export const CAMERA_PRESET_KEYS: CameraPresetKey[] = ['perspective', 'front', 'side', 'top', 'three_quarter']

export const CAMERA_PRESET_LABELS: Record<CameraPresetKey, string> = {
  perspective: 'Perspective',
  front: 'Front',
  side: 'Side',
  top: 'Top',
  three_quarter: 'Three-quarter',
}

function normalize(v: Vec3): Vec3 {
  const length = Math.sqrt(v.x * v.x + v.y * v.y + v.z * v.z) || 1
  return { x: v.x / length, y: v.y / length, z: v.z / length }
}

export interface CameraPose {
  position: [number, number, number]
  target: [number, number, number]
}

/** Computes a camera position/target for a named preset against the
 * model's real bounding box — never a fixed distance, since rings vary
 * in diameter and stone size (see product requirement in Sprint 8:
 * "No hardcoded assumption that every future ring has identical size"). */
export function computeCameraPreset(
  preset: CameraPresetKey,
  bbox: BoundingBoxMm | null,
  marginFactor: number = FIT_DISTANCE_MARGIN,
): CameraPose {
  const { center, size } = backendBoundingBoxToScene(bbox ?? FALLBACK_BBOX)
  const direction = normalize(PRESET_DIRECTIONS[preset])
  const distance = size * marginFactor
  return {
    position: [
      center.x + direction.x * distance,
      center.y + direction.y * distance,
      center.z + direction.z * distance,
    ],
    target: [center.x, center.y, center.z],
  }
}

export function computeFitPose(bbox: BoundingBoxMm | null): CameraPose {
  return computeCameraPreset('three_quarter', bbox, FIT_DISTANCE_MARGIN)
}

export function computeGroundY(bbox: BoundingBoxMm | null): number {
  return backendBoundingBoxToScene(bbox ?? FALLBACK_BBOX).minY
}
