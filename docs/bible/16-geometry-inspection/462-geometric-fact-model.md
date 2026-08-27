---
id: JM-BIBLE-462
title: Geometric Fact Model
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
  - JM-BIBLE-461
  - JM-BIBLE-463
  - JM-BIBLE-481
implementation_status: current
professional_validation: not_required
normative: true
---

# Geometric Fact Model

The normative shape is `backend/jewelmind/geometry/inspection/models.py::GeometricFact`, mirrored machine-readably by `specs/geometry-inspection/v2/geometric-fact.schema.json` and cataloged in `specs/geometry-inspection/v2/fact-registry.json`. Every `GeometryInspectionReport.geometricFacts` entry is one of these.

## `GeometricFact` fields

| Field | Type | Notes |
|---|---|---|
| `factId` | `str` | A deterministic, human-readable string, e.g. `component.band.volume`, `pair.band.prongs.minDistance`, `production.connectivity.group.band-basket_support-prongs` — never a random UUID (INSPECT-GOV-010). Built in `inspector.py`. |
| `factType` | `FactType` | One of the 16 values below. |
| `inspectionVersion` | `str` | Always `INSPECTION_VERSION` (`version.py`) at the time the fact was produced — `"1.0.0"` currently. |
| `scope` | `"COMPONENT" \| "ASSEMBLY" \| "PAIR"` | What the fact describes: one component, the whole assembly, or one named pair. |
| `componentIds` | `str[]` | Every component the fact concerns — one name for a `COMPONENT` fact, two for a `PAIR` fact, a full group for an assembly-level connectivity fact. |
| `value` | `float \| int \| bool \| str \| None` | The measurement itself. Kernel-neutral by construction (INSPECT-GOV-016/017) — never a `cadquery.Shape` or OCP object. |
| `unit` | `str \| None` | `"mm"`, `"mm3"`, or `None` for a count/boolean fact. |
| `status` | `InspectionStatus` | `PASS`/`FAIL`/`UNKNOWN`/`NOT_APPLICABLE`/`NOT_IMPLEMENTED`/`ERROR` — whether this specific fact was produced successfully, not a jewelry-domain judgment. |
| `tolerance` | `float \| None` | Set for distance/intersection facts (`CONTACT_TOLERANCE_MM`); `None` for facts with no tolerance concept (e.g. a count). |
| `sourceOperation` | `str` | The real kernel call that produced the value, e.g. `"Shape.distance()"`, `"Shape.intersect()"`, `"Shape.isValid()"`, `"prongs.metadata"` — always traceable to actual code, never invented. |
| `generatedAt` | `str` | ISO timestamp for this fact's construction. |
| `diagnostic` | `InspectionDiagnostic \| None` | Set only when this specific fact's production hit a diagnostic condition. |
| `metadata` | `dict[str, Any]` | Free-form extra structure for facts that need it (e.g. a bounding-box fact embeds the full `BoundingBoxFact.model_dump()` here rather than trying to fit six numbers into `value`). |

`InspectionDiagnostic` itself (`code`, `severity`, `message`, `componentIds`) is documented in full in [`483-inspection-error-model.md`](483-inspection-error-model.md).

## The 22 `FactType` values

Source: `models.py::FactType` and `specs/geometry-inspection/v2/fact-registry.json` (the hand-curated, authoritative catalog — every entry there was written by inspecting the real `inspector.py`/`assembly.py` fact-construction code, not guessed from the type name).

