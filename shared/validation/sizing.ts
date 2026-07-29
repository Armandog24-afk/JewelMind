/**
 * EU ring size <-> inner diameter conversion.
 *
 * Mirrors backend/jewelmind/validation/sizing.py exactly — same convention,
 * same thresholds. Convention used (French/EU civil ring sizing):
 *
 *   size = (pi * inner_diameter_mm) - 40
 *   inner_diameter_mm = (size + 40) / pi
 *
 * JewelMind never silently rewrites one field from the other; this utility
 * only classifies how consistent the two fields currently are.
 */

const INFO_THRESHOLD_MM = 0.15
const WARNING_THRESHOLD_MM = 0.5

export function euSizeToInnerDiameter(size: number): number {
  return (size + 40) / Math.PI
}

export function innerDiameterToEuSize(innerDiameterMm: number): number {
  return Math.PI * innerDiameterMm - 40
}

export type SizingConsistency = 'information' | 'warning' | null

export function sizingConsistency(size: number, innerDiameterMm: number): SizingConsistency {
  const impliedDiameter = euSizeToInnerDiameter(size)
  const delta = Math.abs(impliedDiameter - innerDiameterMm)

  if (delta <= INFO_THRESHOLD_MM) return null
  if (delta <= WARNING_THRESHOLD_MM) return 'information'
  return 'warning'
}
