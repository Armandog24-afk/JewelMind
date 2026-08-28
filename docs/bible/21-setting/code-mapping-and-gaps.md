---
id: JM-BIBLE-592
title: Setting Code Mapping and Gaps
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-27
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-SETTING-README
  - JM-BIBLE-580
related_documents:
  - JM-BIBLE-581
  - JM-BIBLE-590
implementation_status: current
professional_validation: not_required
normative: true
---

# Setting Code Mapping and Gaps

## File-by-file map

### New

| File | Responsibility |
|---|---|
| `setting/__init__.py` | Deliberately non-eager (imports nothing). |
| `setting/models.py` | `SettingDefinition`, `StoneSettingReference`, `SettingAttachmentInterface`, `ProngSettingDefinition`, `BezelSettingDefinition`, `SettingGeometryResult`, `SettingFallbackEvent`. All kernel-neutral. |
| `setting/capability.py` | `SETTING_CAPABILITIES`, `RESERVED_SETTING_FAMILIES`, `compatibility_status()`, `compatibility_matrix()`. |
| `setting/stone_interface.py` | The only place stone facts enter Setting. |
| `setting/placement.py` | `RADIAL` / `OUTLINE_CARDINAL` strategies and `resolve_strategy()`. |
| `setting/prong.py` | Prong generator. |
| `setting/bezel.py` | Bezel generator, including the STEP-safety repair. |
| `setting/dispatch.py` | `setting_generators()` registry (lazy, cached) and `generate_setting()`. |
| `setting/errors.py` | 8 structured error types. |
| `geometry/setting_adapter.py` | `JewelryDefinition` → Setting contracts. Ring-side by design. |
| `tests/test_setting.py` | 102 tests. |
| `tests/test_setting_schemas.py` | 22 tests. |
| `tests/test_setting_system_no_ring_dependency.py` | 13 tests (AST-based). |
| `tests/test_capability_coverage.py` | 16 tests. |

### Modified

| File | Change |
|---|---|
| `domain/schema.py` | `SettingType` gained `bezel`; `SettingSpec` gained two bezel fields. |
| `geometry/components/prongs.py` | Reduced to a thin adapter. |
| `geometry/assemblies/solitaire.py` | Builds the setting via the Setting System; `_fuse_metal()` generalized to a list. |
| `geometry/model.py` | `GeneratedModel` gained optional `setting_result` (typed `Any` to avoid a Setting import). |
| `geometry/roles.py` | `bezel` registered as production metal, included by default. |
| `geometry/inspection/models.py` | 8 new `FactType` values. |
| `geometry/inspection/inspector.py` | New `_setting_facts()`. |
| `geometry/inspection/assembly.py` | Setting-family-aware required components, prong count, inspection pairs, boolean ops. |
| `validation/engine.py` | `_prong_rules` scoped `PRONG_ONLY`; new `_bezel_rules`. |
| `validation/rules.py` | `JM-SETTING-003`/`004`. |
| `exporters/specification.py` | Family-aware setting section; prong count omitted when `NOT_APPLICABLE`. |
| `api/routes.py` | `metadata["prongs"]` no longer KeyErrors for a bezel; new `metadata["setting"]`. |
| `designer/normalizer.py` | IT/EN setting synonyms; bezel numeric fields. |
| `designer/capability.py` | `bezel` removed from unsupported concepts; bezel field paths added. |
| `shared/types/jewelry-definition.ts`, `shared/validation/engine.ts`, `shared/validation/rules.ts` | Mirrors. |
| `frontend/.../ConfigurationPanel.tsx` | Capability-driven setting selector + family-scoped fields. |

## The `stone.diameter`-style audit

Brief section 53 asked for a specific search. Results, classified:

| Location | Classification |
|---|---|
| `setting/placement.py::radial_positions` reads `reference.widthMm` | **VALID CURRENT BEHAVIOUR** — the resolved width, not `stone.diameter`. For round it *is* the diameter. |
| `geometry/constants.py::prong_center_radius` | **VALID CURRENT BEHAVIOUR** — already fixed in Sprint 18 to use `resolved_width_mm`; still used by the basket. |
| `designer/*` prong field paths | **VALID CURRENT BEHAVIOUR** — field-path strings, not value reads. |
| `exporters/specification.py` prong lines | **FIXED** — now inside a `type == "prong"` branch. |
| `api/routes.py::metadata["prongs"]` | **ARCHITECTURAL LEAK — FIXED** (see below). |
| `exporters/specification.py` inspection prong-count line | **ARCHITECTURAL LEAK — FIXED** (see below). |
| `validation/engine.py::_prong_rules` | **RULE_REQUIRES_SCOPING — FIXED** — now `PRONG_ONLY`. |
| `inspection/assembly.py` (three sites) | **ARCHITECTURAL LEAK — FIXED** (see below). |
| `design_intent/vocabulary.py` `"prongs"` concept | **VALID CURRENT BEHAVIOUR** — a semantic vocabulary term, not geometry. |
| Exporters constructing setting geometry | **None found** — exporters select components by role and never reconstruct geometry. |
| Vision reconstructing setting components | **None found** — Vision parses backend STL generically. |

