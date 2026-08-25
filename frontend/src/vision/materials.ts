import type { MetalType } from '@shared/types/jewelry-definition'

/**
 * Centralized Vision material presets. Nothing outside this module may
 * hardcode a metal color or the stone color — see
 * docs/bible/10-vision/231-material-system.md and
 * docs/bible/10-vision/232-metal-material-model.md.
 *
 * These are visual approximations for on-screen display, not a claim of
 * spectral/optical accuracy for any real metal or gemstone.
 */

export interface MetalMaterialParams {
  color: string
  metalness: number
  roughness: number
  envMapIntensity: number
}

const METAL_PRESENTATION_PRESETS: Record<MetalType, MetalMaterialParams> = {
  yellow_gold_18k: { color: '#d4af37', metalness: 0.95, roughness: 0.28, envMapIntensity: 1 },
  white_gold_18k: { color: '#e7e7ea', metalness: 0.95, roughness: 0.2, envMapIntensity: 1 },
  rose_gold_18k: { color: '#e3b7a4', metalness: 0.95, roughness: 0.3, envMapIntensity: 1 },
  platinum: { color: '#dcdcdc', metalness: 0.95, roughness: 0.18, envMapIntensity: 1 },
  silver: { color: '#c8c8ce', metalness: 0.95, roughness: 0.24, envMapIntensity: 1 },
}

/** Technical mode keeps the selected metal recognizable but flatter and
 * without environment reflections, since inspection — not beauty — is
 * the goal (see docs/bible/10-vision/227-technical-view-contract.md). */
const METAL_TECHNICAL_PRESETS: Record<MetalType, MetalMaterialParams> = Object.fromEntries(
  (Object.entries(METAL_PRESENTATION_PRESETS) as Array<[MetalType, MetalMaterialParams]>).map(
    ([key, preset]) => [key, { ...preset, metalness: 0.55, roughness: 0.55, envMapIntensity: 0 }],
  ),
) as Record<MetalType, MetalMaterialParams>

const FALLBACK_METAL: MetalType = 'yellow_gold_18k'

export function resolveMetalMaterial(metal: string, mode: 'technical' | 'presentation'): MetalMaterialParams {
  const table = mode === 'presentation' ? METAL_PRESENTATION_PRESETS : METAL_TECHNICAL_PRESETS
  return table[metal as MetalType] ?? table[FALLBACK_METAL]
}

export function allMetalKeys(): MetalType[] {
  return Object.keys(METAL_PRESENTATION_PRESETS) as MetalType[]
}

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

/** StoneReference is not a certified gemstone model (LAW-006) — these
 * parameters are a stylized "clear gemstone-like" look, never a claim of
 * physically accurate diamond optics. See
 * docs/bible/10-vision/233-stone-material-model.md. */
export const STONE_TECHNICAL_MATERIAL: StoneMaterialParams = {
  color: '#bfe3ff',
  metalness: 0.1,
  roughness: 0.05,
  opacity: 0.55,
  transmission: 0,
  ior: 1.0,
  thickness: 0,
  clearcoat: 0,
  envMapIntensity: 0,
}

export const STONE_PRESENTATION_MATERIAL: StoneMaterialParams = {
  color: '#eaf6ff',
  metalness: 0,
  roughness: 0.03,
  opacity: 1,
  transmission: 0.92,
  ior: 2.4,
  thickness: 1.2,
  clearcoat: 1,
  envMapIntensity: 1.4,
}

export function resolveStoneMaterial(mode: 'technical' | 'presentation'): StoneMaterialParams {
  return mode === 'presentation' ? STONE_PRESENTATION_MATERIAL : STONE_TECHNICAL_MATERIAL
}

export const BACKGROUND_COLOR: Record<'technical' | 'presentation', string> = {
  technical: '#15171a',
  presentation: '#dedad5',
}

/** Every field a mesh's material actually needs, with metal's
 * stone-only fields (transmission/ior/thickness/clearcoat) filled with
 * neutral defaults — a single shape avoids fragile `in`-narrowing across
 * a metal/stone union at every call site. */
export interface ResolvedComponentMaterial {
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

export function resolveComponentMaterial(
  isStone: boolean,
  metal: string,
  mode: 'technical' | 'presentation',
): ResolvedComponentMaterial {
  if (isStone) {
    return resolveStoneMaterial(mode)
  }
  const metalParams = resolveMetalMaterial(metal, mode)
  return {
    ...metalParams,
    opacity: 1,
    transmission: 0,
    ior: 1.5,
    thickness: 0,
    clearcoat: 0,
  }
}
