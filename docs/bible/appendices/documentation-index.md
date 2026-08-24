---
id: JM-BIBLE-A04
title: "Appendix: Documentation Index"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on: []
related_documents: []
implementation_status: current
---

# Appendix: Documentation Index

Every document in the Technical Bible, plus the pre-existing `docs/`
reference set and the root-level project documents. "Bible" documents
carry a Bible `id`; pre-existing documents do not (they predate the
front-matter convention and are listed here for completeness, per
[`000-bible-governance.md`](../00-foundation/000-bible-governance.md)).

## Technical Bible — `docs/bible/`

| ID | Title | Status | Implementation status | Path |
|---|---|---|---|---|
| JM-BIBLE-README | Technical Bible — Index | accepted | current | [`README.md`](../README.md) |
| JM-BIBLE-000 | Bible Governance | accepted | current | [`00-foundation/000-bible-governance.md`](../00-foundation/000-bible-governance.md) |
| JM-BIBLE-001 | Project Overview | accepted | current | [`00-foundation/001-project-overview.md`](../00-foundation/001-project-overview.md) |
| JM-BIBLE-002 | Vision and Mission | accepted | vision | [`00-foundation/002-vision-and-mission.md`](../00-foundation/002-vision-and-mission.md) |
| JM-BIBLE-003 | Product Principles | accepted | current | [`00-foundation/003-product-principles.md`](../00-foundation/003-product-principles.md) |
| JM-BIBLE-004 | JewelMind Constitution | accepted | current | [`00-foundation/004-jewelmind-constitution.md`](../00-foundation/004-jewelmind-constitution.md) |
| JM-BIBLE-005 | Current Product Status | accepted | current | [`00-foundation/005-current-product-status.md`](../00-foundation/005-current-product-status.md) |
| JM-BIBLE-006 | Scope and Boundaries | accepted | current | [`00-foundation/006-scope-and-boundaries.md`](../00-foundation/006-scope-and-boundaries.md) |
| JM-BIBLE-007 | System Map | accepted | current | [`00-foundation/007-system-map.md`](../00-foundation/007-system-map.md) |
| JM-BIBLE-008 | Glossary | accepted | current | [`00-foundation/008-glossary.md`](../00-foundation/008-glossary.md) |
| JM-BIBLE-010 | User Problems | accepted | current | [`01-product/010-user-problems.md`](../01-product/010-user-problems.md) |
| JM-BIBLE-011 | Target Users | accepted | partial | [`01-product/011-target-users.md`](../01-product/011-target-users.md) |
| JM-BIBLE-012 | Current User Journey | accepted | current | [`01-product/012-current-user-journey.md`](../01-product/012-current-user-journey.md) |
| JM-BIBLE-013 | Functional Requirements | accepted | current | [`01-product/013-functional-requirements.md`](../01-product/013-functional-requirements.md) |
| JM-BIBLE-014 | Non-Functional Requirements | accepted | current | [`01-product/014-non-functional-requirements.md`](../01-product/014-non-functional-requirements.md) |
| JM-BIBLE-015 | Success Metrics | draft | partial | [`01-product/015-success-metrics.md`](../01-product/015-success-metrics.md) |
| JM-BIBLE-020 | Architecture Overview | accepted | current | [`02-architecture/020-architecture-overview.md`](../02-architecture/020-architecture-overview.md) |
| JM-BIBLE-021 | Repository Map | accepted | current | [`02-architecture/021-repository-map.md`](../02-architecture/021-repository-map.md) |
| JM-BIBLE-022 | Domain Boundaries | accepted | current | [`02-architecture/022-domain-boundaries.md`](../02-architecture/022-domain-boundaries.md) |
| JM-BIBLE-023 | Data Flow | accepted | current | [`02-architecture/023-data-flow.md`](../02-architecture/023-data-flow.md) |
| JM-BIBLE-024 | Runtime and Deployment | accepted | current | [`02-architecture/024-runtime-and-deployment.md`](../02-architecture/024-runtime-and-deployment.md) |
| JM-BIBLE-025 | Security and Data Handling | accepted | current | [`02-architecture/025-security-and-data-handling.md`](../02-architecture/025-security-and-data-handling.md) |
| JM-BIBLE-026 | Known Technical Limitations | accepted | current | [`02-architecture/026-known-technical-limitations.md`](../02-architecture/026-known-technical-limitations.md) |
| JM-BIBLE-ADR-INDEX | Architecture Decision Records — Index | accepted | current | [`03-decisions/README.md`](../03-decisions/README.md) |
| JM-BIBLE-ADR-001 | CadQuery for the MVP geometry engine | accepted | current | [`03-decisions/ADR-001-cadquery-for-mvp.md`](../03-decisions/ADR-001-cadquery-for-mvp.md) |
| JM-BIBLE-ADR-002 | No Rhino/commercial CAD runtime dependency | accepted | current | [`03-decisions/ADR-002-no-rhino-runtime-dependency.md`](../03-decisions/ADR-002-no-rhino-runtime-dependency.md) |
| JM-BIBLE-ADR-003 | Deterministic geometry generation | accepted | current | [`03-decisions/ADR-003-deterministic-geometry.md`](../03-decisions/ADR-003-deterministic-geometry.md) |
| JM-BIBLE-ADR-004 | Backend-authoritative validation | accepted | current | [`03-decisions/ADR-004-backend-authoritative-validation.md`](../03-decisions/ADR-004-backend-authoritative-validation.md) |
| JM-BIBLE-ADR-005 | Canonical `JewelryDefinition` schema | accepted | current | [`03-decisions/ADR-005-canonical-jewelry-definition.md`](../03-decisions/ADR-005-canonical-jewelry-definition.md) |
| JM-BIBLE-ADR-006 | Stone reference separated from production metal | accepted | current | [`03-decisions/ADR-006-stone-reference-separated-from-metal.md`](../03-decisions/ADR-006-stone-reference-separated-from-metal.md) |
| JM-BIBLE-ADR-007 | Backend-generated, per-component STL preview (not GLB) | accepted | current | [`03-decisions/ADR-007-backend-generated-preview.md`](../03-decisions/ADR-007-backend-generated-preview.md) |
| JM-BIBLE-ADR-008 | Monorepo architecture | accepted | current | [`03-decisions/ADR-008-monorepo-architecture.md`](../03-decisions/ADR-008-monorepo-architecture.md) |
| JM-BIBLE-ADR-009 | Millimeter-only coordinate/unit system | accepted | current | [`03-decisions/ADR-009-millimeter-coordinate-system.md`](../03-decisions/ADR-009-millimeter-coordinate-system.md) |
| JM-BIBLE-ADR-010 | STEP and STL as the export strategy | accepted | current | [`03-decisions/ADR-010-step-and-stl-export-strategy.md`](../03-decisions/ADR-010-step-and-stl-export-strategy.md) |
| JM-BIBLE-DOMAIN-README | Jewelry Domain Model — Index | accepted | current | [`04-jewelry-domain/README.md`](../04-jewelry-domain/README.md) |
| JM-BIBLE-040 | Domain Governance | accepted | current | [`04-jewelry-domain/040-domain-governance.md`](../04-jewelry-domain/040-domain-governance.md) |
| JM-BIBLE-041 | Jewelry Product Taxonomy | accepted | partial | [`04-jewelry-domain/041-jewelry-product-taxonomy.md`](../04-jewelry-domain/041-jewelry-product-taxonomy.md) |
| JM-BIBLE-042 | Ring Taxonomy | accepted | partial | [`04-jewelry-domain/042-ring-taxonomy.md`](../04-jewelry-domain/042-ring-taxonomy.md) |
| JM-BIBLE-043 | Ring Anatomy | accepted | partial | [`04-jewelry-domain/043-ring-anatomy.md`](../04-jewelry-domain/043-ring-anatomy.md) |
| JM-BIBLE-044 | Solitaire Domain Model | accepted | current | [`04-jewelry-domain/044-solitaire-domain-model.md`](../04-jewelry-domain/044-solitaire-domain-model.md) |
| JM-BIBLE-045 | Band Domain | accepted | current | [`04-jewelry-domain/045-band-domain.md`](../04-jewelry-domain/045-band-domain.md) |
| JM-BIBLE-046 | Stone Domain | accepted | current | [`04-jewelry-domain/046-stone-domain.md`](../04-jewelry-domain/046-stone-domain.md) |
| JM-BIBLE-047 | Setting Domain | accepted | partial | [`04-jewelry-domain/047-setting-domain.md`](../04-jewelry-domain/047-setting-domain.md) |
| JM-BIBLE-048 | Prong Domain | accepted | current | [`04-jewelry-domain/048-prong-domain.md`](../04-jewelry-domain/048-prong-domain.md) |
| JM-BIBLE-049 | Basket and Support Domain | accepted | current | [`04-jewelry-domain/049-basket-and-support-domain.md`](../04-jewelry-domain/049-basket-and-support-domain.md) |
| JM-BIBLE-050 | Material Domain | accepted | current | [`04-jewelry-domain/050-material-domain.md`](../04-jewelry-domain/050-material-domain.md) |
| JM-BIBLE-051 | Manufacturing Context | accepted | current | [`04-jewelry-domain/051-manufacturing-context.md`](../04-jewelry-domain/051-manufacturing-context.md) |
| JM-BIBLE-052 | Parametric Dependency Model | accepted | current | [`04-jewelry-domain/052-parametric-dependency-model.md`](../04-jewelry-domain/052-parametric-dependency-model.md) |
| JM-BIBLE-053 | Domain Invariants | accepted | current | [`04-jewelry-domain/053-domain-invariants.md`](../04-jewelry-domain/053-domain-invariants.md) |
| JM-BIBLE-054 | Domain Validation Classification | accepted | current | [`04-jewelry-domain/054-domain-validation-classification.md`](../04-jewelry-domain/054-domain-validation-classification.md) |
| JM-BIBLE-055 | Domain-to-Code Mapping | accepted | current | [`04-jewelry-domain/055-domain-to-code-mapping.md`](../04-jewelry-domain/055-domain-to-code-mapping.md) |
| JM-BIBLE-056 | Domain Extension Strategy | accepted | current | [`04-jewelry-domain/056-domain-extension-strategy.md`](../04-jewelry-domain/056-domain-extension-strategy.md) |
| JM-BIBLE-057 | Open Domain Questions | accepted | current | [`04-jewelry-domain/057-open-domain-questions.md`](../04-jewelry-domain/057-open-domain-questions.md) |
| JM-BIBLE-058 | Professional Validation Register | accepted | current | [`04-jewelry-domain/058-professional-validation-register.md`](../04-jewelry-domain/058-professional-validation-register.md) |
| JM-BIBLE-SPRINT2-REPORT | Sprint 2 Validation Report | accepted | current | [`04-jewelry-domain/SPRINT-2-VALIDATION-REPORT.md`](../04-jewelry-domain/SPRINT-2-VALIDATION-REPORT.md) |
| JM-BIBLE-A01 | Appendix: Implementation Inventory | accepted | current | [`appendices/implementation-inventory.md`](implementation-inventory.md) |
| JM-BIBLE-A02 | Appendix: Test Inventory | accepted | current | [`appendices/test-inventory.md`](test-inventory.md) |
| JM-BIBLE-A03 | Appendix: API Inventory | accepted | current | [`appendices/api-inventory.md`](api-inventory.md) |
| JM-BIBLE-A04 | Appendix: Documentation Index | accepted | current | [`appendices/documentation-index.md`](documentation-index.md) (this document) |
| JM-BIBLE-A05 | Appendix: Jewelry Domain Entity Catalog | accepted | current | [`appendices/jewelry-domain-entity-catalog.md`](jewelry-domain-entity-catalog.md) |
| JM-BIBLE-A06 | Appendix: Jewelry Domain Parameter Catalog | accepted | current | [`appendices/jewelry-domain-parameter-catalog.md`](jewelry-domain-parameter-catalog.md) |
| JM-BIBLE-A07 | Appendix: Jewelry Domain Relationship Matrix | accepted | current | [`appendices/jewelry-domain-relationship-matrix.md`](jewelry-domain-relationship-matrix.md) |
| JM-BIBLE-A08 | Appendix: Jewelry Domain Status Matrix | accepted | current | [`appendices/jewelry-domain-status-matrix.md`](jewelry-domain-status-matrix.md) |
| JM-BIBLE-JDL-README | Jewelry Definition Language v1 — Index | accepted | partial | [`05-jdl/README.md`](../05-jdl/README.md) |
| JM-BIBLE-060 | JDL Governance | accepted | current | [`05-jdl/060-jdl-governance.md`](../05-jdl/060-jdl-governance.md) |
| JM-BIBLE-061 | JDL Language Overview | accepted | partial | [`05-jdl/061-language-overview.md`](../05-jdl/061-language-overview.md) |
| JM-BIBLE-062 | JDL Design Goals and Non-Goals | accepted | partial | [`05-jdl/062-design-goals-and-non-goals.md`](../05-jdl/062-design-goals-and-non-goals.md) |
| JM-BIBLE-063 | JDL Processing Model | accepted | partial | [`05-jdl/063-jdl-processing-model.md`](../05-jdl/063-jdl-processing-model.md) |
| JM-BIBLE-064 | Canonical Document Model | accepted | current | [`05-jdl/064-canonical-document-model.md`](../05-jdl/064-canonical-document-model.md) |
| JM-BIBLE-065 | Canonical JSON Serialization | accepted | current | [`05-jdl/065-canonical-json-serialization.md`](../05-jdl/065-canonical-json-serialization.md) |
| JM-BIBLE-066 | YAML Serialization Contract | draft | planned | [`05-jdl/066-yaml-serialization-contract.md`](../05-jdl/066-yaml-serialization-contract.md) |
| JM-BIBLE-067 | Textual DSL Overview | draft | planned | [`05-jdl/067-textual-dsl-overview.md`](../05-jdl/067-textual-dsl-overview.md) |
| JM-BIBLE-068 | Lexical Conventions | draft | planned | [`05-jdl/068-lexical-conventions.md`](../05-jdl/068-lexical-conventions.md) |
| JM-BIBLE-069 | Formal Grammar | draft | planned | [`05-jdl/069-formal-grammar.md`](../05-jdl/069-formal-grammar.md) |
| JM-BIBLE-070 | Type System | accepted | partial | [`05-jdl/070-type-system.md`](../05-jdl/070-type-system.md) |
| JM-BIBLE-071 | Units and Numeric Model | accepted | current | [`05-jdl/071-units-and-numeric-model.md`](../05-jdl/071-units-and-numeric-model.md) |
| JM-BIBLE-072 | Identifiers, Enums, and Naming | accepted | current | [`05-jdl/072-identifiers-enums-and-naming.md`](../05-jdl/072-identifiers-enums-and-naming.md) |
| JM-BIBLE-073 | Required, Optional, Default, and Derived Values | accepted | current | [`05-jdl/073-required-optional-default-and-derived-values.md`](../05-jdl/073-required-optional-default-and-derived-values.md) |
| JM-BIBLE-074 | Semantic Rules | accepted | current | [`05-jdl/074-semantic-rules.md`](../05-jdl/074-semantic-rules.md) |
| JM-BIBLE-075 | Validation Pipeline | accepted | partial | [`05-jdl/075-validation-pipeline.md`](../05-jdl/075-validation-pipeline.md) |
| JM-BIBLE-076 | Canonicalization and Definition Hashing | accepted | current | [`05-jdl/076-canonicalization-and-definition-hashing.md`](../05-jdl/076-canonicalization-and-definition-hashing.md) |
| JM-BIBLE-077 | Compiler Contract | accepted | partial | [`05-jdl/077-compiler-contract.md`](../05-jdl/077-compiler-contract.md) |
| JM-BIBLE-078 | Geometry Generation Contract | accepted | current | [`05-jdl/078-geometry-generation-contract.md`](../05-jdl/078-geometry-generation-contract.md) |
| JM-BIBLE-079 | Artifact Generation Contract | accepted | current | [`05-jdl/079-artifact-generation-contract.md`](../05-jdl/079-artifact-generation-contract.md) |
| JM-BIBLE-080 | Errors, Warnings, and Diagnostics | accepted | current | [`05-jdl/080-errors-warnings-and-diagnostics.md`](../05-jdl/080-errors-warnings-and-diagnostics.md) |
| JM-BIBLE-081 | Schema Versioning and Migrations | accepted | current | [`05-jdl/081-schema-versioning-and-migrations.md`](../05-jdl/081-schema-versioning-and-migrations.md) |
| JM-BIBLE-082 | Extension and Capability Model | accepted | planned | [`05-jdl/082-extension-and-capability-model.md`](../05-jdl/082-extension-and-capability-model.md) |
| JM-BIBLE-083 | Security and Resource Limits | accepted | current | [`05-jdl/083-security-and-resource-limits.md`](../05-jdl/083-security-and-resource-limits.md) |
| JM-BIBLE-084 | Current Implementation Mapping | accepted | current | [`05-jdl/084-current-implementation-mapping.md`](../05-jdl/084-current-implementation-mapping.md) |
| JM-BIBLE-085 | Conformance Levels and Test Vectors | accepted | partial | [`05-jdl/085-conformance-and-test-vectors.md`](../05-jdl/085-conformance-and-test-vectors.md) |
| JM-BIBLE-086 | Open JDL Questions | accepted | current | [`05-jdl/086-open-jdl-questions.md`](../05-jdl/086-open-jdl-questions.md) |
| JM-BIBLE-SPRINT3-REPORT | Sprint 3 Validation Report | accepted | current | [`05-jdl/SPRINT-3-VALIDATION-REPORT.md`](../05-jdl/SPRINT-3-VALIDATION-REPORT.md) |
| JM-BIBLE-A09 | Appendix: JDL Field Catalog | accepted | current | [`appendices/jdl-field-catalog.md`](jdl-field-catalog.md) |
| JM-BIBLE-A10 | Appendix: JDL Enumeration Catalog | accepted | current | [`appendices/jdl-enumeration-catalog.md`](jdl-enumeration-catalog.md) |
| JM-BIBLE-A11 | Appendix: JDL Error Code Catalog | accepted | current | [`appendices/jdl-error-code-catalog.md`](jdl-error-code-catalog.md) |
| JM-BIBLE-A12 | Appendix: JDL Version Compatibility Matrix | accepted | current | [`appendices/jdl-version-compatibility-matrix.md`](jdl-version-compatibility-matrix.md) |
| JM-BIBLE-A13 | Appendix: JDL Example Index | accepted | current | [`appendices/jdl-example-index.md`](jdl-example-index.md) |
| JM-BIBLE-FORGE-README | Forge Rule System v1 — Index | accepted | partial | [`06-forge/README.md`](../06-forge/README.md) |
| JM-BIBLE-090 | Forge Governance | accepted | current | [`06-forge/090-forge-governance.md`](../06-forge/090-forge-governance.md) |
| JM-BIBLE-091 | Rule System Overview | accepted | partial | [`06-forge/091-rule-system-overview.md`](../06-forge/091-rule-system-overview.md) |
| JM-BIBLE-092 | Rule Anatomy | accepted | partial | [`06-forge/092-rule-anatomy.md`](../06-forge/092-rule-anatomy.md) |
| JM-BIBLE-093 | Rule Classification Model | accepted | current | [`06-forge/093-rule-classification-model.md`](../06-forge/093-rule-classification-model.md) |
| JM-BIBLE-094 | Rule Provenance Model | accepted | current | [`06-forge/094-rule-provenance-model.md`](../06-forge/094-rule-provenance-model.md) |
| JM-BIBLE-095 | Rule Lifecycle | accepted | current | [`06-forge/095-rule-lifecycle.md`](../06-forge/095-rule-lifecycle.md) |
| JM-BIBLE-096 | Rule Evaluation Pipeline | accepted | partial | [`06-forge/096-rule-evaluation-pipeline.md`](../06-forge/096-rule-evaluation-pipeline.md) |
| JM-BIBLE-097 | Rule Context Model | accepted | partial | [`06-forge/097-rule-context-model.md`](../06-forge/097-rule-context-model.md) |
| JM-BIBLE-098 | Rule Result and Diagnostics | accepted | partial | [`06-forge/098-rule-result-and-diagnostics.md`](../06-forge/098-rule-result-and-diagnostics.md) |
| JM-BIBLE-099 | Severity and Blocking Semantics | accepted | partial | [`06-forge/099-severity-and-blocking-semantics.md`](../06-forge/099-severity-and-blocking-semantics.md) |
| JM-BIBLE-100 | Rule Dependencies and Ordering | accepted | current | [`06-forge/100-rule-dependencies-and-ordering.md`](../06-forge/100-rule-dependencies-and-ordering.md) |
| JM-BIBLE-101 | Conflicts, Precedence, and Resolution | accepted | planned | [`06-forge/101-conflicts-precedence-and-resolution.md`](../06-forge/101-conflicts-precedence-and-resolution.md) |
| JM-BIBLE-102 | Suggestions and Auto-Fix Contract | accepted | partial | [`06-forge/102-suggestions-and-auto-fix-contract.md`](../06-forge/102-suggestions-and-auto-fix-contract.md) |
| JM-BIBLE-103 | Professional Validation Lifecycle | accepted | planned | [`06-forge/103-professional-validation-lifecycle.md`](../06-forge/103-professional-validation-lifecycle.md) |
| JM-BIBLE-104 | Manufacturing Profile Rules | accepted | partial | [`06-forge/104-manufacturing-profile-rules.md`](../06-forge/104-manufacturing-profile-rules.md) |
| JM-BIBLE-105 | Geometry Precondition Rules | accepted | current | [`06-forge/105-geometry-precondition-rules.md`](../06-forge/105-geometry-precondition-rules.md) |
| JM-BIBLE-106 | Generated Geometry Inspection Rules | accepted | partial | [`06-forge/106-generated-geometry-inspection-rules.md`](../06-forge/106-generated-geometry-inspection-rules.md) |
| JM-BIBLE-107 | Export Precondition Rules | accepted | current | [`06-forge/107-export-precondition-rules.md`](../06-forge/107-export-precondition-rules.md) |
| JM-BIBLE-108 | Rule Versioning | accepted | current | [`06-forge/108-rule-versioning.md`](../06-forge/108-rule-versioning.md) |
| JM-BIBLE-109 | Rule Registry | accepted | current | [`06-forge/109-rule-registry.md`](../06-forge/109-rule-registry.md) |
| JM-BIBLE-110 | Current Rule Inventory | accepted | current | [`06-forge/110-current-rule-inventory.md`](../06-forge/110-current-rule-inventory.md) |
| JM-BIBLE-111 | Domain Rule Gap Analysis | accepted | current | [`06-forge/111-domain-rule-gap-analysis.md`](../06-forge/111-domain-rule-gap-analysis.md) |
| JM-BIBLE-112 | Rule Testing Strategy | accepted | partial | [`06-forge/112-rule-testing-strategy.md`](../06-forge/112-rule-testing-strategy.md) |
| JM-BIBLE-113 | Forge API Contract | accepted | partial | [`06-forge/113-forge-api-contract.md`](../06-forge/113-forge-api-contract.md) |
| JM-BIBLE-114 | Future AI-Assisted Rule Discovery | draft | vision | [`06-forge/114-future-ai-assisted-rule-discovery.md`](../06-forge/114-future-ai-assisted-rule-discovery.md) |
| JM-BIBLE-115 | Open Forge Questions | accepted | current | [`06-forge/115-open-forge-questions.md`](../06-forge/115-open-forge-questions.md) |
| JM-BIBLE-SPRINT4-REPORT | Sprint 4 Validation Report | accepted | current | [`06-forge/SPRINT-4-VALIDATION-REPORT.md`](../06-forge/SPRINT-4-VALIDATION-REPORT.md) |
| JM-BIBLE-A14 | Appendix: Forge Rule Catalog | accepted | current | [`appendices/forge-rule-catalog.md`](forge-rule-catalog.md) |
| JM-BIBLE-A15 | Appendix: Forge Rule Provenance Register | accepted | current | [`appendices/forge-rule-provenance-register.md`](forge-rule-provenance-register.md) |
| JM-BIBLE-A16 | Appendix: Forge Severity Matrix | accepted | current | [`appendices/forge-severity-matrix.md`](forge-severity-matrix.md) |
| JM-BIBLE-A17 | Appendix: Forge Professional Validation Matrix | accepted | current | [`appendices/forge-professional-validation-matrix.md`](forge-professional-validation-matrix.md) |
| JM-BIBLE-A18 | Appendix: Forge Rule Dependency Matrix | accepted | current | [`appendices/forge-rule-dependency-matrix.md`](forge-rule-dependency-matrix.md) |
| JM-BIBLE-A19 | Appendix: Forge Rule Test Matrix | accepted | current | [`appendices/forge-rule-test-matrix.md`](forge-rule-test-matrix.md) |
| JM-BIBLE-ATLAS-README | Atlas Geometry Core v1 — Index | accepted | partial | [`07-atlas/README.md`](../07-atlas/README.md) |
| JM-BIBLE-120 | Atlas Governance | accepted | current | [`07-atlas/120-atlas-governance.md`](../07-atlas/120-atlas-governance.md) |
| JM-BIBLE-121 | Atlas Architecture Overview | accepted | partial | [`07-atlas/121-atlas-architecture-overview.md`](../07-atlas/121-atlas-architecture-overview.md) |
| JM-BIBLE-122 | Geometric Representation Model | accepted | current | [`07-atlas/122-geometric-representation-model.md`](../07-atlas/122-geometric-representation-model.md) |
| JM-BIBLE-123 | Coordinate System and Orientation | accepted | current | [`07-atlas/123-coordinate-system-and-orientation.md`](../07-atlas/123-coordinate-system-and-orientation.md) |
| JM-BIBLE-124 | Geometric Primitives | accepted | current | [`07-atlas/124-geometric-primitives.md`](../07-atlas/124-geometric-primitives.md) |
| JM-BIBLE-125 | Transformations | accepted | current | [`07-atlas/125-transformations.md`](../07-atlas/125-transformations.md) |
| JM-BIBLE-126 | Curve and Profile Model | accepted | current | [`07-atlas/126-curve-and-profile-model.md`](../07-atlas/126-curve-and-profile-model.md) |
| JM-BIBLE-127 | Surface and Solid Model | accepted | current | [`07-atlas/127-surface-and-solid-model.md`](../07-atlas/127-surface-and-solid-model.md) |
| JM-BIBLE-128 | B-Rep and Topology Model | accepted | partial | [`07-atlas/128-brep-and-topology-model.md`](../07-atlas/128-brep-and-topology-model.md) |
| JM-BIBLE-129 | Mesh Model | accepted | current | [`07-atlas/129-mesh-model.md`](../07-atlas/129-mesh-model.md) |
| JM-BIBLE-130 | Component Contract | accepted | partial | [`07-atlas/130-component-contract.md`](../07-atlas/130-component-contract.md) |
| JM-BIBLE-131 | Assembly Contract | accepted | current | [`07-atlas/131-assembly-contract.md`](../07-atlas/131-assembly-contract.md) |
| JM-BIBLE-132 | Construction Pipeline | accepted | partial | [`07-atlas/132-construction-pipeline.md`](../07-atlas/132-construction-pipeline.md) |
| JM-BIBLE-133 | Operation Contracts | accepted | current | [`07-atlas/133-operation-contracts.md`](../07-atlas/133-operation-contracts.md) |
| JM-BIBLE-134 | Boolean Operation Strategy | accepted | current | [`07-atlas/134-boolean-operation-strategy.md`](../07-atlas/134-boolean-operation-strategy.md) |
| JM-BIBLE-135 | Fillets, Rounding, and Fallbacks | accepted | current | [`07-atlas/135-fillets-rounding-and-fallbacks.md`](../07-atlas/135-fillets-rounding-and-fallbacks.md) |
| JM-BIBLE-136 | Tolerance Model | accepted | current | [`07-atlas/136-tolerance-model.md`](../07-atlas/136-tolerance-model.md) |
| JM-BIBLE-137 | Determinism and Reproducibility | accepted | current | [`07-atlas/137-determinism-and-reproducibility.md`](../07-atlas/137-determinism-and-reproducibility.md) |
| JM-BIBLE-138 | Component Naming and Identity | accepted | current | [`07-atlas/138-component-naming-and-identity.md`](../07-atlas/138-component-naming-and-identity.md) |
| JM-BIBLE-139 | Geometry Metadata Model | accepted | current | [`07-atlas/139-geometry-metadata-model.md`](../07-atlas/139-geometry-metadata-model.md) |
| JM-BIBLE-140 | Geometry Inspection Framework | accepted | partial | [`07-atlas/140-geometry-inspection-framework.md`](../07-atlas/140-geometry-inspection-framework.md) |
| JM-BIBLE-141 | Connectivity and Component Integrity | accepted | partial | [`07-atlas/141-connectivity-and-component-integrity.md`](../07-atlas/141-connectivity-and-component-integrity.md) |
| JM-BIBLE-142 | Volume and Bounding Box Inspection | accepted | current | [`07-atlas/142-volume-and-bounding-box-inspection.md`](../07-atlas/142-volume-and-bounding-box-inspection.md) |
| JM-BIBLE-143 | Stone-Metal Separation Contract | accepted | current | [`07-atlas/143-stone-metal-separation-contract.md`](../07-atlas/143-stone-metal-separation-contract.md) |
| JM-BIBLE-144 | Preview Mesh Contract | accepted | current | [`07-atlas/144-preview-mesh-contract.md`](../07-atlas/144-preview-mesh-contract.md) |
| JM-BIBLE-145 | STEP Export Geometry Contract | accepted | current | [`07-atlas/145-step-export-geometry-contract.md`](../07-atlas/145-step-export-geometry-contract.md) |
| JM-BIBLE-146 | STL Export Geometry Contract | accepted | current | [`07-atlas/146-stl-export-geometry-contract.md`](../07-atlas/146-stl-export-geometry-contract.md) |
| JM-BIBLE-147 | Geometry Error Model | accepted | partial | [`07-atlas/147-geometry-error-model.md`](../07-atlas/147-geometry-error-model.md) |
| JM-BIBLE-148 | Performance and Resource Model | accepted | partial | [`07-atlas/148-performance-and-resource-model.md`](../07-atlas/148-performance-and-resource-model.md) |
| JM-BIBLE-149 | Current Solitaire Geometry Mapping | accepted | current | [`07-atlas/149-current-solitaire-geometry-mapping.md`](../07-atlas/149-current-solitaire-geometry-mapping.md) |
| JM-BIBLE-150 | Atlas Gap Analysis | accepted | current | [`07-atlas/150-atlas-gap-analysis.md`](../07-atlas/150-atlas-gap-analysis.md) |
| JM-BIBLE-151 | Open Atlas Questions | accepted | current | [`07-atlas/151-open-atlas-questions.md`](../07-atlas/151-open-atlas-questions.md) |
| JM-BIBLE-SPRINT5-REPORT | Sprint 5 Validation Report | accepted | current | [`07-atlas/SPRINT-5-VALIDATION-REPORT.md`](../07-atlas/SPRINT-5-VALIDATION-REPORT.md) |
| JM-BIBLE-A20 | Appendix: Atlas Component Catalog | accepted | current | [`appendices/atlas-component-catalog.md`](atlas-component-catalog.md) |
| JM-BIBLE-A21 | Appendix: Atlas Operation Catalog | accepted | current | [`appendices/atlas-operation-catalog.md`](atlas-operation-catalog.md) |
| JM-BIBLE-A22 | Appendix: Atlas Coordinate Reference | accepted | current | [`appendices/atlas-coordinate-reference.md`](atlas-coordinate-reference.md) |
| JM-BIBLE-A23 | Appendix: Atlas Geometry Invariant Catalog | accepted | current | [`appendices/atlas-geometry-invariant-catalog.md`](atlas-geometry-invariant-catalog.md) |
| JM-BIBLE-A24 | Appendix: Atlas Inspection Catalog | accepted | current | [`appendices/atlas-inspection-catalog.md`](atlas-inspection-catalog.md) |
| JM-BIBLE-A25 | Appendix: Atlas Fallback Register | accepted | current | [`appendices/atlas-fallback-register.md`](atlas-fallback-register.md) |
| JM-BIBLE-A26 | Appendix: Atlas Code Mapping | accepted | current | [`appendices/atlas-code-mapping.md`](atlas-code-mapping.md) |
| JM-BIBLE-ALCHEMIST-README | Alchemist Compiler v1 — Index | accepted | partial | [`08-alchemist/README.md`](../08-alchemist/README.md) |
| JM-BIBLE-160 | Alchemist Governance | accepted | current | [`08-alchemist/160-alchemist-governance.md`](../08-alchemist/160-alchemist-governance.md) |
| JM-BIBLE-161 | Compiler Architecture Overview | accepted | partial | [`08-alchemist/161-compiler-architecture-overview.md`](../08-alchemist/161-compiler-architecture-overview.md) |
| JM-BIBLE-162 | Compiler Boundaries | accepted | current | [`08-alchemist/162-compiler-boundaries.md`](../08-alchemist/162-compiler-boundaries.md) |
| JM-BIBLE-163 | Compilation Input Contract | accepted | partial | [`08-alchemist/163-compilation-input-contract.md`](../08-alchemist/163-compilation-input-contract.md) |
| JM-BIBLE-164 | Normalization Stage | accepted | current | [`08-alchemist/164-normalization-stage.md`](../08-alchemist/164-normalization-stage.md) |
| JM-BIBLE-165 | Forge Evaluation Integration | accepted | partial | [`08-alchemist/165-forge-evaluation-integration.md`](../08-alchemist/165-forge-evaluation-integration.md) |
| JM-BIBLE-166 | Geometry Plan Model | accepted | planned | [`08-alchemist/166-geometry-plan-model.md`](../08-alchemist/166-geometry-plan-model.md) |
| JM-BIBLE-167 | Geometry Plan Generation | accepted | planned | [`08-alchemist/167-geometry-plan-generation.md`](../08-alchemist/167-geometry-plan-generation.md) |
| JM-BIBLE-168 | Atlas Execution Contract | accepted | partial | [`08-alchemist/168-atlas-execution-contract.md`](../08-alchemist/168-atlas-execution-contract.md) |
| JM-BIBLE-169 | Component Build Order | accepted | current | [`08-alchemist/169-component-build-order.md`](../08-alchemist/169-component-build-order.md) |
| JM-BIBLE-170 | Compilation State Machine | accepted | planned | [`08-alchemist/170-compilation-state-machine.md`](../08-alchemist/170-compilation-state-machine.md) |
| JM-BIBLE-171 | Compilation Result Model | accepted | partial | [`08-alchemist/171-compilation-result-model.md`](../08-alchemist/171-compilation-result-model.md) |
| JM-BIBLE-172 | Diagnostics and Failure Propagation | accepted | current | [`08-alchemist/172-diagnostics-and-failure-propagation.md`](../08-alchemist/172-diagnostics-and-failure-propagation.md) |
| JM-BIBLE-173 | Partial Compilation Policy | accepted | partial | [`08-alchemist/173-partial-compilation-policy.md`](../08-alchemist/173-partial-compilation-policy.md) |
| JM-BIBLE-174 | Determinism and Version Fingerprint | accepted | partial | [`08-alchemist/174-determinism-and-version-fingerprint.md`](../08-alchemist/174-determinism-and-version-fingerprint.md) |
| JM-BIBLE-175 | Definition Hash vs. Compilation Hash | accepted | planned | [`08-alchemist/175-definition-hash-vs-compilation-hash.md`](../08-alchemist/175-definition-hash-vs-compilation-hash.md) |
| JM-BIBLE-176 | Compilation Cache Model | accepted | current | [`08-alchemist/176-compilation-cache-model.md`](../08-alchemist/176-compilation-cache-model.md) |
| JM-BIBLE-177 | Artifact Request Model | accepted | partial | [`08-alchemist/177-artifact-request-model.md`](../08-alchemist/177-artifact-request-model.md) |
| JM-BIBLE-178 | Artifact Manifest Contract | accepted | partial | [`08-alchemist/178-artifact-manifest-contract.md`](../08-alchemist/178-artifact-manifest-contract.md) |
| JM-BIBLE-179 | Preview Generation Integration | accepted | current | [`08-alchemist/179-preview-generation-integration.md`](../08-alchemist/179-preview-generation-integration.md) |
| JM-BIBLE-180 | Export Generation Integration | accepted | current | [`08-alchemist/180-export-generation-integration.md`](../08-alchemist/180-export-generation-integration.md) |
| JM-BIBLE-181 | Compiler Capability Model | accepted | planned | [`08-alchemist/181-compiler-capability-model.md`](../08-alchemist/181-compiler-capability-model.md) |
| JM-BIBLE-182 | Compiler Versioning | accepted | planned | [`08-alchemist/182-compiler-versioning.md`](../08-alchemist/182-compiler-versioning.md) |
| JM-BIBLE-183 | Current Backend to Compiler Mapping | accepted | current | [`08-alchemist/183-current-backend-to-compiler-mapping.md`](../08-alchemist/183-current-backend-to-compiler-mapping.md) |
| JM-BIBLE-184 | Compiler Observability | accepted | planned | [`08-alchemist/184-compiler-observability.md`](../08-alchemist/184-compiler-observability.md) |
| JM-BIBLE-185 | Compiler Performance Model | accepted | partial | [`08-alchemist/185-compiler-performance-model.md`](../08-alchemist/185-compiler-performance-model.md) |
| JM-BIBLE-186 | Compiler Security and Resource Limits | accepted | current | [`08-alchemist/186-compiler-security-and-resource-limits.md`](../08-alchemist/186-compiler-security-and-resource-limits.md) |
| JM-BIBLE-187 | Alchemist Gap Analysis | accepted | current | [`08-alchemist/187-alchemist-gap-analysis.md`](../08-alchemist/187-alchemist-gap-analysis.md) |
| JM-BIBLE-188 | Open Alchemist Questions | accepted | current | [`08-alchemist/188-open-alchemist-questions.md`](../08-alchemist/188-open-alchemist-questions.md) |
| JM-BIBLE-SPRINT6-REPORT | Sprint 6 Validation Report | accepted | current | [`08-alchemist/SPRINT-6-VALIDATION-REPORT.md`](../08-alchemist/SPRINT-6-VALIDATION-REPORT.md) |
| JM-BIBLE-A27 | Appendix: Alchemist Stage Catalog | accepted | partial | [`appendices/alchemist-stage-catalog.md`](alchemist-stage-catalog.md) |
| JM-BIBLE-A28 | Appendix: Alchemist State Transition Matrix | accepted | planned | [`appendices/alchemist-state-transition-matrix.md`](alchemist-state-transition-matrix.md) |
| JM-BIBLE-A29 | Appendix: Geometry Plan Field Catalog | accepted | planned | [`appendices/geometry-plan-field-catalog.md`](geometry-plan-field-catalog.md) |
| JM-BIBLE-A30 | Appendix: Compilation Result Field Catalog | accepted | partial | [`appendices/compilation-result-field-catalog.md`](compilation-result-field-catalog.md) |
| JM-BIBLE-A31 | Appendix: Compiler Diagnostic Catalog | accepted | current | [`appendices/compiler-diagnostic-catalog.md`](compiler-diagnostic-catalog.md) |
| JM-BIBLE-A32 | Appendix: Compiler Code Mapping | accepted | current | [`appendices/compiler-code-mapping.md`](compiler-code-mapping.md) |
| JM-BIBLE-A33 | Appendix: Compiler Test Matrix | accepted | current | [`appendices/compiler-test-matrix.md`](compiler-test-matrix.md) |
| JM-BIBLE-FOUNDRY-README | Foundry Export System v1 — Index | accepted | current | [`09-foundry/README.md`](../09-foundry/README.md) |
| JM-BIBLE-190 | Foundry Governance | accepted | current | [`09-foundry/190-foundry-governance.md`](../09-foundry/190-foundry-governance.md) |
| JM-BIBLE-191 | Foundry Architecture Overview | accepted | partial | [`09-foundry/191-foundry-architecture-overview.md`](../09-foundry/191-foundry-architecture-overview.md) |
| JM-BIBLE-192 | Artifact Domain Model | accepted | partial | [`09-foundry/192-artifact-domain-model.md`](../09-foundry/192-artifact-domain-model.md) |
| JM-BIBLE-193 | Artifact Request Contract | accepted | partial | [`09-foundry/193-artifact-request-contract.md`](../09-foundry/193-artifact-request-contract.md) |
| JM-BIBLE-194 | Artifact Generation Pipeline (FOUNDRY-0..FOUNDRY-9) | accepted | partial | [`09-foundry/194-generation-pipeline.md`](../09-foundry/194-generation-pipeline.md) |
| JM-BIBLE-195 | Component Inclusion Policy | accepted | current | [`09-foundry/195-component-inclusion-policy.md`](../09-foundry/195-component-inclusion-policy.md) |
| JM-BIBLE-196 | Production Geometry Selection | accepted | current | [`09-foundry/196-production-geometry-selection.md`](../09-foundry/196-production-geometry-selection.md) |
| JM-BIBLE-197 | STEP Export Contract | accepted | current | [`09-foundry/197-step-export-contract.md`](../09-foundry/197-step-export-contract.md) |
| JM-BIBLE-198 | STL Export Contract | accepted | current | [`09-foundry/198-stl-export-contract.md`](../09-foundry/198-stl-export-contract.md) |
| JM-BIBLE-199 | JSON Export Contract | accepted | current | [`09-foundry/199-json-export-contract.md`](../09-foundry/199-json-export-contract.md) |
| JM-BIBLE-200 | Technical Specification Contract | accepted | current | [`09-foundry/200-technical-specification-contract.md`](../09-foundry/200-technical-specification-contract.md) |
| JM-BIBLE-201 | Artifact Manifest Model | accepted | planned | [`09-foundry/201-artifact-manifest-model.md`](../09-foundry/201-artifact-manifest-model.md) |
| JM-BIBLE-202 | Artifact Integrity Model | accepted | partial | [`09-foundry/202-artifact-integrity-model.md`](../09-foundry/202-artifact-integrity-model.md) |
| JM-BIBLE-203 | Export Validation Pipeline | accepted | partial | [`09-foundry/203-export-validation-pipeline.md`](../09-foundry/203-export-validation-pipeline.md) |
| JM-BIBLE-204 | Export Diagnostics | accepted | partial | [`09-foundry/204-export-diagnostics.md`](../09-foundry/204-export-diagnostics.md) |
| JM-BIBLE-205 | Export Failure and Partial Success | accepted | planned | [`09-foundry/205-export-failure-and-partial-success.md`](../09-foundry/205-export-failure-and-partial-success.md) |
| JM-BIBLE-206 | Filename and Path Safety | accepted | current | [`09-foundry/206-filename-and-path-safety.md`](../09-foundry/206-filename-and-path-safety.md) |
| JM-BIBLE-207 | Temp-File Lifecycle | accepted | current | [`09-foundry/207-temp-file-lifecycle.md`](../09-foundry/207-temp-file-lifecycle.md) |
| JM-BIBLE-208 | Export Version Fingerprint | accepted | planned | [`09-foundry/208-export-version-fingerprint.md`](../09-foundry/208-export-version-fingerprint.md) |
| JM-BIBLE-209 | CAD Interoperability Philosophy | accepted | current | [`09-foundry/209-cad-interoperability-philosophy.md`](../09-foundry/209-cad-interoperability-philosophy.md) |
| JM-BIBLE-210 | STEP Interoperability Boundaries | accepted | current | [`09-foundry/210-step-interoperability-boundaries.md`](../09-foundry/210-step-interoperability-boundaries.md) |
| JM-BIBLE-211 | STL Interoperability Boundaries | accepted | current | [`09-foundry/211-stl-interoperability-boundaries.md`](../09-foundry/211-stl-interoperability-boundaries.md) |
| JM-BIBLE-212 | Unit and Scale Contract | accepted | current | [`09-foundry/212-unit-and-scale-contract.md`](../09-foundry/212-unit-and-scale-contract.md) |
| JM-BIBLE-213 | Multi-Solid and Fusion Policy | accepted | current | [`09-foundry/213-multi-solid-and-fusion-policy.md`](../09-foundry/213-multi-solid-and-fusion-policy.md) |
| JM-BIBLE-214 | Export Roundtrip Validation | accepted | current | [`09-foundry/214-export-roundtrip-validation.md`](../09-foundry/214-export-roundtrip-validation.md) |
| JM-BIBLE-215 | Foundry Performance Model | accepted | current | [`09-foundry/215-foundry-performance-model.md`](../09-foundry/215-foundry-performance-model.md) |
| JM-BIBLE-216 | Foundry Security and Resource Limits | accepted | current | [`09-foundry/216-foundry-security-and-resource-limits.md`](../09-foundry/216-foundry-security-and-resource-limits.md) |
| JM-BIBLE-217 | Current Exporter Code Mapping | accepted | current | [`09-foundry/217-current-exporter-code-mapping.md`](../09-foundry/217-current-exporter-code-mapping.md) |
| JM-BIBLE-218 | Foundry Gap Analysis | accepted | current | [`09-foundry/218-foundry-gap-analysis.md`](../09-foundry/218-foundry-gap-analysis.md) |
| JM-BIBLE-219 | Open Foundry Questions | accepted | current | [`09-foundry/219-open-foundry-questions.md`](../09-foundry/219-open-foundry-questions.md) |
| JM-BIBLE-SPRINT7-REPORT | Sprint 7 Validation Report | accepted | current | [`09-foundry/SPRINT-7-VALIDATION-REPORT.md`](../09-foundry/SPRINT-7-VALIDATION-REPORT.md) |
| JM-BIBLE-A34 | Appendix: Foundry Artifact Catalog | accepted | current | [`appendices/foundry-artifact-catalog.md`](foundry-artifact-catalog.md) |
| JM-BIBLE-A35 | Appendix: Foundry MIME Type Catalog | accepted | current | [`appendices/foundry-mime-type-catalog.md`](foundry-mime-type-catalog.md) |
| JM-BIBLE-A36 | Appendix: Foundry Component Inclusion Matrix | accepted | current | [`appendices/foundry-component-inclusion-matrix.md`](foundry-component-inclusion-matrix.md) |
| JM-BIBLE-A37 | Appendix: Foundry Export Diagnostic Catalog | accepted | partial | [`appendices/foundry-export-diagnostic-catalog.md`](foundry-export-diagnostic-catalog.md) |
| JM-BIBLE-A38 | Appendix: Foundry Export Test Matrix | accepted | current | [`appendices/foundry-export-test-matrix.md`](foundry-export-test-matrix.md) |
| JM-BIBLE-A39 | Appendix: Foundry Code Mapping | accepted | current | [`appendices/foundry-code-mapping.md`](foundry-code-mapping.md) |
| JM-BIBLE-A40 | Appendix: Foundry Interoperability Matrix | accepted | current | [`appendices/foundry-interoperability-matrix.md`](foundry-interoperability-matrix.md) |

