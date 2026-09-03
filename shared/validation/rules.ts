export type Severity = 'error' | 'warning' | 'information'

export interface ValidationResult {
  ruleId: string
  severity: Severity
  message: string
  parameter: string
  suggestedValue?: number | string | null
}

// Mirrors backend/jewelmind/validation/rules.py — keep identifiers in sync.
export const RULE_IDS = {
  RING_INNER_DIAMETER_RANGE: 'JM-RING-001',
  RING_SIZE_RANGE: 'JM-RING-002',
  RING_SIZE_DIAMETER_CONSISTENCY: 'JM-RING-003',
  BAND_WIDTH_MIN: 'JM-BAND-001',
  BAND_THICKNESS_MIN: 'JM-BAND-002',
  BAND_WIDTH_MAX: 'JM-BAND-003',
  STONE_DIAMETER_RANGE: 'JM-STONE-001',
  STONE_DEPTH_RANGE: 'JM-STONE-002',
  PRONG_COUNT: 'JM-PRONG-001',
  PRONG_DIAMETER_MIN: 'JM-PRONG-002',
  PRONG_COUNT_VS_STONE_SIZE: 'JM-PRONG-003',
  PRONG_HEIGHT_VS_BASKET: 'JM-PRONG-004',
  SETTING_BASKET_HEIGHT_POSITIVE: 'JM-SETTING-001',
  SETTING_BASKET_HEIGHT_MAX: 'JM-SETTING-002',
  // Sprint 19, BEZEL_ONLY, both ENGINEERING_INVARIANT (constructibility,
  // not a jewelry threshold). No minimum bezel wall dimension is asserted.
  BEZEL_WALL_THICKNESS_POSITIVE: 'JM-SETTING-003',
  BEZEL_WALL_HEIGHT_POSITIVE: 'JM-SETTING-004',
  // Sprint 21 — GEM_IDENTITY_ONLY. Referential and coherence invariants
  // only; no gemological or manufacturing claim.
  GEM_REFERENCE_EXISTS: 'JM-GEM-001',
  GEM_ORIGIN_APPLICABLE: 'JM-GEM-002',
  GEM_CUSTOM_COHERENT: 'JM-GEM-003',
  GEM_VISUAL_PROFILE_RESOLVES: 'JM-GEM-004',
  GEM_TREATMENT_COHERENT: 'JM-GEM-005',
  GEM_ENTRY_DEPRECATED: 'JM-GEM-006',
  MANUFACTURING_MIN_FEATURE: 'JM-MANUFACTURING-001',
  GEOMETRY_OUTER_BAND_POSITIVE: 'JM-GEOMETRY-001',
} as const