| `FactType` | What it measures |
|---|---|
| `SHAPE_EXISTS` | Whether a component produced at least one solid (`Shape.Solids()`). |
| `SHAPE_VALID` | Whether `Shape.isValid()` (OpenCascade's `BRepCheck_Analyzer`) reports no defects. |
| `SOLID_COUNT` | Number of top-level solids in a shape. |
| `VOLUME` | Solid volume of a component or assembly, in mm³. |
| `BOUNDING_BOX` | Axis-aligned bounding box (min/max/size/center per axis), in mm. |
| `COMPONENT_COUNT` | Number of named components in the assembly. |
| `INTERSECTION_EXISTS` | Whether two components have a real geometric intersection — `INTERSECTS`/`TOUCHES`/`NO_INTERSECTION`/`UNKNOWN`. |
| `INTERSECTION_VOLUME` | Volume of the boolean-common solid between two components, in mm³. |
| `MIN_DISTANCE` | Minimum distance between two components, in mm. |
| `CONNECTED` | A group of production components forming one connected group. |
| `DISCONNECTED` | A group of production components not connected to the rest of the production assembly. |
| `COMPONENT_PRESENT` | Whether a specific required component exists in the model. |
| `PRONG_COUNT` | Requested vs. actually generated prong count. |
| `STONE_METAL_SEPARATE` | Whether the StoneReference solid remains distinct from (never fused into) production metal. |
| `BOOLEAN_RESULT_VALID` | Whether a fuse/cut/common boolean operation produced a real, non-empty result. |
| `FALLBACK_USED` | Whether a geometry builder fell back from its primary operation (e.g. band fillet, metal fuse) to a simpler alternative. |
| `STONE_REQUESTED_LENGTH` | The stone reference's requested major horizontal dimension, from build-time metadata (CONSTRUCTION_PARAMETER). Sprint 18. |
| `STONE_MEASURED_LENGTH` | The stone reference's measured major horizontal extent, from the independently computed bounding box (`sizeY`). Sprint 18. |
| `STONE_REQUESTED_WIDTH` | The stone reference's requested minor horizontal dimension, from build-time metadata (CONSTRUCTION_PARAMETER). Sprint 18. |
| `STONE_MEASURED_WIDTH` | The stone reference's measured minor horizontal extent, from the bounding box (`sizeX`). Sprint 18. |
| `STONE_REQUESTED_DEPTH` | The stone reference's requested vertical dimension, from build-time metadata (CONSTRUCTION_PARAMETER). Sprint 18. |
| `STONE_MEASURED_DEPTH` | The stone reference's measured vertical extent, from the bounding box (`sizeZ`). Sprint 18. |

Not every `FactType` currently has a dedicated flattened entry in `inspector.py::inspect_model()` — `inspector.py` currently emits `COMPONENT_PRESENT`, `SOLID_COUNT`, `VOLUME`, `SHAPE_VALID`, `BOUNDING_BOX` (per component), `COMPONENT_COUNT`, `PRONG_COUNT`, `STONE_METAL_SEPARATE`, `INTERSECTION_VOLUME`, `MIN_DISTANCE` (per pair), and `CONNECTED`/`DISCONNECTED` (per production connectivity group). `SHAPE_EXISTS`, `INTERSECTION_EXISTS`, `BOOLEAN_RESULT_VALID`, and `FALLBACK_USED` are real, defined `FactType` values whose underlying information is present on `ComponentInspectionResult`/`AssemblyInspectionResult`/`BooleanOperationResult` (e.g. `exists`, `IntersectionResult.status`, `BooleanOperationResult.succeeded`/`fallbackUsed`) but are not independently flattened into `geometricFacts` as their own fact entries today — a real, minor gap, not a hidden one; see [`494-current-runtime-inspection-gap-analysis.md`](494-current-runtime-inspection-gap-analysis.md).

The 6 `STONE_*` dimension facts added in Sprint 18 (`inspector.py::_stone_dimension_facts()`) are all genuinely emitted, for the `stone_reference` component only. Their contract — the deliberate CONSTRUCTION_PARAMETER / MEASURED_GEOMETRY pairing, and the honest limitation that an axis-aligned bounding box isolates length from width exactly only at `stone.orientation == 0` — is documented in [`docs/bible/20-stone/574-stone-inspection-contract.md`](../20-stone/574-stone-inspection-contract.md).

## No professional threshold anywhere in this catalog

`fact-registry.json`'s own `notes` field states this explicitly: "No fact type in this registry encodes a professional or manufacturing threshold — every `meaning` describes a geometric measurement or a structural presence/absence check only." `backend/tests/test_geometry_inspection_schemas.py::test_fact_registry_exists_and_has_no_professional_thresholds` enforces this mechanically by asserting the registry's serialized text never contains the strings `"manufacturable"`, `"acceptable tolerance"`, or `"industry standard"`. This is the geometric-fact-model-level restatement of INSPECT-GOV-001/002.

## Forge consumption status

Every one of the 16 facts in `fact-registry.json` currently carries `"forgeConsumptionStatus": "not_consumed"`. This is not an oversight recorded once and forgotten — it is the honest, current state of the Atlas/Forge boundary this Sprint establishes but does not cross. See [`487-forge-fact-contract.md`](487-forge-fact-contract.md).
