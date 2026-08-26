---
id: JM-BIBLE-558
title: Current Code Mapping and Gaps
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-SHANK-README
  - JM-BIBLE-540
related_documents:
  - JM-BIBLE-541
  - JM-BIBLE-526
implementation_status: current
professional_validation: not_required
normative: true
---

# Current Code Mapping and Gaps

## File-by-file map

| File | Role |
|---|---|
| `backend/jewelmind/geometry/shank/profile.py` | Ring-agnostic section-profile builders — `flat_profile_wire()`, `comfort_fit_profile_wire()`, `build_profile()` dispatch. Takes only `inner_r`/`outer_r`/`half_width`; no `JewelryDefinition` knowledge. |
| `backend/jewelmind/geometry/shank/taper.py` | Ring-agnostic taper math — `taper_ratio(u, taper)`, `angle_deg_for_u(u)`. Takes only `u`/`BandTaperSpec`; no `JewelryDefinition` knowledge. |
| `backend/jewelmind/geometry/shank/builder.py` | Ring-aware dispatch and construction — `_build_uniform_shank()`, `_build_tapered_shank()`, `build_shank()`, `ShankConstructionError`, `SECTION_COUNT`. The one module in the package that reads `JewelryDefinition`. |
| `backend/jewelmind/geometry/shank/capability.py` | `SHANK_CAPABILITIES` registry, `get_shank_capability()` — SHANK-GOV-015's single source of truth. |
| `backend/jewelmind/geometry/shank/__init__.py` | Public surface — exposes exactly `build_shank` (`__all__ = ["build_shank"]`). |
| `backend/jewelmind/geometry/connection.py` | `ShankConnectionInterface`, `shank_connection_interface()` — the Shank → RingHead handoff, deliberately placed in the Atlas layer (see [`550-head-connection-interface.md`](550-head-connection-interface.md)). |
| `backend/jewelmind/geometry/components/band.py` | Thin, stable re-export: `from jewelmind.geometry.shank.builder import build_shank as build_ring_band`. Exists so `geometry/assemblies/solitaire.py` and `backend/tests/test_geometry.py` keep importing `build_ring_band` unchanged. |
| `backend/jewelmind/ring/models.py::ShankDefinition` | Data-mapping model only — `profile`/`widthMm`/`thicknessMm`/`widthTaper`/`thicknessTaper`, 1:1 from `JewelryDefinition.band`. No geometry, no CadQuery, no knowledge of `SECTION_COUNT`/loft/revolve. |
| `backend/jewelmind/ring/adapter.py::ring_definition_from_jdl()` | Constructs `ShankDefinition(..., widthTaper=definition.band.widthTaper.model_copy(), thicknessTaper=definition.band.thicknessTaper.model_copy())` — the real, current mapping. |
| `backend/jewelmind/domain/schema.py::BandSpec`/`BandTaperSpec` | The JDL-facing input schema — see [`542-shank-domain-model.md`](542-shank-domain-model.md). |

## Real bug 1: the circular import from misplacing `connection.py`

An earlier version of `geometry/connection.py` was placed inside `jewelmind/ring/` during this Sprint's own implementation. This produced a real, reproducible circular import (`jewelmind.ring.adapter` → `jewelmind.jewelry_category` → `dispatch.py` → `jewelmind.ring.families` → `jewelmind.geometry.assemblies.solitaire` → `geometry/components/basket.py` → back to the Ring-layer connection module) — a genuine Atlas/Ring layering violation (Ring depending on Atlas while an Atlas-layer builder simultaneously depended back on Ring), not merely an import-ordering accident that a different statement order would have papered over. Fixed by relocating the module to `jewelmind/geometry/connection.py`, with no change to `ShankConnectionInterface`'s fields or `shank_connection_interface()`'s computation. Verified from multiple real, independent import orders: `python -c "import jewelmind.ring"`, `python -c "import jewelmind.jewelry_category"`, `python -c "import jewelmind.geometry.components.prongs"` — each succeeding on its own. See [`541-shank-architecture-overview.md`](541-shank-architecture-overview.md) for the full account.

