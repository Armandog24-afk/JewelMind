import { describe, expect, it } from 'vitest'

import {
  FALLBACK_GEM_PROFILE_ID,
  isMirroredProfile,
  mirroredProfileIds,
  paramsFromBackendProfile,
  profileIdForGem,
  resolveGemMaterial,
} from './gemMaterials'
import type { GemIdentity, GemVisualProfile } from '@shared/types/jewelry-definition'

const identity = (over: Partial<GemIdentity> = {}): GemIdentity => ({
  gemId: 'diamond',
  origin: 'NATURAL',
  treatments: [],
  visualProfileId: null,
  customName: null,
  note: null,
  ...over,
})

describe('resolveGemMaterial', () => {
  it('renders the fallback for an unrecognized profile in both modes', () => {
    const fallbackPresentation = resolveGemMaterial(
      FALLBACK_GEM_PROFILE_ID,
      'presentation',
    )
    expect(resolveGemMaterial('no.such.profile', 'presentation')).toEqual(
      fallbackPresentation,
    )
    expect(resolveGemMaterial(null, 'presentation')).toEqual(fallbackPresentation)
    expect(resolveGemMaterial(undefined, 'technical')).toEqual(
      resolveGemMaterial(FALLBACK_GEM_PROFILE_ID, 'technical'),
    )
  })

  it('keeps the fallback neutral rather than diamond-like', () => {
    // A fallback that looked like a brilliant colourless stone would make an
    // unidentified gem render as the most valuable reading of itself.
    const fallback = resolveGemMaterial(FALLBACK_GEM_PROFILE_ID, 'presentation')
    const brilliant = resolveGemMaterial('colourless.brilliant', 'presentation')
    expect(fallback).not.toEqual(brilliant)
    expect(fallback.transmission).toBeLessThan(brilliant.transmission)
    expect(fallback.ior).toBeLessThan(brilliant.ior)
  })

  it('pins the non-null assertion in the lookup: the fallback key exists', () => {
    expect(mirroredProfileIds()).toContain(FALLBACK_GEM_PROFILE_ID)
  })

  it('renders every mirrored profile in both modes', () => {
    for (const id of mirroredProfileIds()) {
      for (const mode of ['presentation', 'technical'] as const) {
        const params = resolveGemMaterial(id, mode)
        expect(params.color).toMatch(/^#[0-9a-fA-F]{6}$/)
        expect(params.metalness).toBeGreaterThanOrEqual(0)
        expect(params.roughness).toBeGreaterThanOrEqual(0)
        expect(params.opacity).toBeGreaterThan(0)
      }
    }
  })

  it('flattens technical mode: no transmission, no environment reflection', () => {
    for (const id of mirroredProfileIds()) {
      const technical = resolveGemMaterial(id, 'technical')
      expect(technical.transmission).toBe(0)
      expect(technical.envMapIntensity).toBe(0)
      expect(technical.clearcoat).toBe(0)
      expect(technical.roughness).toBeGreaterThanOrEqual(0.35)
    }
  })

  it('keeps a gem recognizable by colour in technical mode', () => {
    // Inspection, not beauty — but a ruby should still not read as a sapphire.
    expect(resolveGemMaterial('red.deep', 'technical').color).toBe(
      resolveGemMaterial('red.deep', 'presentation').color,
    )
    expect(resolveGemMaterial('red.deep', 'technical').color).not.toBe(
      resolveGemMaterial('blue.deep', 'technical').color,
    )
  })
})

describe('isMirroredProfile', () => {
  it('distinguishes a rendered gem appearance from a generic fallback', () => {
    expect(isMirroredProfile('colourless.brilliant')).toBe(true)
    expect(isMirroredProfile(FALLBACK_GEM_PROFILE_ID)).toBe(true)
    expect(isMirroredProfile('no.such.profile')).toBe(false)
    expect(isMirroredProfile(null)).toBe(false)
    expect(isMirroredProfile(undefined)).toBe(false)
  })
})

describe('profileIdForGem', () => {
  it('prefers the identity override over the registry default', () => {
    expect(
      profileIdForGem(identity({ visualProfileId: 'blue.pale' }), 'blue.deep'),
    ).toBe('blue.pale')
  })

  it('uses the registry default when the identity has no override', () => {
    expect(profileIdForGem(identity(), 'colourless.brilliant')).toBe(
      'colourless.brilliant',
    )
  })

  it('falls back when there is no gem and when the registry has not loaded', () => {
    expect(profileIdForGem(null)).toBe(FALLBACK_GEM_PROFILE_ID)
    expect(profileIdForGem(undefined)).toBe(FALLBACK_GEM_PROFILE_ID)
    expect(profileIdForGem(identity(), null)).toBe(FALLBACK_GEM_PROFILE_ID)
  })
})

describe('paramsFromBackendProfile', () => {
  it('narrows a backend profile without reinterpreting any value', () => {
    const profile: GemVisualProfile = {
      profileId: 'x.y',
      renderCategory: 'TRANSPARENT_COLOURED',
      baseColor: '#123456',
      metalness: 0.1,
      roughness: 0.2,
      opacity: 0.9,
      transmission: 0.5,
      ior: 1.7,
      thickness: 1.1,
      clearcoat: 0.3,
      envMapIntensity: 1.2,
      dispersion: 0.02,
      hasVariableColour: false,
      isFallback: false,
      description: 'test',
    }
    expect(paramsFromBackendProfile(profile)).toEqual({
      color: '#123456',
      metalness: 0.1,
      roughness: 0.2,
      opacity: 0.9,
      transmission: 0.5,
      ior: 1.7,
      thickness: 1.1,
      clearcoat: 0.3,
      envMapIntensity: 1.2,
    })
  })
})
