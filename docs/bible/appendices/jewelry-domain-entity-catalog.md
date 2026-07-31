---
id: JM-BIBLE-A05
title: "Appendix: Jewelry Domain Entity Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on:
  - JM-BIBLE-044
related_documents:
  - JM-BIBLE-A06
  - JM-BIBLE-A07
implementation_status: current
professional_validation: not_required
---

# Appendix: Jewelry Domain Entity Catalog

Every entity and value object in the current domain model, per
[`04-jewelry-domain/044-solitaire-domain-model.md`](../04-jewelry-domain/044-solitaire-domain-model.md)'s
kind definitions.

| ID | Name | Kind | Definition | Parent aggregate | Current status | Source document | Code mapping |
|---|---|---|---|---|---|---|---|
| JM-ENT-001 | `SolitaireRing` | DOMAIN ENTITY (aggregate root) | The complete solitaire ring definition + its generated state. | — (root) | current | [044](../04-jewelry-domain/044-solitaire-domain-model.md) | `domain/schema.py::JewelryDefinition` + `services/model_service.py::ModelRecord` |
| JM-ENT-002 | `RingIdentity` | DOMAIN ENTITY (conceptual) | The identity of a specific generated model (hash-based). | `SolitaireRing` | current (not a named type) | [044](../04-jewelry-domain/044-solitaire-domain-model.md) | `utils/hashing.py::definition_hash` |
| JM-ENT-003 | `ProjectInfo` | VALUE OBJECT | Project name and unit system label. | `SolitaireRing` | current | [044](../04-jewelry-domain/044-solitaire-domain-model.md) | `domain/schema.py::ProjectInfo` |
| JM-ENT-004 | `JewelryInfo` | VALUE OBJECT | Category and style labels (fixed to ring/solitaire). | `SolitaireRing` | current | [041](../04-jewelry-domain/041-jewelry-product-taxonomy.md), [042](../04-jewelry-domain/042-ring-taxonomy.md) | `domain/schema.py::JewelryInfo` |
| JM-ENT-005 | `RingDimensions` | PARAMETER SET | Ring size system, size, inner diameter. | `SolitaireRing` | current | [044](../04-jewelry-domain/044-solitaire-domain-model.md) | `domain/schema.py::RingSpec` |
| JM-ENT-006 | `Band` | GEOMETRIC COMPONENT | The ring's metal shank solid. | `SolitaireRing` | current | [045](../04-jewelry-domain/045-band-domain.md) | `domain/schema.py::BandSpec`, `geometry/components/band.py` |
| JM-ENT-007 | `CenterStoneReference` | GEOMETRIC COMPONENT | Simplified stone reference solid, kept separate from metal. | `SolitaireRing` | current (reference only) | [046](../04-jewelry-domain/046-stone-domain.md) | `domain/schema.py::StoneSpec`, `geometry/components/stone.py` |
| JM-ENT-008 | `ProngSetting` | GEOMETRIC COMPONENT | The setting mechanism (currently prong-only) as a whole. | `SolitaireRing` | current | [047](../04-jewelry-domain/047-setting-domain.md) | `domain/schema.py::SettingSpec`, `geometry/components/prongs.py` |
| JM-ENT-009 | `Prong` (individual) | GEOMETRIC COMPONENT (sub-part) | One prong cylinder within the prong set. | `ProngSetting` | current | [048](../04-jewelry-domain/048-prong-domain.md) | `geometry/components/prongs.py::build_prongs` (per-solid within the compound) |
| JM-ENT-010 | `BasketSupport` | GEOMETRIC COMPONENT | Structural support connecting setting to band. | `SolitaireRing` | current (simplified) | [049](../04-jewelry-domain/049-basket-and-support-domain.md) | `geometry/components/basket.py` |
| JM-ENT-011 | `MaterialMetadata` | METADATA / VALUE OBJECT | Selected metal, cosmetic/metadata only. | `SolitaireRing` | current | [050](../04-jewelry-domain/050-material-domain.md) | `domain/schema.py::MaterialSpec` |
| JM-ENT-012 | `ManufacturingContext` | MANUFACTURING CONTEXT / VALUE OBJECT | Selected manufacturing method, validation-context only. | `SolitaireRing` | current | [051](../04-jewelry-domain/051-manufacturing-context.md) | `domain/schema.py::ManufacturingSpec` |
| JM-ENT-013 | `PreviewConfiguration` | PARAMETER SET | Mesh tessellation tolerances. | `SolitaireRing` | current | [044](../04-jewelry-domain/044-solitaire-domain-model.md) | `domain/schema.py::PreviewSpec` |
| JM-ENT-014 | `ValidationResult` | VALUE OBJECT | One rule outcome (ID, severity, message, parameter, suggestion). | — (produced by, not contained in, the aggregate) | current | [054](../04-jewelry-domain/054-domain-validation-classification.md) | `validation/rules.py::ValidationResult` |
| JM-ENT-015 | `ValidationResults` (collection) | VALUE OBJECT | The full list of results from one validation run. | — | current | [044](../04-jewelry-domain/044-solitaire-domain-model.md) | `validation/engine.py::validate_definition` (return value) |
| JM-ENT-016 | `GeneratedComponent` | VALUE OBJECT | One named component's shape, volume, bounding box, warnings, metadata. | `GeneratedModel` | current | [044](../04-jewelry-domain/044-solitaire-domain-model.md) | `geometry/model.py::GeneratedComponent` |
| JM-ENT-017 | `BoundingBox` | VALUE OBJECT | Min/max X/Y/Z in millimeters. | `GeneratedComponent` / `GeneratedModel` | current | [043](../04-jewelry-domain/043-ring-anatomy.md) | `geometry/model.py::BoundingBox` |
| JM-ENT-018 | `GeneratedModel` | DOMAIN ENTITY | The full generated assembly: components, combined metal, hash, warnings. | `SolitaireRing` | current | [044](../04-jewelry-domain/044-solitaire-domain-model.md) | `geometry/model.py::GeneratedModel` |
| JM-ENT-019 | `GeneratedArtifacts` (STEP) | GENERATED ARTIFACT | Exported STEP file. | `GeneratedModel` | current | [044](../04-jewelry-domain/044-solitaire-domain-model.md) | `exporters/step_exporter.py` |
| JM-ENT-020 | `GeneratedArtifacts` (STL) | GENERATED ARTIFACT | Exported STL file (also used for preview meshes). | `GeneratedModel` | current | [044](../04-jewelry-domain/044-solitaire-domain-model.md) | `exporters/stl_exporter.py`, `preview/mesh.py` |
| JM-ENT-021 | `GeneratedArtifacts` (JSON) | GENERATED ARTIFACT | Exported canonical definition JSON. | `SolitaireRing` | current | [044](../04-jewelry-domain/044-solitaire-domain-model.md) | `exporters/json_exporter.py` |
| JM-ENT-022 | `GeneratedArtifacts` (Specification) | GENERATED ARTIFACT | Exported Markdown technical specification. | `GeneratedModel` | current | [044](../04-jewelry-domain/044-solitaire-domain-model.md) | `exporters/specification.py` |

## Entities/value objects with no current implementation

Logged for completeness — these are discussed conceptually in
[`043-ring-anatomy.md`](../04-jewelry-domain/043-ring-anatomy.md) but have
no ID above because they have no code mapping at all: `Head` (informal
umbrella term), `Gallery`, `Bridge`, `Shoulders`, `Engraving`, `Internal
relief`. See
[`jewelry-domain-status-matrix.md`](jewelry-domain-status-matrix.md) for
their status.
