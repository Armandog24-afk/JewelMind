import { describe, expect, it } from 'vitest'
import {
  CAMERA_PRESET_KEYS,
  backendBoundingBoxToScene,
  computeCameraPreset,
  computeFitPose,
  computeGroundY,
} from './camera'

const RING_BBOX = { xmin: -10.7, xmax: 10.7, ymin: -10.7, ymax: 10.7, zmin: 0, zmax: 15 }
const SMALL_BBOX = { xmin: -4, xmax: 4, ymin: -4, ymax: 4, zmin: 0, zmax: 6 }
const LARGE_BBOX = { xmin: -20, xmax: 20, ymin: -20, ymax: 20, zmin: 0, zmax: 30 }

describe('backendBoundingBoxToScene', () => {
  it('maps backend Y (finger axis) to scene Z and backend Z (stone direction) to scene Y (up)', () => {
    const { center } = backendBoundingBoxToScene(RING_BBOX)
    // center.y should come from backend Z range, center.z from backend Y range (negated)
    expect(center.y).toBeCloseTo((RING_BBOX.zmin + RING_BBOX.zmax) / 2)
    expect(center.z).toBeCloseTo(-(RING_BBOX.ymin + RING_BBOX.ymax) / 2)
  })

  it('reports the scene-space minimum Y for grounding', () => {
    const { minY } = backendBoundingBoxToScene(RING_BBOX)
    expect(minY).toBeCloseTo(RING_BBOX.zmin)
  })
})

describe('computeCameraPreset', () => {
  it('produces a distinct camera position for every named preset', () => {
    const positions = CAMERA_PRESET_KEYS.map((key) => computeCameraPreset(key, RING_BBOX).position.join(','))
    expect(new Set(positions).size).toBe(CAMERA_PRESET_KEYS.length)
  })

  it('scales camera distance with model size instead of using a fixed distance', () => {
    const small = computeCameraPreset('three_quarter', SMALL_BBOX)
    const large = computeCameraPreset('three_quarter', LARGE_BBOX)
    const dist = (p: [number, number, number], t: [number, number, number]) =>
      Math.hypot(p[0] - t[0], p[1] - t[1], p[2] - t[2])
    expect(dist(large.position, large.target)).toBeGreaterThan(dist(small.position, small.target) * 2)
  })

  it('targets the model bounding-box center, not the world origin, for an off-center model', () => {
    const offCenter = { xmin: 90, xmax: 110, ymin: -5, ymax: 5, zmin: 0, zmax: 10 }
    const pose = computeCameraPreset('front', offCenter)
    expect(pose.target[0]).toBeCloseTo(100)
  })

  it('falls back to a reasonable default when no model has been generated yet', () => {
    const pose = computeCameraPreset('perspective', null)
    expect(pose.position.every((n) => Number.isFinite(n))).toBe(true)
    expect(pose.target).toEqual([0, 0, 0])
  })
})

describe('computeFitPose', () => {
  it('is equivalent to the three_quarter preset', () => {
    expect(computeFitPose(RING_BBOX)).toEqual(computeCameraPreset('three_quarter', RING_BBOX))
  })
})

describe('computeGroundY', () => {
  it('matches the scene-space minimum Y used for grounding', () => {
    expect(computeGroundY(RING_BBOX)).toBeCloseTo(backendBoundingBoxToScene(RING_BBOX).minY)
  })
})