## Machine-readable Foundry specification — `specs/foundry/v1/`

| File | Normative? | Path |
|---|---|---|
| Overview | — | [`specs/foundry/v1/README.md`](../../../specs/foundry/v1/README.md) |
| Artifact request schema | Yes | [`specs/foundry/v1/artifact-request.schema.json`](../../../specs/foundry/v1/artifact-request.schema.json) |
| Artifact record schema | Yes | [`specs/foundry/v1/artifact-record.schema.json`](../../../specs/foundry/v1/artifact-record.schema.json) |
| Artifact manifest schema | Yes | [`specs/foundry/v1/artifact-manifest.schema.json`](../../../specs/foundry/v1/artifact-manifest.schema.json) |
| Export diagnostic schema | Yes | [`specs/foundry/v1/export-diagnostic.schema.json`](../../../specs/foundry/v1/export-diagnostic.schema.json) |
| Export validation result schema | Yes | [`specs/foundry/v1/export-validation-result.schema.json`](../../../specs/foundry/v1/export-validation-result.schema.json) |
| Export version fingerprint schema | Yes | [`specs/foundry/v1/export-version-fingerprint.schema.json`](../../../specs/foundry/v1/export-version-fingerprint.schema.json) |
| Examples (real, generated) | Yes | [`specs/foundry/v1/examples/`](../../../specs/foundry/v1/examples/) |
| Test vectors | Yes | [`specs/foundry/v1/test-vectors/`](../../../specs/foundry/v1/test-vectors/) |

