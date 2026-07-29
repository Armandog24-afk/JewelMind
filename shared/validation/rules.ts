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
  MANUFACTURING_MIN_FEATURE: 'JM-MANUFACTURING-001',
  GEOMETRY_OUTER_BAND_POSITIVE: 'JM-GEOMETRY-001',
} as const