### Leaks found and fixed: 5

1. **`api/routes.py` KeyError.** `record.generated_model.components["prongs"].metadata` was indexed unconditionally, so **every bezel generation would have crashed the API with a `KeyError`**. Found by exercising the real endpoint for both families rather than by reading. Now `None` when no prong component exists, with a new `metadata["setting"]` carrying the structured result.
2. **`inspection/assembly.py::REQUIRED_COMPONENT_NAMES`** hardcoded `prongs` → every valid bezel assembly inspected as `FAIL`.
3. **`inspection/assembly.py::_prong_count`** returned `FAIL` rather than `NOT_APPLICABLE` for a bezel.
4. **`inspection/assembly.py::_ALL_PAIRS`** was a constant over a hardcoded 4-name tuple, so the `bezel` component was **silently excluded** from all pairwise intersection/distance inspection. The subtlest of the five: nothing failed, facts were simply missing.
5. **`exporters/specification.py`** reported "Requested vs. generated prong count: 0 vs. 0" for a bezel, which reads as a defect.

Leaks 2–4 were all found by inspecting a real bezel model and asking why it reported `FAIL` — a code-reading pass would plausibly have missed leak 4 entirely.

### Tests that assumed all settings are prong

None found that break: the existing suites pass unchanged (1166 tests before the Setting suites were added). The prong assumptions lived in production code, not in test expectations.

## Honest remaining gaps

| Gap | Status | Why not closed |
|---|---|---|
| **No seat, bearing, or cutter geometry** | `PLANNED` for every family | Real manufacturing semantics; needs an RFC, not a geometric side effect. Stone/metal overlap is not a seat. |
| **Prong placement is not shape-optimized** | `EXPERIMENTAL` for all 6 non-round shapes | Marquise tips, pear tips, and angular corners are not targeted. Needs `V_PRONG` geometry and shape-specific strategies. |
| **No `V_PRONG` / `CLAW` / `SHARED_PRONG` styles** | `PLANNED` | Sprint 23 territory. |
| **`basket_support` ownership unresolved** | `PARTIAL` | Genuinely both setting support and ring attachment; not force-split (brief section 23). |
| **Prongs are one compound, not individual components** | Accepted design decision | Splitting exceeds "smallest safe refactor"; per-prong facts provided instead. |
| **No minimum bezel wall dimension rule** | REQUIRES_PROFESSIONAL_VALIDATION | No sourced professional minimum exists; inventing one is forbidden. |
| **`tipDirectionY` / `isBilaterallySymmetric` unconsumed** | Recorded, not load-bearing | Present on the interface for a future tip-aware strategy; no strategy reads them yet. |
| **Attachment interface is minimal** | Deliberate | Attachment region/anchors have no consumer yet; adding unread fields would be speculative capability. |
| **`definitionHash` drift on additive change** | Standing tension | Third occurrence; recorded in the JDL compatibility matrix. |
| **No professionally validated setting** | `NOT_REVIEWED` | No human evidence exists. |

## Layer-boundary audit

| Boundary | Status |
|---|---|
| Setting → Ring | **Clean.** Zero imports, AST-verified, including `JewelryDefinition`. |
| Setting → jewelry_category | **Clean.** |
| Setting → Shank / connection / adapter | **Clean.** |
| Setting → Forge | **Clean.** No `jewelmind.validation` import. |
| Setting → Stone | **Present and intended** — via `stone_interface.py` only. |
| Ring → Setting | **Present and intended** — via `setting_adapter.py`. |
| Exporters → setting geometry | **Clean.** Role-based selection only. |
| Vision → setting geometry | **Clean.** Generic STL parsing. |

## Note on a corrected count

`setting/prong.py`'s docstring originally said splitting the prong compound would affect "all 18 Golden baselines" — true when written, before this Sprint added five Setting cases. Corrected to 23 in the same change rather than left to drift.
