---
id: JM-BIBLE-120
title: Atlas Governance
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-090
related_documents:
  - JM-BIBLE-ATLAS-README
implementation_status: current
professional_validation: not_required
normative: true
---

# Atlas Governance

## ATLAS-GOV-001 through ATLAS-GOV-015

| ID | Rule |
|---|---|
| **ATLAS-GOV-001** | Atlas must remain jewelry-domain agnostic where practical. Atlas code answers "can this geometry be built, and what does it measure" — never "is this appropriate for a solitaire ring." |
| **ATLAS-GOV-002** | Jewelry-specific thresholds belong to Forge, not Atlas. A concrete counter-example already in the codebase: `build_prongs()` will construct *any* non-negative prong count — the `{4, 6}` restriction is enforced entirely by Forge's `JM-PRONG-001`, not by the geometry builder (see [`149-current-solitaire-geometry-mapping.md`](149-current-solitaire-geometry-mapping.md)). This is the correct pattern; new geometry code should follow it. |
| **ATLAS-GOV-003** | Atlas operations must be deterministic for identical canonical inputs and versions — see [`137-determinism-and-reproducibility.md`](137-determinism-and-reproducibility.md). |
| **ATLAS-GOV-004** | Geometry failures must never be silently ignored — every `try/except` around a CadQuery/OpenCascade operation must either re-raise, or record a warning and take a documented fallback (never swallow silently). |
| **ATLAS-GOV-005** | Fallback geometry must be reported — see [`135-fillets-rounding-and-fallbacks.md`](135-fillets-rounding-and-fallbacks.md) and [`atlas-fallback-register.md`](../appendices/atlas-fallback-register.md). |
| **ATLAS-GOV-006** | Required components must never disappear silently — a component with zero solids still appears in the manifest with `"file": null`, never omitted entirely (confirmed current behavior — see [`144-preview-mesh-contract.md`](144-preview-mesh-contract.md)). |
| **ATLAS-GOV-007** | Stone reference must remain distinguishable from production metal at every stage — see [`143-stone-metal-separation-contract.md`](143-stone-metal-separation-contract.md) and LAW-006. |
| **ATLAS-GOV-008** | All internal linear geometry uses millimeters — restates LAW-007 for Atlas specifically. |
| **ATLAS-GOV-009** | Meshes must not become the source of B-Rep truth — see [`129-mesh-model.md`](129-mesh-model.md). STL is always derived from, never a substitute for, the B-Rep solid. |
| **ATLAS-GOV-010** | Preview geometry must originate from the generated model — the frontend never constructs its own geometry; every preview mesh is tessellated from a real backend-generated component (see [`144-preview-mesh-contract.md`](144-preview-mesh-contract.md)). |
| **ATLAS-GOV-011** | Exports must use explicit component-inclusion rules — `includeStoneReference` is an explicit, opt-in parameter, never an implicit default (LAW-006). |
| **ATLAS-GOV-012** | Topology assumptions must be documented — see [`128-brep-and-topology-model.md`](128-brep-and-topology-model.md) and [`123-coordinate-system-and-orientation.md`](123-coordinate-system-and-orientation.md). |
| **ATLAS-GOV-013** | Every geometry-driving parameter must be traceable to a JDL field path — see [`149-current-solitaire-geometry-mapping.md`](149-current-solitaire-geometry-mapping.md) and `sourceJDLPaths` in [`130-component-contract.md`](130-component-contract.md). |
| **ATLAS-GOV-014** | Every derived geometric value must have a deterministic derivation — every constant/formula in `geometry/constants.py` and each builder is a pure function of the definition, never of wall-clock time, randomness, or external state. |
| **ATLAS-GOV-015** | Geometry changes affecting public outputs require regression tests — see [`backend/tests/test_geometry.py`](../../../backend/tests/test_geometry.py) and the test-category requirements in this section's testing-strategy discussion (folded into [`132-construction-pipeline.md`](132-construction-pipeline.md) and [`150-atlas-gap-analysis.md`](150-atlas-gap-analysis.md) for this Sprint). |

## When an ADR is required

Replacing or wrapping the CadQuery/OpenCascade kernel; changing the coordinate convention; changing which components are required vs. optional in the solitaire assembly; changing default export component-inclusion behavior; or any change that violates ATLAS-GOV-001 through ATLAS-GOV-015 without superseding this document first.

## When an RFC is required

Adding a new geometric component family (a new component type beyond band/stone_reference/prongs/basket_support) or a new ring style's geometry, per [`04-jewelry-domain/056-domain-extension-strategy.md`](../04-jewelry-domain/056-domain-extension-strategy.md)'s workflow extended to geometry. Adding a new profile variant (e.g. a new band profile) to an *existing* component family follows the same RFC path as the equivalent JDL/domain extension, since it also touches enum membership.
