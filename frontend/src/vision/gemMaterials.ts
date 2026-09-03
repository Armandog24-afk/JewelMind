import type { GemIdentity, GemVisualProfile } from '@shared/types/jewelry-definition'

/**
 * Gem-driven stone appearance (Sprint 21, brief section 22).
 *
 * Vision derives a stone's look from the ACTUAL gem identity in the design.
 * There is deliberately no frontend-only gem identity here: the backend
 * registry is authoritative, and this module only knows how to *render* a
 * profile it is handed.
 *
 * EVERY VALUE IN A PROFILE IS A RENDERING PARAMETER, NOT A MEASUREMENT. `ior`
 * is what the renderer is given to make a stone look plausible on screen, never
 * a laboratory refractive index, and `dispersion` drives a sparkle effect
 * rather than describing real spectral separation.
 *
 * WHY THERE IS A LOCAL PROFILE TABLE AT ALL. The viewer must render before, and
 * independently of, any network round trip — a stale or failed
 * `GET /api/gems` must never leave a stone unrendered. So this module keeps a
 * presentation table for the profile IDs the backend currently defines, and
 * falls back safely for anything it does not recognize.
 *
 * That makes it a MIRROR, with the usual obligation: it must never invent a
 * profile the backend does not have, and a profile added to
 * `backend/jewelmind/gem/visual.py` should be added here in the same change.
 * `gemMaterials.test.ts` pins the fallback behaviour so an unmirrored profile
 * degrades visibly rather than silently rendering as something else.
 */

export interface StoneMaterialParams {
  color: string
  metalness: number
  roughness: number
  opacity: number
  transmission: number
  ior: number
  thickness: number
  clearcoat: number
  envMapIntensity: number
}

/**
 * The generic fallback appearance, mirroring `FALLBACK_PROFILE` in
 * `backend/jewelmind/gem/visual.py`.
 *
 * Deliberately NEUTRAL rather than diamond-like. Falling back to a brilliant
 * white stone would make an unidentified gem look like the most valuable
 * possible reading of itself, which is the one appearance a fallback must never
 * have.
 */
export const FALLBACK_GEM_PROFILE_ID = 'fallback.generic'

const PRESENTATION: Record<string, StoneMaterialParams> = {
  'fallback.generic': {
    color: '#c9ccd1', metalness: 0, roughness: 0.25, opacity: 0.85,
    transmission: 0.35, ior: 1.5, thickness: 0.6, clearcoat: 0.2,
    envMapIntensity: 0.8,
  },
  'colourless.brilliant': {
    color: '#f2f8ff', metalness: 0, roughness: 0.02, opacity: 1,
    transmission: 0.95, ior: 2.4, thickness: 1.2, clearcoat: 1,
    envMapIntensity: 1.5,
  },
  'colourless.moderate': {
    color: '#f0f4f8', metalness: 0, roughness: 0.05, opacity: 1,
    transmission: 0.9, ior: 1.8, thickness: 1, clearcoat: 0.6,
    envMapIntensity: 1.2,
  },
  'red.deep': {
    color: '#9b1128', metalness: 0, roughness: 0.04, opacity: 1,
    transmission: 0.72, ior: 1.77, thickness: 1.4, clearcoat: 0.8,
    envMapIntensity: 1.2,
  },
  'blue.deep': {
    color: '#123c8c', metalness: 0, roughness: 0.04, opacity: 1,
    transmission: 0.72, ior: 1.77, thickness: 1.4, clearcoat: 0.8,
    envMapIntensity: 1.2,
  },
  'green.deep': {
    color: '#0f7a4a', metalness: 0, roughness: 0.08, opacity: 1,
    transmission: 0.62, ior: 1.58, thickness: 1.5, clearcoat: 0.5,
    envMapIntensity: 1,
  },
  'green.light': {
    color: '#9bc53d', metalness: 0, roughness: 0.05, opacity: 1,
    transmission: 0.78, ior: 1.65, thickness: 1.1, clearcoat: 0.6,
    envMapIntensity: 1.1,
  },
  'blue.pale': {
    color: '#a8dbe8', metalness: 0, roughness: 0.05, opacity: 1,
    transmission: 0.85, ior: 1.58, thickness: 1, clearcoat: 0.6,
    envMapIntensity: 1.1,
  },
  'violet.medium': {
    color: '#7a4fb5', metalness: 0, roughness: 0.05, opacity: 1,
    transmission: 0.8, ior: 1.55, thickness: 1.1, clearcoat: 0.6,
    envMapIntensity: 1.1,
  },
  'yellow.warm': {
    color: '#e0a12c', metalness: 0, roughness: 0.05, opacity: 1,
    transmission: 0.82, ior: 1.55, thickness: 1.1, clearcoat: 0.6,
    envMapIntensity: 1.1,
  },
  'pink.medium': {
    color: '#e0719a', metalness: 0, roughness: 0.05, opacity: 1,
    transmission: 0.8, ior: 1.62, thickness: 1.1, clearcoat: 0.7,
    envMapIntensity: 1.1,
  },
  'orange.warm': {
    color: '#c4581f', metalness: 0, roughness: 0.05, opacity: 1,
    transmission: 0.74, ior: 1.75, thickness: 1.2, clearcoat: 0.7,
    envMapIntensity: 1.1,
  },
  'brown.warm': {
    color: '#8a4b2a', metalness: 0, roughness: 0.06, opacity: 1,
    transmission: 0.7, ior: 1.62, thickness: 1.2, clearcoat: 0.5,
    envMapIntensity: 1,
  },
  'translucent.green': {
    color: '#4f8f6b', metalness: 0, roughness: 0.22, opacity: 1,
    transmission: 0.32, ior: 1.66, thickness: 2, clearcoat: 0.25,
    envMapIntensity: 0.7,
  },
  'translucent.warm': {
    color: '#d69a3c', metalness: 0, roughness: 0.3, opacity: 1,
    transmission: 0.4, ior: 1.54, thickness: 1.8, clearcoat: 0.2,
    envMapIntensity: 0.6,
  },
  'translucent.moonstone': {
    color: '#dfe6ef', metalness: 0, roughness: 0.12, opacity: 1,
    transmission: 0.5, ior: 1.52, thickness: 1.5, clearcoat: 0.4,
    envMapIntensity: 0.9,
  },
  'opaque.turquoise': {
    color: '#41b3b8', metalness: 0, roughness: 0.45, opacity: 1,
    transmission: 0, ior: 1.61, thickness: 0, clearcoat: 0.15,
    envMapIntensity: 0.5,
  },
  'opaque.coral': {
    color: '#d95f52', metalness: 0, roughness: 0.4, opacity: 1,
    transmission: 0, ior: 1.5, thickness: 0, clearcoat: 0.2,
    envMapIntensity: 0.5,
  },
  'iridescent.opal': {
    color: '#dfe9f2', metalness: 0, roughness: 0.15, opacity: 1,
    transmission: 0.45, ior: 1.45, thickness: 1.4, clearcoat: 0.5,
    envMapIntensity: 1,
  },
  'pearlescent.white': {
    color: '#f4ece1', metalness: 0.15, roughness: 0.18, opacity: 1,
    transmission: 0, ior: 1.53, thickness: 0, clearcoat: 0.7,
    envMapIntensity: 1.1,
  },
}