## Machine-readable Alchemist specification — `specs/alchemist/v1/`

| File | Normative? | Path |
|---|---|---|
| Overview | — | [`specs/alchemist/v1/README.md`](../../../specs/alchemist/v1/README.md) |
| Compilation input schema | Yes | [`specs/alchemist/v1/compilation-input.schema.json`](../../../specs/alchemist/v1/compilation-input.schema.json) |
| Geometry plan schema | Yes | [`specs/alchemist/v1/geometry-plan.schema.json`](../../../specs/alchemist/v1/geometry-plan.schema.json) |
| Geometry plan component schema | Yes | [`specs/alchemist/v1/geometry-plan-component.schema.json`](../../../specs/alchemist/v1/geometry-plan-component.schema.json) |
| Compilation result schema | Yes | [`specs/alchemist/v1/compilation-result.schema.json`](../../../specs/alchemist/v1/compilation-result.schema.json) |
| Compiler diagnostic schema | Yes | [`specs/alchemist/v1/compiler-diagnostic.schema.json`](../../../specs/alchemist/v1/compiler-diagnostic.schema.json) |
| Artifact request schema | Yes | [`specs/alchemist/v1/artifact-request.schema.json`](../../../specs/alchemist/v1/artifact-request.schema.json) |
| Artifact manifest schema | Yes | [`specs/alchemist/v1/artifact-manifest.schema.json`](../../../specs/alchemist/v1/artifact-manifest.schema.json) |
| Compiler capabilities schema | Yes | [`specs/alchemist/v1/compiler-capabilities.schema.json`](../../../specs/alchemist/v1/compiler-capabilities.schema.json) |
| Examples (real, generated) | Yes | [`specs/alchemist/v1/examples/`](../../../specs/alchemist/v1/examples/) |
| Test vectors | Yes | [`specs/alchemist/v1/test-vectors/`](../../../specs/alchemist/v1/test-vectors/) |

