---
id: JM-BIBLE-476
title: Component Presence Inspection
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-INSPECTION-README
  - JM-BIBLE-460
related_documents:
  - JM-BIBLE-475
  - JM-BIBLE-465
  - JM-BIBLE-464
implementation_status: current
professional_validation: not_required
normative: true
---

# Component Presence Inspection

## The 4 required conceptual components

`REQUIRED_COMPONENT_NAMES = ("band", "stone_reference", "prongs", "basket_support")` (`assembly.py:27`, `backend/jewelmind/geometry/inspection/`). These are exactly the 4 keys `GeneratedModel.components` (`geometry/model.py`) ever contains for the current solitaire assembly — verified directly against `build_solitaire_ring()` (`geometry/assemblies/solitaire.py:74-88`), which constructs `components={"band": band, "stone_reference": stone, "prongs": prongs, "basket_support": basket}`.

## How presence is checked

`inspect_component()` (`components.py:19-94`) computes `exists = bool(shape.Solids())` for the component's real `cadquery.Shape` — presence means "this component's shape has at least one solid," never "this key exists in the dict with a non-`None` value." A component that is present in `model.components` but whose shape happens to produce zero solids is still reported, with `exists=False`, `status="FAIL"`, `solidCount=0`, `volumeMm3=0.0`, and an `INSPECTION_COMPONENT_MISSING` diagnostic (`severity="warning"`) naming it. This is INSPECT-GOV-014's "never repair silently" applied at the presence level: a genuinely empty component is reported as missing, not treated as absent-therefore-skipped.

At the assembly level, `inspect_assembly()` computes `missing = [n for n in REQUIRED_COMPONENT_NAMES if n not in model.components or not component_results[n].exists]` — a required name is "missing" if either the key itself is absent from `model.components`, or the key is present but its component reported `exists=False`. `AssemblyInspectionResult.requiredComponentsPresent = not missing` and `missingComponentIds = missing` surface this at the assembly scope; `GeometricFact`s of `factType="COMPONENT_PRESENT"` (one per component, `factId=f"component.{name}.exists"`) surface it at the flattened-fact level (`inspector.py::_component_facts()`).

## Prongs is one compound component, not six

This is the real current architecture, and it is worth stating plainly and explicitly at the presence-inspection level (the same finding [`475-prong-count-and-identity-inspection.md`](475-prong-count-and-identity-inspection.md) makes about identity, restated here about presence): `build_prongs()` (`geometry/components/prongs.py`) merges every individual prong solid into a single `cq.Compound` via `cq.Compound.makeCompound(solids)`, and that one compound becomes the single value at `model.components["prongs"]`. There is no `prong_0`, `prong_1`, ... key anywhere in `GeneratedModel.components` — confirmed directly by reading `solitaire.py`'s `components={...}` dict literal, which has exactly 4 keys, and by `TestAssemblyComponentCount::test_real_solitaire_has_4_components` (`backend/tests/test_geometry_inspection.py`), which asserts `assemblyResult.componentCount == 4` against real generated geometry.

Consequently, `inspect_component("prongs", ...)` reports one `ComponentInspectionResult` with `componentId="prongs"`, `exists=True`, and `solidCount=6` (or 4, for a supported alternate count) — a single component whose `solidCount` happens to be greater than 1, exactly the way `combined_metal`'s own multi-solid-fallback signal works (see [`478-boolean-result-inspection.md`](478-boolean-result-inspection.md)). Do not read `solidCount > 1` on `prongs` as six individually-identified sub-components; it is the real, current representation and should not be described as though individual prong identities exist anywhere in `GeometryInspectionReport`.

## Tests

`backend/tests/test_geometry_inspection.py::TestComponentExistsInspection` — `test_every_real_component_exists` (all 4 required components report `exists=True` for a real generated model) and `test_a_zero_solid_component_is_reported_missing` (a component whose shape has zero solids is reported `exists=False`, not silently dropped from `componentResults`). `TestAssemblyComponentCount::test_real_solitaire_has_4_components` and `test_required_components_present`.

## Cross-references

- [`464-component-inspection-contract.md`](464-component-inspection-contract.md) — the general per-component inspection contract this document specializes to presence.
- [`465-assembly-inspection-contract.md`](465-assembly-inspection-contract.md) — how `requiredComponentsPresent`/`missingComponentIds` feed `GeometryInspectionReport.status`.
- [`475-prong-count-and-identity-inspection.md`](475-prong-count-and-identity-inspection.md) — the identity half of the same "one compound, not N components" finding.
- [`07-atlas/138-component-naming-and-identity.md`](../07-atlas/138-component-naming-and-identity.md) — the Sprint 5 precursor naming/identity contract.
