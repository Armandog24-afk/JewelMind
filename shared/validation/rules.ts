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

  // Sprint 23 — structural checks on the advanced head/prong fields. No
  // professional threshold: nothing here judges whether a prong is thick
  // enough or a head castable.
  SETTING_HEAD_PARAMETERS_COMPLETE: 'JM-SETTING-005',
  SETTING_FIELD_APPLICABLE: 'JM-SETTING-006',
  SETTING_SEAT_FEASIBLE: 'JM-SETTING-007',

  // Sprint 27 — EXTENDED_SETTING_MODES. A DELIBERATE SUBSET of the backend's
  // six rules (FORGE-GOV-004: this mirror may only ever enforce a subset, and
  // the backend's verdict always wins).
  //
  // Mirrored: 008 (the declared mode's family must match `setting.type`), 010
  // (a flush setting requires seat relief) and 012 (the mode requires
  // professional review). Each is checkable from the document alone with no
  // registry lookup.
  //
  // NOT mirrored, and each for a reason rather than an oversight:
  //   - JM-SETTING-009 (unread parameters) needs the backend's
  //     MODE_PARAMETER_FIELDS table, and duplicating it here would be a second
  //     copy of which mode reads which field.
  //   - JM-SETTING-011 (geometric feasibility) needs the stone's resolved
  //     dimensions and the same support arithmetic; the backend's exact check
  //     runs against the real measured solid.
  //   - JM-SETTING-013 (mode status) needs the capability registry, which the
  //     backend owns — the frontend must never define a capability status the
  //     backend has not.
  SETTING_MODE_FAMILY_MATCHES: 'JM-SETTING-008',
  SETTING_MODE_REQUIREMENTS_MET: 'JM-SETTING-010',
  SETTING_MODE_PROFESSIONAL_REVIEW: 'JM-SETTING-012',
  // Sprint 21 — GEM_IDENTITY_ONLY. Referential and coherence invariants
  // only; no gemological or manufacturing claim.
  GEM_REFERENCE_EXISTS: 'JM-GEM-001',
  GEM_ORIGIN_APPLICABLE: 'JM-GEM-002',
  GEM_CUSTOM_COHERENT: 'JM-GEM-003',
  GEM_VISUAL_PROFILE_RESOLVES: 'JM-GEM-004',
  GEM_TREATMENT_COHERENT: 'JM-GEM-005',
  GEM_ENTRY_DEPRECATED: 'JM-GEM-006',

  // Sprint 22 — ARRANGEMENT_ONLY, structural/referential only. No spacing,
  // proportion or density rule exists: each would need sourced professional
  // evidence this project does not have.
  ARRANGEMENT_INSTANCE_IDS_UNIQUE: 'JM-ARRANGE-001',
  ARRANGEMENT_REFERENCES_RESOLVE: 'JM-ARRANGE-002',
  ARRANGEMENT_STONE_REFERENCE_RESOLVES: 'JM-ARRANGE-003',
  ARRANGEMENT_STRUCTURE_RESOLVES: 'JM-ARRANGE-004',
  ARRANGEMENT_ROLE_COHERENT: 'JM-ARRANGE-005',
  ARRANGEMENT_GENERATION_PARTIAL: 'JM-ARRANGE-006',

  // Sprint 24 — structural checks on a multi-stone family. No proportion,
  // spacing or settability rule: each would need sourced professional
  // evidence this project does not have.
  FAMILY_SINGLE_PLACEMENT_AUTHORITY: 'JM-FAMILY-001',
  FAMILY_ROLES_VALID: 'JM-FAMILY-002',
  FAMILY_COMPILES: 'JM-FAMILY-003',
  FAMILY_REFERENCES_RESOLVE: 'JM-FAMILY-004',
  FAMILY_SETTING_COVERAGE: 'JM-FAMILY-005',

  // Sprint 25 — HALO_ONLY. A DOCUMENTED SUBSET is mirrored: JM-HALO-003
  // (composition support) and JM-HALO-004 (reference resolution) are decidable
  // from the document alone, so the client can report them instantly.
  // JM-HALO-001 (does the named centre exist in the real compiled placement),
  // JM-HALO-002 (does the real compiler accept it) and JM-HALO-005 (the
  // metal-coverage report) need the backend compiler and stay backend-only.
  // FORGE-GOV-004: the mirror may only ever be a subset.
  HALO_CENTER_RESOLVES: 'JM-HALO-001',
  HALO_COMPOSES: 'JM-HALO-002',
  HALO_COMPOSITION_SUPPORTED: 'JM-HALO-003',
  HALO_REFERENCES_RESOLVE: 'JM-HALO-004',
  HALO_SETTING_COVERAGE: 'JM-HALO-005',

  // Sprint 26 — PAVE_ONLY. A DOCUMENTED SUBSET is mirrored: JM-PAVE-004
  // (reference resolution), JM-PAVE-005 (the execution boundary and the
  // professional-review statement) and JM-PAVE-006 (pitch consistency, pure
  // arithmetic) are decidable from the document alone. JM-PAVE-001 (does the
  // host surface resolve), JM-PAVE-002 (does the real compiler accept it) and
  // JM-PAVE-003 (how many cells the surface clipped) need the backend's
  // resolved host surface and its compiler, and stay backend-only.
  // FORGE-GOV-004: the mirror may only ever be a subset.
  PAVE_HOST_RESOLVES: 'JM-PAVE-001',
  PAVE_COMPILES: 'JM-PAVE-002',
  PAVE_FIELD_CONTAINMENT: 'JM-PAVE-003',
  PAVE_REFERENCES_RESOLVE: 'JM-PAVE-004',
  PAVE_EXECUTION_BOUNDARY: 'JM-PAVE-005',
  PAVE_PITCH_CONSISTENCY: 'JM-PAVE-006',
  MANUFACTURING_MIN_FEATURE: 'JM-MANUFACTURING-001',
  GEOMETRY_OUTER_BAND_POSITIVE: 'JM-GEOMETRY-001',
} as const