## Machine-readable Atlas specification — `specs/atlas/v1/`

| File | Normative? | Path |
|---|---|---|
| Overview | — | [`specs/atlas/v1/README.md`](../../../specs/atlas/v1/README.md) |
| Component schema | Yes | [`specs/atlas/v1/geometry-component.schema.json`](../../../specs/atlas/v1/geometry-component.schema.json) |
| Assembly schema | Yes | [`specs/atlas/v1/geometry-assembly.schema.json`](../../../specs/atlas/v1/geometry-assembly.schema.json) |
| Metadata schema | Yes | [`specs/atlas/v1/geometry-metadata.schema.json`](../../../specs/atlas/v1/geometry-metadata.schema.json) |
| Inspection-result schema | Yes | [`specs/atlas/v1/geometry-inspection-result.schema.json`](../../../specs/atlas/v1/geometry-inspection-result.schema.json) |
| Error schema | Yes | [`specs/atlas/v1/geometry-error.schema.json`](../../../specs/atlas/v1/geometry-error.schema.json) |
| Component-manifest schema | Yes | [`specs/atlas/v1/component-manifest.schema.json`](../../../specs/atlas/v1/component-manifest.schema.json) |
| Examples (real, generated) | Yes | [`specs/atlas/v1/examples/`](../../../specs/atlas/v1/examples/) |
| Test vectors | Yes | [`specs/atlas/v1/test-vectors/`](../../../specs/atlas/v1/test-vectors/) |