/**
 * Technical mode keeps the gem's colour recognizable but flat and without
 * environment reflections, since inspection — not beauty — is the goal.
 *
 * Derived from the presentation table rather than hand-written, so the two can
 * never disagree about which profiles exist. The same discipline
 * `materials.ts` already applies to metals.
 */
const TECHNICAL: Record<string, StoneMaterialParams> = Object.fromEntries(
  Object.entries(PRESENTATION).map(([key, preset]) => [
    key,
    {
      ...preset,
      roughness: Math.max(preset.roughness, 0.35),
      opacity: 0.6,
      transmission: 0,
      ior: 1,
      thickness: 0,
      clearcoat: 0,
      envMapIntensity: 0,
    },
  ]),
) as Record<string, StoneMaterialParams>

/** Every profile ID this module can render. Exported for the mirror test. */
export function mirroredProfileIds(): string[] {
  return Object.keys(PRESENTATION)
}

/**
 * The stone appearance for a gem identity.
 *
 * `profileId` is resolved from the identity's override first, then the entry's
 * default (supplied by the caller from backend data), then the fallback. An
 * unrecognized ID renders as the neutral fallback — never as some other gem.
 */
export function resolveGemMaterial(
  profileId: string | null | undefined,
  mode: 'technical' | 'presentation',
): StoneMaterialParams {
  const table = mode === 'presentation' ? PRESENTATION : TECHNICAL
  // The lookups are non-null-asserted deliberately: both tables are keyed by
  // the same literal set, and `FALLBACK_GEM_PROFILE_ID` is one of those keys —
  // a fact `gemMaterials.test.ts` pins, so the assertion cannot silently
  // become false.
  const fallback = table[FALLBACK_GEM_PROFILE_ID] as StoneMaterialParams
  if (profileId && profileId in table) {
    return table[profileId] as StoneMaterialParams
  }
  return fallback
}

/**
 * Whether this module recognizes a profile ID.
 *
 * Lets a caller tell "rendered with the gem's own appearance" from "rendered
 * with a generic fallback", which the UI surfaces rather than hiding
 * (brief section 22: the fallback must be represented AS a fallback).
 */
export function isMirroredProfile(profileId: string | null | undefined): boolean {
  return Boolean(profileId && profileId in PRESENTATION)
}

/**
 * The visual profile ID a gem identity should render with, given the registry
 * entry's default.
 *
 * `entryDefaultProfileId` comes from backend data. When it is unavailable —
 * the registry has not loaded yet — the fallback is used, so a stone always
 * renders.
 */
export function profileIdForGem(
  gem: GemIdentity | null | undefined,
  entryDefaultProfileId?: string | null,
): string {
  return (
    gem?.visualProfileId ?? entryDefaultProfileId ?? FALLBACK_GEM_PROFILE_ID
  )
}

/** Narrow a backend `GemVisualProfile` to the fields a renderer needs. */
export function paramsFromBackendProfile(
  profile: GemVisualProfile,
): StoneMaterialParams {
  return {
    color: profile.baseColor,
    metalness: profile.metalness,
    roughness: profile.roughness,
    opacity: profile.opacity,
    transmission: profile.transmission,
    ior: profile.ior,
    thickness: profile.thickness,
    clearcoat: profile.clearcoat,
    envMapIntensity: profile.envMapIntensity,
  }
}