## Real bug 2: Pydantic `StrictModel` has no `validate_assignment=True`

`domain/schema.py::StrictModel` sets `extra="forbid"` and `strict=True`, but not `validate_assignment=True`. This is a real, generally-useful gotcha discovered while writing `backend/tests/test_shank.py::TestInvalidTaper`: mutating an attribute on an already-constructed `JewelryDefinition`/`BandTaperSpec` instance (e.g. `definition.band.widthTaper.bottomRatio = 5.0`) does not trigger Pydantic v2 revalidation and silently succeeds even for a value that would be rejected at construction time (`bottomRatio` requires `gt=0, le=1`). The class docstring for `TestInvalidTaper` in `test_shank.py` records the fix directly: those tests were rewritten to construct a fresh dict (via `default_definition().model_dump(mode="json")`, with `d["band"].update(overrides)`) and call `JewelryDefinition.model_validate()` on it — the real path every JDL input actually goes through — rather than mutating an existing instance, in order to exercise real construction-time rejection. This is worth remembering for any future test in this codebase that wants to prove a `StrictModel` field's validation actually rejects a bad value: mutate-then-assert will not exercise it; construct-then-assert will.

## Real bug 3 (partially resolved): STEP-roundtrip discrepancy at `SECTION_COUNT=72`

During `SECTION_COUNT` tuning, a bounding-box discrepancy of approximately 0.26% between a tapered shank's in-memory geometry and its STEP-roundtripped (export, then re-import) geometry was observed once at `SECTION_COUNT=72` — exceeding the Golden Suite's 1e-3 relative comparison tolerance. It was not reproducible after settling on `SECTION_COUNT=48`: re-tested across 4 different taper configurations with zero discrepancies at that section count. This is reported honestly as **resolved by configuration change, not fully root-caused** — the underlying reason `SECTION_COUNT=72` produced the discrepancy while `48` did not was not identified. Per the guidance this Sprint's work follows, this is flagged as worth re-investigation if `SECTION_COUNT` is ever changed again (any such change is itself a MAJOR change under SHANK-GOV-008, which already requires a Golden re-verification pass that would surface a recurrence).

## What is not a gap: `geometry/components/band.py`'s re-export

Unlike the three items above, the re-export in `geometry/components/band.py` is not a bug — it is a deliberate, documented compatibility shim (see [`556-current-band-migration.md`](556-current-band-migration.md)), included here only to make clear it was checked and found to introduce no behavior change of its own.

## What was deliberately left unchanged

`geometry/constants.py::inner_radius()`, `outer_radius()`, `band_top_z()`, `prong_center_radius()`, and `EMBED_MM` — all pre-Sprint-17 — were not modified by this Sprint; `builder.py` and `connection.py` both call them as-is. `geometry/primitives/selectors.py::FlatCircleAtRadius`, used only by the uniform path's fillet selector, is likewise unchanged and is never reached by `_build_tapered_shank()`. Recording this here is meant to make the code map complete: every file this Sprint touched is listed above, and every closely-related file it did not touch is named here so a future reader does not need to independently verify their absence from the change.

## Test coverage added this Sprint

`backend/tests/test_shank.py` is the primary new test file, covering `taper_ratio()`/`angle_deg_for_u()` behavior directly (including the symmetric-offset parametrized test referenced above under bug 2's `TestInvalidTaper` discussion), plus construction-level tests for both `_build_uniform_shank()` and `_build_tapered_shank()`. `backend/tests/test_shank_schemas.py` validates the 6 schemas and 5 examples under `specs/shank/v1/` and re-derives one example live against the real code to catch pipeline drift, per [`specs/shank/v1/README.md`](../../../specs/shank/v1/README.md#how-these-files-are-validated). `backend/tests/test_ring_architecture_schemas.py` (44/44 passing) covers the `ring/models.py::ShankDefinition` extension and its updated `specs/ring/v2/shank-definition.schema.json` examples.