## Machine-readable Forge specification — `specs/forge/v1/`

| File | Normative? | Path |
|---|---|---|
| Overview | — | [`specs/forge/v1/README.md`](../../../specs/forge/v1/README.md) |
| Rule schema | Yes | [`specs/forge/v1/rule.schema.json`](../../../specs/forge/v1/rule.schema.json) |
| Rule result schema | Yes | [`specs/forge/v1/rule-result.schema.json`](../../../specs/forge/v1/rule-result.schema.json) |
| Rule context schema | Yes | [`specs/forge/v1/rule-context.schema.json`](../../../specs/forge/v1/rule-context.schema.json) |
| Rule registry schema | Yes | [`specs/forge/v1/rule-registry.schema.json`](../../../specs/forge/v1/rule-registry.schema.json) |
| Current rule registry (21 rules) | Yes | [`specs/forge/v1/current-rule-registry.json`](../../../specs/forge/v1/current-rule-registry.json) |
| Examples (valid + invalid) | Yes | [`specs/forge/v1/examples/`](../../../specs/forge/v1/examples/) |
| Test vectors | Yes | [`specs/forge/v1/test-vectors/`](../../../specs/forge/v1/test-vectors/) |

## Machine-readable JDL specification — `specs/jdl/v1/`

| File | Normative? | Path |
|---|---|---|
| Overview | — | [`specs/jdl/v1/README.md`](../../../specs/jdl/v1/README.md) |
| JSON Schema | Yes (structural layer) | [`specs/jdl/v1/jdl.schema.json`](../../../specs/jdl/v1/jdl.schema.json) |
| EBNF grammar (planned DSL) | No | [`specs/jdl/v1/jdl.ebnf`](../../../specs/jdl/v1/jdl.ebnf) |
| Canonicalization reference | Yes | [`specs/jdl/v1/canonicalization.md`](../../../specs/jdl/v1/canonicalization.md) |
| Compiler contract reference | Yes (CURRENT rows) | [`specs/jdl/v1/compiler-contract.md`](../../../specs/jdl/v1/compiler-contract.md) |
| Examples (valid + invalid) | Yes | [`specs/jdl/v1/examples/`](../../../specs/jdl/v1/examples/) |
| Test vectors | Yes | [`specs/jdl/v1/test-vectors/`](../../../specs/jdl/v1/test-vectors/) |

