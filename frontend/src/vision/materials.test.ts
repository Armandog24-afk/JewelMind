import { describe, expect, it } from 'vitest'
import { allMetalKeys, resolveMetalMaterial, resolveStoneMaterial } from './materials'

describe('resolveMetalMaterial', () => {
  it('produces a visibly distinct color for every one of the 5 current metals, in presentation mode', () => {
    const colors = allMetalKeys().map((key) => resolveMetalMaterial(key, 'presentation').color)
    expect(new Set(colors).size).toBe(5)
  })

  it('produces a visibly distinct color for every one of the 5 current metals, in technical mode', () => {
    const colors = allMetalKeys().map((key) => resolveMetalMaterial(key, 'technical').color)
    expect(new Set(colors).size).toBe(5)
  })

  it('falls back to a known preset for an unrecognized metal key rather than throwing', () => {
    expect(() => resolveMetalMaterial('unobtainium', 'presentation')).not.toThrow()
    const fallback = resolveMetalMaterial('unobtainium', 'presentation')
    expect(fallback.color).toBe(resolveMetalMaterial('yellow_gold_18k', 'presentation').color)
  })

  it('gives technical mode zero environment contribution and presentation mode a real one', () => {
    expect(resolveMetalMaterial('platinum', 'technical').envMapIntensity).toBe(0)
    expect(resolveMetalMaterial('platinum', 'presentation').envMapIntensity).toBeGreaterThan(0)
  })
})

describe('resolveStoneMaterial', () => {
  it('gives presentation mode real transmission and technical mode none', () => {
    expect(resolveStoneMaterial('presentation').transmission).toBeGreaterThan(0)
    expect(resolveStoneMaterial('technical').transmission).toBe(0)
  })

  it('keeps the stone visually distinct from every metal color', () => {
    const stoneColor = resolveStoneMaterial('technical').color
    const metalColors = allMetalKeys().map((key) => resolveMetalMaterial(key, 'technical').color)
    expect(metalColors).not.toContain(stoneColor)
  })
})
