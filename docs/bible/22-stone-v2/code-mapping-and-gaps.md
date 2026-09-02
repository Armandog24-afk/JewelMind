---
id: JM-BIBLE-618
title: "Stone v2 Code Mapping and Gaps"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-09-02
source_of_truth: true
depends_on:
  - JM-BIBLE-600
related_documents:
  - JM-BIBLE-619
implementation_status: current
professional_validation: not_required
normative: false
---

# Stone v2 Code Mapping and Gaps

## Where the code is

| Concern | File |
|---|---|
| Source modes, profiles, families, anchors, provenance (kernel-neutral) | `backend/jewelmind/stone/models.py` |
| Shape and source registries | `backend/jewelmind/stone/capability.py` |
| Custom outline validation and normalization | `backend/jewelmind/stone/outline_validation.py` |
| Anchor derivation | `backend/jewelmind/stone/anchors.py` |
| Canonicalization (`canonicalize_stone`) | `backend/jewelmind/stone/normalize.py` |
| Source dispatch registry | `backend/jewelmind/stone/dispatch.py` |
| Asset store, format detection, import normalization | `backend/jewelmind/stone/importing.py` |
| Structured errors | `backend/jewelmind/stone/errors.py` |
| 2D outline primitives (all 20) | `backend/jewelmind/geometry/stone/outline.py` |
| 3D profile builders | `backend/jewelmind/geometry/stone/profile.py` |
| Placement adapter + round fast path | `backend/jewelmind/geometry/stone/builder.py` |
| Dimension resolution (shared with Forge) | `backend/jewelmind/domain/stone_dimensions.py` |
| JDL schema | `backend/jewelmind/domain/schema.py` |
| Stone → Setting interface | `backend/jewelmind/setting/stone_interface.py` |
| Inspection facts | `backend/jewelmind/geometry/inspection/inspector.py` |

## The audit the brief asked for (section 84)

| Looked for | Found | Classification | Action |
|---|---|---|---|
| `stone.diameter` assumptions | `resolved_*_mm` asserted named-cut fields | ARCHITECTURAL LEAK | Fixed — handles custom, refuses imported |
| Switches assuming seven shapes | Setting's hardcoded shape lists | ARCHITECTURAL LEAK | Fixed — derived from the Stone registry |
| Setting tied to shape names | `shape == "round"` in placement and outline lookup | ARCHITECTURAL LEAK | Fixed — reads `isRadiallySymmetric`; round registered in the builder table |
| Designer vocabulary hardcoded | 6 newly-real shapes listed as unsupported; 2 canonical IDs missing from aliases | ARCHITECTURAL LEAK | Fixed — both derived from the registry |
| Spec assuming named parametric stone | Printed only shape/diameter/length/width | ARCHITECTURAL LEAK | Fixed — full source-aware section |
| Inspection assuming solid B-Rep | Volume read unconditionally | ARCHITECTURAL LEAK | Fixed — mesh reports 0 solids, null volume |
| Cache identity ignoring asset hash | — | VALID CURRENT | `assetHash` is in JDL, so it is in `definitionHash` |
| Stone code importing Ring | — | VALID CURRENT | Zero, AST-verified |
| Studio drop-down duplicated | `STONE_SHAPE_OPTIONS` is a hand mirror | VALID CURRENT | Documented as a mirror; no runtime access to the Python registry |
| Foundry assuming CadQuery B-Rep | Exporters handle whatever shape they are given | REQUIRES_EVOLUTION | A mesh stone in a STEP export is untested; stones are excluded by default |
| Review package assuming parametric | Bundles current artifacts generically | VALID CURRENT | Provenance now flows through the specification |

## Bugs found and fixed this sprint

Each was found by **exercising real objects**, not by reading code — the same
method that found all five Sprint 19 leaks.

1. **Forge crashed on an imported stone.** `_stone_rules` called
   `resolved_length_mm()` unconditionally, which correctly refuses for
   `IMPORTED_CAD`, so validation raised instead of validating. Scoped.