## Pre-existing technical reference — `docs/`

These predate the Bible and remain authoritative for their own detail
(see [`000-bible-governance.md`](../00-foundation/000-bible-governance.md)).
No Bible `id` is assigned to them in this Sprint 1 pass.

| Title | Status | Path |
|---|---|---|
| Architecture | authoritative (detail level) | [`../../architecture.md`](../../architecture.md) |
| API reference | authoritative (detail level) | [`../../api.md`](../../api.md) |
| Development guide | authoritative (detail level) | [`../../development.md`](../../development.md) |
| Domain model | authoritative (detail level) | [`../../domain-model.md`](../../domain-model.md) |
| Geometry conventions | authoritative (detail level) | [`../../geometry-conventions.md`](../../geometry-conventions.md) |
| Known limitations | authoritative (detail level) | [`../../known-limitations.md`](../../known-limitations.md) |
| Validation rules | authoritative (detail level) | [`../../validation-rules.md`](../../validation-rules.md) |

## Root-level project documents

| Title | Purpose | Path |
|---|---|---|
| README | Product description, setup, commands | [`../../../README.md`](../../../README.md) |
| CLAUDE.md | Non-negotiable rules for coding agents, including Technical Bible rules | [`../../../CLAUDE.md`](../../../CLAUDE.md) |
| AUDIT_FIXES.md | Data-safety/reliability hardening pass summary | [`../../../AUDIT_FIXES.md`](../../../AUDIT_FIXES.md) |