2. **Forge fired on every valid pearl.** `STONE_DEPTH_RANGE` asserts
   `depth < min(length, width)`; for a sphere that is `d < d`. Scoped away
   rather than loosened.

3. **Mesh transforms did nothing.** Neither `Shape.scale()` nor
   `BRepBuilderAPI_Transform` moves a triangulation. An STL declared in
   centimetres came back at millimetre size **while provenance claimed the
   conversion had happened.** Fixed with node-level transformation.

4. **`half_moon` was not centred on the origin.** `ellipseArc(...,
   startAtCurrent=False)` centres on the current point. Its bounding-box *size*
   was correct, so only a centre assertion caught it.

5. **Three shapes overshot their requested dimensions** — shield, trillion,
   half_moon — and heart's normalization had not converged. All fixed at the
   source.

6. **A pearl request failed deep in the outline builder**, because `profile`
   defaults to `FACETED_REFERENCE` and a sphere supports only
   `SPHERICAL_REFERENCE`. Fixed with recorded default resolution.

7. **A non-simple outline passed validation.** A vertex touching a distant edge
   is not a proper crossing. Added the touching check.

8. **Designer produced a dead end** for a shape named without dimensions.
   Now asks a structured question per missing dimension (brief section 39).

## Real gaps, recorded rather than closed

### Geometry

- **The head floats above the band for a footprint above ~7.5mm.**
  Pre-existing and size-driven, not shape-specific: `round d=8.0` reproduces it
  exactly. Recorded in `STV2-001-heart-prong`'s known limitations with the full
  measurement table. Surfaced by Sprint 20's wider coverage; not caused by it.
- **No outline projection from imported geometry.** This is what keeps imported
  stones `UNSUPPORTED` for both settings.
- **No seat, bearing or cutter geometry** for any setting — carried from
  Sprint 19, unchanged.

### Rules

- **`pearl` has no diameter-range rule.** `STONE_DIAMETER_RANGE` remains
  ROUND_ONLY. Extending it would need a sourced range for spherical stones, and
  inventing one is forbidden (STONEV2-GOV-011).
- **A non-round shape's `length`/`width` have no individual range rule.**
  Carried from Sprint 18, still open, still not closed by invention.
- **No custom-outline complexity rule.** A 9,999-point outline is structurally
  valid and would be unmanufacturable. No sourced threshold exists.

### Sources

- **Measured stones have no girdle measurements and no tolerance model.**
  Recording an uncertainty would need a sourced tolerance.
- **`MEASURED` cannot use a non-native shape.** A measured stone with no known
  cut must currently pick a named shape or supply an outline; it cannot be
  `shape: null` with dimensions only.
- **Concave custom outlines are not bezel-verified for every concavity.** They
  generate valid geometry; a deep enough notch could make a constant offset
  self-intersect, and that has not been characterized.

### Coverage

- **No Golden ring case for pearl or imported stones**, because no setting will
  grip them. Covered by unit tests and import vectors instead. A stone-only
  Golden category is the obvious future change.
- **A mesh stone has never been exported to STEP.** Stones are excluded from
  production exports by default, so this is untested rather than broken.

### Frontend

- **No custom-outline editor.** Deliberate — brief section 59 defers freeform
  modelling to Sprint 32. A custom outline is supplied through the API.
- **No stone-source selector in Studio.** The runtime capability exists and the
  UI does not, which is the honest order: brief section 58 says not to show fake
  UI. Studio currently offers parametric shapes and profiles only.
- **No import upload UI.** Same reasoning.

## Cross-references

- [`open-stone-v2-questions.md`](open-stone-v2-questions.md)
- [`../21-setting/code-mapping-and-gaps.md`](../21-setting/code-mapping-and-gaps.md)
- [`../06-forge/111-domain-rule-gap-analysis.md`](../06-forge/111-domain-rule-gap-analysis.md)
