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
| JM-BIBLE-VISION-README | Vision v1 — Index | accepted | partial | [`10-vision/README.md`](../10-vision/README.md) |
| JM-BIBLE-220 | Vision Governance | accepted | current | [`10-vision/220-vision-governance.md`](../10-vision/220-vision-governance.md) |
| JM-BIBLE-221 | Vision Architecture Overview | accepted | current | [`10-vision/221-vision-architecture-overview.md`](../10-vision/221-vision-architecture-overview.md) |
| JM-BIBLE-222 | Visual Representation Model | accepted | current | [`10-vision/222-visual-representation-model.md`](../10-vision/222-visual-representation-model.md) |
| JM-BIBLE-223 | Atlas to Vision Contract | accepted | current | [`10-vision/223-atlas-to-vision-contract.md`](../10-vision/223-atlas-to-vision-contract.md) |
| JM-BIBLE-224 | Preview Mesh Contract (Vision) | accepted | current | [`10-vision/224-preview-mesh-contract.md`](../10-vision/224-preview-mesh-contract.md) |
| JM-BIBLE-225 | Scene Graph Model | accepted | current | [`10-vision/225-scene-graph-model.md`](../10-vision/225-scene-graph-model.md) |
| JM-BIBLE-226 | Component Visual Identity | accepted | current | [`10-vision/226-component-visual-identity.md`](../10-vision/226-component-visual-identity.md) |
| JM-BIBLE-227 | Technical View Contract | accepted | current | [`10-vision/227-technical-view-contract.md`](../10-vision/227-technical-view-contract.md) |
| JM-BIBLE-228 | Presentation View Contract | accepted | current | [`10-vision/228-presentation-view-contract.md`](../10-vision/228-presentation-view-contract.md) |
| JM-BIBLE-229 | Camera System | accepted | current | [`10-vision/229-camera-system.md`](../10-vision/229-camera-system.md) |
| JM-BIBLE-230 | Lighting System | accepted | current | [`10-vision/230-lighting-system.md`](../10-vision/230-lighting-system.md) |
| JM-BIBLE-231 | Material System | accepted | current | [`10-vision/231-material-system.md`](../10-vision/231-material-system.md) |
| JM-BIBLE-232 | Metal Material Model | accepted | current | [`10-vision/232-metal-material-model.md`](../10-vision/232-metal-material-model.md) |
| JM-BIBLE-233 | Stone Material Model | accepted | current | [`10-vision/233-stone-material-model.md`](../10-vision/233-stone-material-model.md) |
| JM-BIBLE-234 | Background and Environment Model | accepted | current | [`10-vision/234-background-and-environment-model.md`](../10-vision/234-background-and-environment-model.md) |
| JM-BIBLE-235 | Shadows and Grounding | accepted | current | [`10-vision/235-shadows-and-grounding.md`](../10-vision/235-shadows-and-grounding.md) |
| JM-BIBLE-236 | Component Visibility Model | accepted | current | [`10-vision/236-component-visibility-model.md`](../10-vision/236-component-visibility-model.md) |
| JM-BIBLE-237 | Model Framing and Fit | accepted | current | [`10-vision/237-model-framing-and-fit.md`](../10-vision/237-model-framing-and-fit.md) |
| JM-BIBLE-238 | Image Capture Contract | accepted | current | [`10-vision/238-image-capture-contract.md`](../10-vision/238-image-capture-contract.md) |
| JM-BIBLE-239 | Render State Model | accepted | partial | [`10-vision/239-render-state-model.md`](../10-vision/239-render-state-model.md) |
| JM-BIBLE-240 | Stale and Last-Good Preview | accepted | current | [`10-vision/240-stale-and-last-good-preview.md`](../10-vision/240-stale-and-last-good-preview.md) |
| JM-BIBLE-241 | Rendering Errors and Diagnostics | accepted | planned | [`10-vision/241-rendering-errors-and-diagnostics.md`](../10-vision/241-rendering-errors-and-diagnostics.md) |
| JM-BIBLE-242 | Performance and GPU Resource Model | accepted | partial | [`10-vision/242-performance-and-gpu-resource-model.md`](../10-vision/242-performance-and-gpu-resource-model.md) |
| JM-BIBLE-243 | Accessibility and Input Model | accepted | partial | [`10-vision/243-accessibility-and-input-model.md`](../10-vision/243-accessibility-and-input-model.md) |
| JM-BIBLE-244 | Visual Consistency Contract | accepted | current | [`10-vision/244-visual-consistency-contract.md`](../10-vision/244-visual-consistency-contract.md) |
| JM-BIBLE-245 | Visual Regression Strategy | accepted | planned | [`10-vision/245-visual-regression-strategy.md`](../10-vision/245-visual-regression-strategy.md) |
| JM-BIBLE-246 | Current Viewer Code Mapping | accepted | current | [`10-vision/246-current-viewer-code-mapping.md`](../10-vision/246-current-viewer-code-mapping.md) |
| JM-BIBLE-247 | Vision Gap Analysis | accepted | current | [`10-vision/247-vision-gap-analysis.md`](../10-vision/247-vision-gap-analysis.md) |
| JM-BIBLE-248 | Open Vision Questions | accepted | current | [`10-vision/248-open-vision-questions.md`](../10-vision/248-open-vision-questions.md) |
| JM-BIBLE-SPRINT8-REPORT | Sprint 8 Validation Report | accepted | current | [`10-vision/SPRINT-8-VALIDATION-REPORT.md`](../10-vision/SPRINT-8-VALIDATION-REPORT.md) |
| JM-BIBLE-A41 | Appendix: Vision Component Style Catalog | accepted | current | [`appendices/vision-component-style-catalog.md`](vision-component-style-catalog.md) |
| JM-BIBLE-A42 | Appendix: Vision Camera Preset Catalog | accepted | current | [`appendices/vision-camera-preset-catalog.md`](vision-camera-preset-catalog.md) |
| JM-BIBLE-A43 | Appendix: Vision Material Catalog | accepted | current | [`appendices/vision-material-catalog.md`](vision-material-catalog.md) |
| JM-BIBLE-A44 | Appendix: Vision Render State Catalog | accepted | partial | [`appendices/vision-render-state-catalog.md`](vision-render-state-catalog.md) |
| JM-BIBLE-A45 | Appendix: Vision Diagnostic Catalog | accepted | planned | [`appendices/vision-diagnostic-catalog.md`](vision-diagnostic-catalog.md) |
| JM-BIBLE-A46 | Appendix: Vision Code Mapping | accepted | current | [`appendices/vision-code-mapping.md`](vision-code-mapping.md) |
| JM-BIBLE-A47 | Appendix: Vision Test Matrix | accepted | current | [`appendices/vision-test-matrix.md`](vision-test-matrix.md) |
| JM-BIBLE-STUDIO-README | Studio v1 — Index | accepted | current | [`11-studio/README.md`](../11-studio/README.md) |
| JM-BIBLE-250 | Studio Governance | accepted | current | [`11-studio/250-studio-governance.md`](../11-studio/250-studio-governance.md) |
| JM-BIBLE-251 | Product Workspace Overview | accepted | current | [`11-studio/251-product-workspace-overview.md`](../11-studio/251-product-workspace-overview.md) |
| JM-BIBLE-252 | Information Architecture | accepted | current | [`11-studio/252-information-architecture.md`](../11-studio/252-information-architecture.md) |
| JM-BIBLE-253 | User Workflow Model | accepted | current | [`11-studio/253-user-workflow-model.md`](../11-studio/253-user-workflow-model.md) |
| JM-BIBLE-254 | Project Session Model | accepted | current | [`11-studio/254-project-session-model.md`](../11-studio/254-project-session-model.md) |
| JM-BIBLE-255 | Design Editing Contract | accepted | current | [`11-studio/255-design-editing-contract.md`](../11-studio/255-design-editing-contract.md) |
| JM-BIBLE-256 | Parameter Editor Model | accepted | current | [`11-studio/256-parameter-editor-model.md`](../11-studio/256-parameter-editor-model.md) |
| JM-BIBLE-257 | Validation Experience | accepted | current | [`11-studio/257-validation-experience.md`](../11-studio/257-validation-experience.md) |
| JM-BIBLE-258 | Generation Experience | accepted | current | [`11-studio/258-generation-experience.md`](../11-studio/258-generation-experience.md) |
| JM-BIBLE-259 | Model State Experience | accepted | current | [`11-studio/259-model-state-experience.md`](../11-studio/259-model-state-experience.md) |
| JM-BIBLE-260 | Output Review Experience | accepted | current | [`11-studio/260-output-review-experience.md`](../11-studio/260-output-review-experience.md) |
| JM-BIBLE-261 | Export Experience | accepted | current | [`11-studio/261-export-experience.md`](../11-studio/261-export-experience.md) |
| JM-BIBLE-262 | Technical Review Workspace | accepted | current | [`11-studio/262-technical-review-workspace.md`](../11-studio/262-technical-review-workspace.md) |
| JM-BIBLE-263 | Presentation Review Workspace | accepted | current | [`11-studio/263-presentation-review-workspace.md`](../11-studio/263-presentation-review-workspace.md) |
| JM-BIBLE-264 | Navigation Model | accepted | current | [`11-studio/264-navigation-model.md`](../11-studio/264-navigation-model.md) |
| JM-BIBLE-265 | Layout System | accepted | current | [`11-studio/265-layout-system.md`](../11-studio/265-layout-system.md) |
| JM-BIBLE-266 | Responsive Behaviour | accepted | partial | [`11-studio/266-responsive-behaviour.md`](../11-studio/266-responsive-behaviour.md) |
| JM-BIBLE-267 | Status and Feedback System | accepted | current | [`11-studio/267-status-and-feedback-system.md`](../11-studio/267-status-and-feedback-system.md) |
| JM-BIBLE-268 | Loading and Progress Model | accepted | current | [`11-studio/268-loading-and-progress-model.md`](../11-studio/268-loading-and-progress-model.md) |
| JM-BIBLE-269 | Error Recovery Model | accepted | current | [`11-studio/269-error-recovery-model.md`](../11-studio/269-error-recovery-model.md) |
| JM-BIBLE-270 | Empty State Model | accepted | current | [`11-studio/270-empty-state-model.md`](../11-studio/270-empty-state-model.md) |
| JM-BIBLE-271 | Confirmation and Destructive Actions | accepted | current | [`11-studio/271-confirmation-and-destructive-actions.md`](../11-studio/271-confirmation-and-destructive-actions.md) |
| JM-BIBLE-272 | Accessibility Contract | accepted | partial | [`11-studio/272-accessibility-contract.md`](../11-studio/272-accessibility-contract.md) |
| JM-BIBLE-273 | Keyboard and Input Model | accepted | current | [`11-studio/273-keyboard-and-input-model.md`](../11-studio/273-keyboard-and-input-model.md) |
| JM-BIBLE-274 | Local Persistence Model | accepted | current | [`11-studio/274-local-persistence-model.md`](../11-studio/274-local-persistence-model.md) |
| JM-BIBLE-275 | Session Recovery | accepted | current | [`11-studio/275-session-recovery.md`](../11-studio/275-session-recovery.md) |
| JM-BIBLE-276 | Design System Foundations | accepted | current | [`11-studio/276-design-system-foundations.md`](../11-studio/276-design-system-foundations.md) |
| JM-BIBLE-277 | UI Component Architecture | accepted | current | [`11-studio/277-ui-component-architecture.md`](../11-studio/277-ui-component-architecture.md) |
| JM-BIBLE-278 | Frontend State Architecture | accepted | current | [`11-studio/278-frontend-state-architecture.md`](../11-studio/278-frontend-state-architecture.md) |
| JM-BIBLE-279 | API Interaction Model | accepted | current | [`11-studio/279-api-interaction-model.md`](../11-studio/279-api-interaction-model.md) |
| JM-BIBLE-280 | Product Copy and Terminology | accepted | current | [`11-studio/280-product-copy-and-terminology.md`](../11-studio/280-product-copy-and-terminology.md) |
| JM-BIBLE-281 | User Guidance Model | accepted | current | [`11-studio/281-user-guidance-model.md`](../11-studio/281-user-guidance-model.md) |
| JM-BIBLE-282 | Current UI Code Mapping | accepted | current | [`11-studio/282-current-ui-code-mapping.md`](../11-studio/282-current-ui-code-mapping.md) |
| JM-BIBLE-283 | Studio Gap Analysis | accepted | current | [`11-studio/283-studio-gap-analysis.md`](../11-studio/283-studio-gap-analysis.md) |
| JM-BIBLE-284 | Open Studio Questions | accepted | current | [`11-studio/284-open-studio-questions.md`](../11-studio/284-open-studio-questions.md) |
| JM-BIBLE-SPRINT9-REPORT | Sprint 9 Validation Report | accepted | current | [`11-studio/SPRINT-9-VALIDATION-REPORT.md`](../11-studio/SPRINT-9-VALIDATION-REPORT.md) |
| JM-BIBLE-A48 | Appendix: Studio Screen Catalog | accepted | current | [`appendices/studio-screen-catalog.md`](studio-screen-catalog.md) |
| JM-BIBLE-A49 | Appendix: Studio State Catalog | accepted | current | [`appendices/studio-state-catalog.md`](studio-state-catalog.md) |
| JM-BIBLE-A50 | Appendix: Studio Action Catalog | accepted | current | [`appendices/studio-action-catalog.md`](studio-action-catalog.md) |
| JM-BIBLE-A51 | Appendix: Studio Status Catalog | accepted | current | [`appendices/studio-status-catalog.md`](studio-status-catalog.md) |
| JM-BIBLE-A52 | Appendix: Studio UI Component Catalog | accepted | current | [`appendices/studio-ui-component-catalog.md`](studio-ui-component-catalog.md) |
| JM-BIBLE-A53 | Appendix: Studio Copy Catalog | accepted | current | [`appendices/studio-copy-catalog.md`](studio-copy-catalog.md) |
| JM-BIBLE-A54 | Appendix: Studio Code Mapping | accepted | current | [`appendices/studio-code-mapping.md`](studio-code-mapping.md) |
| JM-BIBLE-A55 | Appendix: Studio Test Matrix | accepted | current | [`appendices/studio-test-matrix.md`](studio-test-matrix.md) |
| JM-BIBLE-DESIGNER-README | Designer v1 — Index | accepted | current | [`12-designer/README.md`](../12-designer/README.md) |
| JM-BIBLE-290 | Designer Governance | accepted | current | [`12-designer/290-designer-governance.md`](../12-designer/290-designer-governance.md) |
| JM-BIBLE-291 | Designer Architecture Overview | accepted | current | [`12-designer/291-designer-architecture-overview.md`](../12-designer/291-designer-architecture-overview.md) |
| JM-BIBLE-292 | Natural Language Input Contract | accepted | current | [`12-designer/292-natural-language-input-contract.md`](../12-designer/292-natural-language-input-contract.md) |
| JM-BIBLE-293 | Intent Extraction Model | accepted | current | [`12-designer/293-intent-extraction-model.md`](../12-designer/293-intent-extraction-model.md) |
| JM-BIBLE-294 | Design Proposal Model | accepted | current | [`12-designer/294-design-proposal-model.md`](../12-designer/294-design-proposal-model.md) |
| JM-BIBLE-295 | Designer To JDL Contract | accepted | current | [`12-designer/295-designer-to-jdl-contract.md`](../12-designer/295-designer-to-jdl-contract.md) |
| JM-BIBLE-296 | Capability Awareness | accepted | current | [`12-designer/296-capability-awareness.md`](../12-designer/296-capability-awareness.md) |
| JM-BIBLE-297 | Supported Language Scope | accepted | current | [`12-designer/297-supported-language-scope.md`](../12-designer/297-supported-language-scope.md) |
| JM-BIBLE-298 | Defaulting Policy | accepted | current | [`12-designer/298-defaulting-policy.md`](../12-designer/298-defaulting-policy.md) |
| JM-BIBLE-299 | Ambiguity Model | accepted | current | [`12-designer/299-ambiguity-model.md`](../12-designer/299-ambiguity-model.md) |
| JM-BIBLE-300 | Clarification Policy | accepted | current | [`12-designer/300-clarification-policy.md`](../12-designer/300-clarification-policy.md) |
| JM-BIBLE-301 | Unsupported Request Handling | accepted | current | [`12-designer/301-unsupported-request-handling.md`](../12-designer/301-unsupported-request-handling.md) |
| JM-BIBLE-302 | Confidence Model | accepted | current | [`12-designer/302-confidence-model.md`](../12-designer/302-confidence-model.md) |
| JM-BIBLE-303 | Field Provenance Model | accepted | current | [`12-designer/303-field-provenance-model.md`](../12-designer/303-field-provenance-model.md) |
| JM-BIBLE-304 | AI Output Constraining | accepted | current | [`12-designer/304-ai-output-constraining.md`](../12-designer/304-ai-output-constraining.md) |
| JM-BIBLE-305 | Structured Output Contract | accepted | current | [`12-designer/305-structured-output-contract.md`](../12-designer/305-structured-output-contract.md) |
| JM-BIBLE-306 | Prompt Architecture | accepted | current | [`12-designer/306-prompt-architecture.md`](../12-designer/306-prompt-architecture.md) |
| JM-BIBLE-307 | Provider Abstraction | accepted | partial | [`12-designer/307-provider-abstraction.md`](../12-designer/307-provider-abstraction.md) |
| JM-BIBLE-308 | Designer Validation Pipeline | accepted | current | [`12-designer/308-designer-validation-pipeline.md`](../12-designer/308-designer-validation-pipeline.md) |
| JM-BIBLE-309 | Designer Forge Integration | accepted | current | [`12-designer/309-designer-forge-integration.md`](../12-designer/309-designer-forge-integration.md) |
| JM-BIBLE-310 | User Review and Acceptance | accepted | current | [`12-designer/310-user-review-and-acceptance.md`](../12-designer/310-user-review-and-acceptance.md) |
| JM-BIBLE-311 | Proposal Diff Model | accepted | current | [`12-designer/311-proposal-diff-model.md`](../12-designer/311-proposal-diff-model.md) |
| JM-BIBLE-312 | Designer Error Model | accepted | current | [`12-designer/312-designer-error-model.md`](../12-designer/312-designer-error-model.md) |
| JM-BIBLE-313 | Designer Security Model | accepted | current | [`12-designer/313-designer-security-model.md`](../12-designer/313-designer-security-model.md) |
| JM-BIBLE-314 | Prompt Injection and Untrusted Input | accepted | current | [`12-designer/314-prompt-injection-and-untrusted-input.md`](../12-designer/314-prompt-injection-and-untrusted-input.md) |
| JM-BIBLE-315 | Privacy and Data Boundaries | accepted | current | [`12-designer/315-privacy-and-data-boundaries.md`](../12-designer/315-privacy-and-data-boundaries.md) |
| JM-BIBLE-316 | Designer Observability | accepted | current | [`12-designer/316-designer-observability.md`](../12-designer/316-designer-observability.md) |
| JM-BIBLE-317 | Designer Cost and Latency Model | accepted | current | [`12-designer/317-designer-cost-and-latency-model.md`](../12-designer/317-designer-cost-and-latency-model.md) |
| JM-BIBLE-318 | Designer Evaluation Framework | accepted | current | [`12-designer/318-designer-evaluation-framework.md`](../12-designer/318-designer-evaluation-framework.md) |
| JM-BIBLE-319 | Designer Test Corpus | accepted | current | [`12-designer/319-designer-test-corpus.md`](../12-designer/319-designer-test-corpus.md) |
| JM-BIBLE-320 | Current Studio Integration | accepted | current | [`12-designer/320-current-studio-integration.md`](../12-designer/320-current-studio-integration.md) |
| JM-BIBLE-321 | Designer Gap Analysis | accepted | current | [`12-designer/321-designer-gap-analysis.md`](../12-designer/321-designer-gap-analysis.md) |
| JM-BIBLE-322 | Open Designer Questions | accepted | current | [`12-designer/322-open-designer-questions.md`](../12-designer/322-open-designer-questions.md) |
| JM-BIBLE-SPRINT10-REPORT | Sprint 10 Validation Report | accepted | current | [`12-designer/SPRINT-10-VALIDATION-REPORT.md`](../12-designer/SPRINT-10-VALIDATION-REPORT.md) |
| JM-BIBLE-DESIGN-INTENT-README | Design Intent Model v1 — Index | accepted | current | [`13-design-intent/README.md`](../13-design-intent/README.md) |
| JM-BIBLE-330 | Intent Governance | accepted | current | [`13-design-intent/330-intent-governance.md`](../13-design-intent/330-intent-governance.md) |
| JM-BIBLE-331 | Design Intent Architecture | accepted | current | [`13-design-intent/331-design-intent-architecture.md`](../13-design-intent/331-design-intent-architecture.md) |
| JM-BIBLE-332 | Intent Domain Model | accepted | current | [`13-design-intent/332-intent-domain-model.md`](../13-design-intent/332-intent-domain-model.md) |
| JM-BIBLE-333 | Intent Vocabulary | accepted | current | [`13-design-intent/333-intent-vocabulary.md`](../13-design-intent/333-intent-vocabulary.md) |
| JM-BIBLE-334 | Intent Target Model | accepted | current | [`13-design-intent/334-intent-target-model.md`](../13-design-intent/334-intent-target-model.md) |
| JM-BIBLE-335 | Aesthetic Descriptor Model | accepted | current | [`13-design-intent/335-aesthetic-descriptor-model.md`](../13-design-intent/335-aesthetic-descriptor-model.md) |
| JM-BIBLE-336 | Relative Proportion Intent | accepted | current | [`13-design-intent/336-relative-proportion-intent.md`](../13-design-intent/336-relative-proportion-intent.md) |
| JM-BIBLE-337 | Visual Weight Model | accepted | current | [`13-design-intent/337-visual-weight-model.md`](../13-design-intent/337-visual-weight-model.md) |
| JM-BIBLE-338 | Style Continuum Model | accepted | current | [`13-design-intent/338-style-continuum-model.md`](../13-design-intent/338-style-continuum-model.md) |
| JM-BIBLE-339 | Emphasis And Hierarchy Model | accepted | current | [`13-design-intent/339-emphasis-and-hierarchy-model.md`](../13-design-intent/339-emphasis-and-hierarchy-model.md) |
| JM-BIBLE-340 | Symmetry And Balance Model | accepted | current | [`13-design-intent/340-symmetry-and-balance-model.md`](../13-design-intent/340-symmetry-and-balance-model.md) |
| JM-BIBLE-341 | Simplicity And Complexity Model | accepted | current | [`13-design-intent/341-simplicity-and-complexity-model.md`](../13-design-intent/341-simplicity-and-complexity-model.md) |
| JM-BIBLE-342 | Classic Contemporary Model | accepted | current | [`13-design-intent/342-classic-contemporary-model.md`](../13-design-intent/342-classic-contemporary-model.md) |
| JM-BIBLE-343 | Intent Strength And Priority | accepted | current | [`13-design-intent/343-intent-strength-and-priority.md`](../13-design-intent/343-intent-strength-and-priority.md) |
| JM-BIBLE-344 | Intent Provenance | accepted | current | [`13-design-intent/344-intent-provenance.md`](../13-design-intent/344-intent-provenance.md) |
| JM-BIBLE-345 | Intent Confidence | accepted | current | [`13-design-intent/345-intent-confidence.md`](../13-design-intent/345-intent-confidence.md) |
| JM-BIBLE-346 | Intent Conflict Model | accepted | current | [`13-design-intent/346-intent-conflict-model.md`](../13-design-intent/346-intent-conflict-model.md) |
| JM-BIBLE-347 | Intent Compatibility Model | accepted | current | [`13-design-intent/347-intent-compatibility-model.md`](../13-design-intent/347-intent-compatibility-model.md) |
| JM-BIBLE-348 | Intent Resolution Model | accepted | current | [`13-design-intent/348-intent-resolution-model.md`](../13-design-intent/348-intent-resolution-model.md) |
| JM-BIBLE-349 | Deterministic Resolution Policy | accepted | current | [`13-design-intent/349-deterministic-resolution-policy.md`](../13-design-intent/349-deterministic-resolution-policy.md) |
| JM-BIBLE-350 | Intent To JDL Boundary | accepted | current | [`13-design-intent/350-intent-to-jdl-boundary.md`](../13-design-intent/350-intent-to-jdl-boundary.md) |
| JM-BIBLE-351 | Intent To Forge Boundary | accepted | current | [`13-design-intent/351-intent-to-forge-boundary.md`](../13-design-intent/351-intent-to-forge-boundary.md) |
| JM-BIBLE-352 | Unresolved Intent Lifecycle | accepted | current | [`13-design-intent/352-unresolved-intent-lifecycle.md`](../13-design-intent/352-unresolved-intent-lifecycle.md) |
| JM-BIBLE-353 | Intent Preservation | accepted | current | [`13-design-intent/353-intent-preservation.md`](../13-design-intent/353-intent-preservation.md) |
| JM-BIBLE-354 | Intent Diff Model | accepted | current | [`13-design-intent/354-intent-diff-model.md`](../13-design-intent/354-intent-diff-model.md) |
| JM-BIBLE-355 | Intent Profile Model | accepted | current | [`13-design-intent/355-intent-profile-model.md`](../13-design-intent/355-intent-profile-model.md) |
| JM-BIBLE-356 | Designer Intent Extraction | accepted | current | [`13-design-intent/356-designer-intent-extraction.md`](../13-design-intent/356-designer-intent-extraction.md) |
| JM-BIBLE-357 | Studio Intent Review | accepted | current | [`13-design-intent/357-studio-intent-review.md`](../13-design-intent/357-studio-intent-review.md) |
| JM-BIBLE-358 | Intent Diagnostics | accepted | current | [`13-design-intent/358-intent-diagnostics.md`](../13-design-intent/358-intent-diagnostics.md) |
| JM-BIBLE-359 | Intent Evaluation Framework | accepted | current | [`13-design-intent/359-intent-evaluation-framework.md`](../13-design-intent/359-intent-evaluation-framework.md) |
| JM-BIBLE-360 | Intent Test Corpus | accepted | current | [`13-design-intent/360-intent-test-corpus.md`](../13-design-intent/360-intent-test-corpus.md) |
| JM-BIBLE-361 | Current Code Mapping | accepted | current | [`13-design-intent/361-current-code-mapping.md`](../13-design-intent/361-current-code-mapping.md) |
| JM-BIBLE-362 | Design Intent Gap Analysis | accepted | current | [`13-design-intent/362-design-intent-gap-analysis.md`](../13-design-intent/362-design-intent-gap-analysis.md) |
| JM-BIBLE-363 | Open Design Intent Questions | accepted | current | [`13-design-intent/363-open-design-intent-questions.md`](../13-design-intent/363-open-design-intent-questions.md) |
| JM-BIBLE-SPRINT11-REPORT | Sprint 11 Validation Report | accepted | current | [`13-design-intent/SPRINT-11-VALIDATION-REPORT.md`](../13-design-intent/SPRINT-11-VALIDATION-REPORT.md) |
| JM-BIBLE-A56 | Appendix: Designer Supported Intent Catalog | accepted | current | [`appendices/designer-supported-intent-catalog.md`](designer-supported-intent-catalog.md) |
| JM-BIBLE-A57 | Appendix: Designer Field Provenance Catalog | accepted | current | [`appendices/designer-field-provenance-catalog.md`](designer-field-provenance-catalog.md) |
| JM-BIBLE-A58 | Appendix: Designer Clarification Catalog | accepted | current | [`appendices/designer-clarification-catalog.md`](designer-clarification-catalog.md) |
| JM-BIBLE-A59 | Appendix: Designer Unsupported Feature Catalog | accepted | current | [`appendices/designer-unsupported-feature-catalog.md`](designer-unsupported-feature-catalog.md) |
| JM-BIBLE-A60 | Appendix: Designer Diagnostic Catalog | accepted | current | [`appendices/designer-diagnostic-catalog.md`](designer-diagnostic-catalog.md) |
| JM-BIBLE-A61 | Appendix: Designer Test Case Catalog | accepted | current | [`appendices/designer-test-case-catalog.md`](designer-test-case-catalog.md) |
| JM-BIBLE-A62 | Appendix: Designer Code Mapping | accepted | current | [`appendices/designer-code-mapping.md`](designer-code-mapping.md) |
| JM-BIBLE-A63 | Appendix: Designer Test Matrix | accepted | current | [`appendices/designer-test-matrix.md`](designer-test-matrix.md) |
| JM-BIBLE-A64 | Appendix: Intent Vocabulary Catalog | accepted | current | [`appendices/intent-vocabulary-catalog.md`](intent-vocabulary-catalog.md) |
| JM-BIBLE-A65 | Appendix: Intent Target Catalog | accepted | current | [`appendices/intent-target-catalog.md`](intent-target-catalog.md) |
| JM-BIBLE-A66 | Appendix: Intent Relation Catalog | accepted | current | [`appendices/intent-relation-catalog.md`](intent-relation-catalog.md) |
| JM-BIBLE-A67 | Appendix: Intent Resolution Catalog | accepted | current | [`appendices/intent-resolution-catalog.md`](intent-resolution-catalog.md) |
| JM-BIBLE-A68 | Appendix: Intent Conflict Catalog | accepted | current | [`appendices/intent-conflict-catalog.md`](intent-conflict-catalog.md) |
| JM-BIBLE-A69 | Appendix: Intent Diagnostic Catalog | accepted | current | [`appendices/intent-diagnostic-catalog.md`](intent-diagnostic-catalog.md) |
| JM-BIBLE-A70 | Appendix: Intent Test Case Catalog | accepted | current | [`appendices/intent-test-case-catalog.md`](intent-test-case-catalog.md) |
| JM-BIBLE-A71 | Appendix: Intent Code Mapping | accepted | current | [`appendices/intent-code-mapping.md`](intent-code-mapping.md) |
| JM-BIBLE-A72 | Appendix: Intent Test Matrix | accepted | current | [`appendices/intent-test-matrix.md`](intent-test-matrix.md) |
| JM-BIBLE-CONVERSATION-README | Conversation Engine v1 — Index | accepted | current | [`14-conversation/README.md`](../14-conversation/README.md) |
| JM-BIBLE-370 | Conversation Governance | accepted | current | [`14-conversation/370-conversation-governance.md`](../14-conversation/370-conversation-governance.md) |
| JM-BIBLE-371 | Conversation Architecture | accepted | current | [`14-conversation/371-conversation-architecture.md`](../14-conversation/371-conversation-architecture.md) |
| JM-BIBLE-372 | Conversation Domain Model | accepted | current | [`14-conversation/372-conversation-domain-model.md`](../14-conversation/372-conversation-domain-model.md) |
| JM-BIBLE-373 | Conversation Session Lifecycle | accepted | current | [`14-conversation/373-conversation-session-lifecycle.md`](../14-conversation/373-conversation-session-lifecycle.md) |
| JM-BIBLE-374 | Conversation Turn Model | accepted | current | [`14-conversation/374-conversation-turn-model.md`](../14-conversation/374-conversation-turn-model.md) |
| JM-BIBLE-375 | Turn Context Model | accepted | current | [`14-conversation/375-turn-context-model.md`](../14-conversation/375-turn-context-model.md) |
| JM-BIBLE-376 | Conversation State Machine | accepted | current | [`14-conversation/376-conversation-state-machine.md`](../14-conversation/376-conversation-state-machine.md) |
| JM-BIBLE-377 | Design State Synchronization | accepted | current | [`14-conversation/377-design-state-synchronization.md`](../14-conversation/377-design-state-synchronization.md) |
| JM-BIBLE-378 | Turn Role and Message Model | accepted | current | [`14-conversation/378-turn-role-and-message-model.md`](../14-conversation/378-turn-role-and-message-model.md) |
| JM-BIBLE-379 | Reference Resolution | accepted | current | [`14-conversation/379-reference-resolution.md`](../14-conversation/379-reference-resolution.md) |
| JM-BIBLE-380 | Pronoun and Implicit Target Resolution | accepted | current | [`14-conversation/380-pronoun-and-implicit-target-resolution.md`](../14-conversation/380-pronoun-and-implicit-target-resolution.md) |
| JM-BIBLE-381 | Clarification Thread Model | accepted | current | [`14-conversation/381-clarification-thread-model.md`](../14-conversation/381-clarification-thread-model.md) |
| JM-BIBLE-382 | Clarification Answer Resolution | accepted | current | [`14-conversation/382-clarification-answer-resolution.md`](../14-conversation/382-clarification-answer-resolution.md) |
| JM-BIBLE-383 | Correction Model | accepted | current | [`14-conversation/383-correction-model.md`](../14-conversation/383-correction-model.md) |
| JM-BIBLE-384 | Accept Reject Cancel Semantics | accepted | current | [`14-conversation/384-accept-reject-cancel-semantics.md`](../14-conversation/384-accept-reject-cancel-semantics.md) |
| JM-BIBLE-385 | Conversational Diff Model | accepted | current | [`14-conversation/385-conversational-diff-model.md`](../14-conversation/385-conversational-diff-model.md) |
| JM-BIBLE-386 | State Preservation Policy | accepted | current | [`14-conversation/386-state-preservation-policy.md`](../14-conversation/386-state-preservation-policy.md) |
| JM-BIBLE-387 | Context Window Policy | accepted | current | [`14-conversation/387-context-window-policy.md`](../14-conversation/387-context-window-policy.md) |
| JM-BIBLE-388 | History Compaction Model | accepted | current | [`14-conversation/388-history-compaction-model.md`](../14-conversation/388-history-compaction-model.md) |
| JM-BIBLE-389 | Conversation Summary Model | accepted | current | [`14-conversation/389-conversation-summary-model.md`](../14-conversation/389-conversation-summary-model.md) |
| JM-BIBLE-390 | Provider Context Contract | accepted | current | [`14-conversation/390-provider-context-contract.md`](../14-conversation/390-provider-context-contract.md) |
| JM-BIBLE-391 | Conversation Designer Integration | accepted | current | [`14-conversation/391-conversation-designer-integration.md`](../14-conversation/391-conversation-designer-integration.md) |
| JM-BIBLE-392 | Conversation Intent Integration | accepted | current | [`14-conversation/392-conversation-intent-integration.md`](../14-conversation/392-conversation-intent-integration.md) |
| JM-BIBLE-393 | Conversation JDL Integration | accepted | current | [`14-conversation/393-conversation-jdl-integration.md`](../14-conversation/393-conversation-jdl-integration.md) |
| JM-BIBLE-394 | Conversation Forge Integration | accepted | current | [`14-conversation/394-conversation-forge-integration.md`](../14-conversation/394-conversation-forge-integration.md) |
| JM-BIBLE-395 | Studio Integration | accepted | current | [`14-conversation/395-studio-integration.md`](../14-conversation/395-studio-integration.md) |
| JM-BIBLE-396 | Conversational Error Model | accepted | current | [`14-conversation/396-conversational-error-model.md`](../14-conversation/396-conversational-error-model.md) |
| JM-BIBLE-397 | Conversation Security | accepted | current | [`14-conversation/397-conversation-security.md`](../14-conversation/397-conversation-security.md) |
| JM-BIBLE-398 | Conversation Privacy | accepted | current | [`14-conversation/398-conversation-privacy.md`](../14-conversation/398-conversation-privacy.md) |
| JM-BIBLE-399 | Conversation Observability | accepted | current | [`14-conversation/399-conversation-observability.md`](../14-conversation/399-conversation-observability.md) |
| JM-BIBLE-400 | Conversation Evaluation Framework | accepted | current | [`14-conversation/400-conversation-evaluation-framework.md`](../14-conversation/400-conversation-evaluation-framework.md) |
| JM-BIBLE-401 | Conversation Test Corpus | accepted | current | [`14-conversation/401-conversation-test-corpus.md`](../14-conversation/401-conversation-test-corpus.md) |
| JM-BIBLE-402 | Stale Context and Concurrent Editing | accepted | current | [`14-conversation/402-stale-context-and-concurrent-editing.md`](../14-conversation/402-stale-context-and-concurrent-editing.md) |
| JM-BIBLE-403 | Current Code Mapping | accepted | current | [`14-conversation/403-current-code-mapping.md`](../14-conversation/403-current-code-mapping.md) |
| JM-BIBLE-404 | Conversation Gap Analysis and Open Questions | accepted | current | [`14-conversation/404-conversation-gap-analysis-and-open-questions.md`](../14-conversation/404-conversation-gap-analysis-and-open-questions.md) |
| JM-BIBLE-SPRINT12-REPORT | Sprint 12 Validation Report | accepted | current | [`14-conversation/SPRINT-12-VALIDATION-REPORT.md`](../14-conversation/SPRINT-12-VALIDATION-REPORT.md) |
| JM-BIBLE-A73 | Appendix: Conversation Action Catalog | accepted | current | [`appendices/conversation-action-catalog.md`](conversation-action-catalog.md) |
| JM-BIBLE-A74 | Appendix: Conversation State Catalog | accepted | current | [`appendices/conversation-state-catalog.md`](conversation-state-catalog.md) |
| JM-BIBLE-A75 | Appendix: Conversation Reference Catalog | accepted | current | [`appendices/conversation-reference-catalog.md`](conversation-reference-catalog.md) |
| JM-BIBLE-A76 | Appendix: Clarification Type Catalog | accepted | current | [`appendices/clarification-type-catalog.md`](clarification-type-catalog.md) |
| JM-BIBLE-A77 | Appendix: Conversation Diagnostic Catalog | accepted | current | [`appendices/conversation-diagnostic-catalog.md`](conversation-diagnostic-catalog.md) |
| JM-BIBLE-A78 | Appendix: Conversation Test Case Catalog | accepted | current | [`appendices/conversation-test-case-catalog.md`](conversation-test-case-catalog.md) |
| JM-BIBLE-A79 | Appendix: Conversation Code Mapping | accepted | current | [`appendices/conversation-code-mapping.md`](conversation-code-mapping.md) |
| JM-BIBLE-A80 | Appendix: Conversation Test Matrix | accepted | current | [`appendices/conversation-test-matrix.md`](conversation-test-matrix.md) |
| JM-BIBLE-PROVAL-README | Professional Validation Framework v1 — Index | accepted | current | [`15-professional-validation/README.md`](../15-professional-validation/README.md) |
| JM-BIBLE-410 | Validation Governance | accepted | current | [`15-professional-validation/410-validation-governance.md`](../15-professional-validation/410-validation-governance.md) |
| JM-BIBLE-411 | Professional Validation Overview | accepted | current | [`15-professional-validation/411-professional-validation-overview.md`](../15-professional-validation/411-professional-validation-overview.md) |
| JM-BIBLE-412 | Validation Object Model | accepted | current | [`15-professional-validation/412-validation-object-model.md`](../15-professional-validation/412-validation-object-model.md) |
| JM-BIBLE-413 | Reviewer Role Model | accepted | current | [`15-professional-validation/413-reviewer-role-model.md`](../15-professional-validation/413-reviewer-role-model.md) |
| JM-BIBLE-414 | Reviewer Qualification Model | accepted | current | [`15-professional-validation/414-reviewer-qualification-model.md`](../15-professional-validation/414-reviewer-qualification-model.md) |
| JM-BIBLE-415 | Validation Scope Model | accepted | current | [`15-professional-validation/415-validation-scope-model.md`](../15-professional-validation/415-validation-scope-model.md) |
| JM-BIBLE-416 | Review Session Model | accepted | current | [`15-professional-validation/416-review-session-model.md`](../15-professional-validation/416-review-session-model.md) |
| JM-BIBLE-417 | Review Evidence Model | accepted | current | [`15-professional-validation/417-review-evidence-model.md`](../15-professional-validation/417-review-evidence-model.md) |
| JM-BIBLE-418 | Validation Decision Model | accepted | current | [`15-professional-validation/418-validation-decision-model.md`](../15-professional-validation/418-validation-decision-model.md) |
| JM-BIBLE-419 | Rule Validation Process | accepted | current | [`15-professional-validation/419-rule-validation-process.md`](../15-professional-validation/419-rule-validation-process.md) |
| JM-BIBLE-420 | Geometry Validation Process | accepted | current | [`15-professional-validation/420-geometry-validation-process.md`](../15-professional-validation/420-geometry-validation-process.md) |
| JM-BIBLE-421 | Manufacturing Validation Process | accepted | current | [`15-professional-validation/421-manufacturing-validation-process.md`](../15-professional-validation/421-manufacturing-validation-process.md) |
| JM-BIBLE-422 | Setting Validation Process | accepted | current | [`15-professional-validation/422-setting-validation-process.md`](../15-professional-validation/422-setting-validation-process.md) |
| JM-BIBLE-423 | Material Validation Process | accepted | current | [`15-professional-validation/423-material-validation-process.md`](../15-professional-validation/423-material-validation-process.md) |
| JM-BIBLE-424 | CAD Workflow Validation Process | accepted | current | [`15-professional-validation/424-cad-workflow-validation-process.md`](../15-professional-validation/424-cad-workflow-validation-process.md) |
| JM-BIBLE-425 | Review Case Model | accepted | current | [`15-professional-validation/425-review-case-model.md`](../15-professional-validation/425-review-case-model.md) |
| JM-BIBLE-426 | Review Package Contract | accepted | current | [`15-professional-validation/426-review-package-contract.md`](../15-professional-validation/426-review-package-contract.md) |
| JM-BIBLE-427 | Review Checklist Model | accepted | current | [`15-professional-validation/427-review-checklist-model.md`](../15-professional-validation/427-review-checklist-model.md) |
| JM-BIBLE-428 | Review Observation Model | accepted | current | [`15-professional-validation/428-review-observation-model.md`](../15-professional-validation/428-review-observation-model.md) |
| JM-BIBLE-429 | Severity and Finding Classification | accepted | current | [`15-professional-validation/429-severity-and-finding-classification.md`](../15-professional-validation/429-severity-and-finding-classification.md) |
| JM-BIBLE-430 | Professional Disagreement Model | accepted | current | [`15-professional-validation/430-professional-disagreement-model.md`](../15-professional-validation/430-professional-disagreement-model.md) |
| JM-BIBLE-431 | Conditional Acceptance Model | accepted | current | [`15-professional-validation/431-conditional-acceptance-model.md`](../15-professional-validation/431-conditional-acceptance-model.md) |
| JM-BIBLE-432 | Validation Versioning | accepted | current | [`15-professional-validation/432-validation-versioning.md`](../15-professional-validation/432-validation-versioning.md) |
| JM-BIBLE-433 | Validation Expiration and Revalidation | accepted | current | [`15-professional-validation/433-validation-expiration-and-revalidation.md`](../15-professional-validation/433-validation-expiration-and-revalidation.md) |
| JM-BIBLE-434 | Implementation Change Impact | accepted | current | [`15-professional-validation/434-implementation-change-impact.md`](../15-professional-validation/434-implementation-change-impact.md) |
| JM-BIBLE-435 | Validation to Forge Workflow | accepted | current | [`15-professional-validation/435-validation-to-forge-workflow.md`](../15-professional-validation/435-validation-to-forge-workflow.md) |
| JM-BIBLE-436 | Validation to Atlas Workflow | accepted | current | [`15-professional-validation/436-validation-to-atlas-workflow.md`](../15-professional-validation/436-validation-to-atlas-workflow.md) |
| JM-BIBLE-437 | Validation to Product Workflow | accepted | current | [`15-professional-validation/437-validation-to-product-workflow.md`](../15-professional-validation/437-validation-to-product-workflow.md) |
| JM-BIBLE-438 | Professional Review Audit Trail | accepted | current | [`15-professional-validation/438-professional-review-audit-trail.md`](../15-professional-validation/438-professional-review-audit-trail.md) |
| JM-BIBLE-439 | Reviewer Independence and Conflicts | accepted | current | [`15-professional-validation/439-reviewer-independence-and-conflicts.md`](../15-professional-validation/439-reviewer-independence-and-conflicts.md) |
| JM-BIBLE-440 | Evidence Quality Model | accepted | current | [`15-professional-validation/440-evidence-quality-model.md`](../15-professional-validation/440-evidence-quality-model.md) |
| JM-BIBLE-441 | Review Sampling Strategy | accepted | current | [`15-professional-validation/441-review-sampling-strategy.md`](../15-professional-validation/441-review-sampling-strategy.md) |
| JM-BIBLE-442 | Golden Review Models | accepted | current | [`15-professional-validation/442-golden-review-models.md`](../15-professional-validation/442-golden-review-models.md) |
| JM-BIBLE-443 | Current Preliminary Rule Review Plan | accepted | current | [`15-professional-validation/443-current-preliminary-rule-review-plan.md`](../15-professional-validation/443-current-preliminary-rule-review-plan.md) |
| JM-BIBLE-444 | Current Solitaire Review Plan | accepted | current | [`15-professional-validation/444-current-solitaire-review-plan.md`](../15-professional-validation/444-current-solitaire-review-plan.md) |
| JM-BIBLE-445 | Professional Validation Register (Sprint 13) | accepted | current | [`15-professional-validation/445-professional-validation-register.md`](../15-professional-validation/445-professional-validation-register.md) |
| JM-BIBLE-446 | Review Package Generation | accepted | current | [`15-professional-validation/446-review-package-generation.md`](../15-professional-validation/446-review-package-generation.md) |
| JM-BIBLE-447 | Studio Professional Review Mode | accepted | current | [`15-professional-validation/447-studio-professional-review-mode.md`](../15-professional-validation/447-studio-professional-review-mode.md) |
| JM-BIBLE-448 | Validation Security and Privacy | accepted | current | [`15-professional-validation/448-validation-security-and-privacy.md`](../15-professional-validation/448-validation-security-and-privacy.md) |
| JM-BIBLE-449 | Validation Evaluation Framework | accepted | current | [`15-professional-validation/449-validation-evaluation-framework.md`](../15-professional-validation/449-validation-evaluation-framework.md) |
| JM-BIBLE-450 | Current Code Mapping (Professional Validation) | accepted | current | [`15-professional-validation/450-current-code-mapping.md`](../15-professional-validation/450-current-code-mapping.md) |
| JM-BIBLE-451 | Validation Gap Analysis | accepted | current | [`15-professional-validation/451-validation-gap-analysis.md`](../15-professional-validation/451-validation-gap-analysis.md) |
| JM-BIBLE-452 | Open Professional Validation Questions | accepted | current | [`15-professional-validation/452-open-professional-validation-questions.md`](../15-professional-validation/452-open-professional-validation-questions.md) |
| JM-BIBLE-SPRINT13-REPORT | Sprint 13 Validation Report | accepted | current | [`15-professional-validation/SPRINT-13-VALIDATION-REPORT.md`](../15-professional-validation/SPRINT-13-VALIDATION-REPORT.md) |
| JM-BIBLE-A81 | Appendix: Professional Reviewer Role Catalog | accepted | current | [`appendices/professional-reviewer-role-catalog.md`](professional-reviewer-role-catalog.md) |
| JM-BIBLE-A82 | Appendix: Professional Validation Object Catalog | accepted | current | [`appendices/professional-validation-object-catalog.md`](professional-validation-object-catalog.md) |
| JM-BIBLE-A83 | Appendix: Professional Review Checklist Catalog | accepted | current | [`appendices/professional-review-checklist-catalog.md`](professional-review-checklist-catalog.md) |
| JM-BIBLE-A84 | Appendix: Professional Validation Decision Catalog | accepted | current | [`appendices/professional-validation-decision-catalog.md`](professional-validation-decision-catalog.md) |
| JM-BIBLE-A85 | Appendix: Professional Finding Catalog | accepted | current | [`appendices/professional-finding-catalog.md`](professional-finding-catalog.md) |
| JM-BIBLE-A86 | Appendix: Professional Validation Status Matrix | accepted | current | [`appendices/professional-validation-status-matrix.md`](professional-validation-status-matrix.md) |
| JM-BIBLE-A87 | Appendix: Professional Rule Review Matrix | accepted | current | [`appendices/professional-rule-review-matrix.md`](professional-rule-review-matrix.md) |
| JM-BIBLE-A88 | Appendix: Professional Geometry Review Matrix | accepted | current | [`appendices/professional-geometry-review-matrix.md`](professional-geometry-review-matrix.md) |
| JM-BIBLE-A89 | Appendix: Professional Evidence Catalog | accepted | current | [`appendices/professional-evidence-catalog.md`](professional-evidence-catalog.md) |
| JM-BIBLE-A90 | Appendix: Professional Code Mapping | accepted | current | [`appendices/professional-code-mapping.md`](professional-code-mapping.md) |
| JM-BIBLE-A91 | Appendix: Professional Test Matrix | accepted | current | [`appendices/professional-test-matrix.md`](professional-test-matrix.md) |

## Machine-readable Professional Validation specification — `specs/professional-validation/v1/`

| File | Normative? | Path |
|---|---|---|
| Overview | — | [`specs/professional-validation/v1/README.md`](../../../specs/professional-validation/v1/README.md) |
| Schemas (10 JSON Schemas covering validation record/target/scope/reviewer/qualification/evidence/decision/case/package/disagreement models) | Yes | [`specs/professional-validation/v1/`](../../../specs/professional-validation/v1/) |
| Active validation registry (currently empty — zero records) | Yes | [`specs/professional-validation/v1/current-validation-registry.json`](../../../specs/professional-validation/v1/current-validation-registry.json) |
| Example/template records (5) | Yes | [`specs/professional-validation/v1/examples/`](../../../specs/professional-validation/v1/examples/) |
| Test vectors (6 files) | Yes | [`specs/professional-validation/v1/test-vectors/`](../../../specs/professional-validation/v1/test-vectors/) |

## Machine-readable Studio specification — `specs/studio/v1/`

| File | Normative? | Path |
|---|---|---|
| Overview | — | [`specs/studio/v1/README.md`](../../../specs/studio/v1/README.md) |
| Studio state schema | Yes | [`specs/studio/v1/studio-state.schema.json`](../../../specs/studio/v1/studio-state.schema.json) |
| Project session schema | Yes | [`specs/studio/v1/project-session.schema.json`](../../../specs/studio/v1/project-session.schema.json) |
| Generation state schema | Yes | [`specs/studio/v1/generation-state.schema.json`](../../../specs/studio/v1/generation-state.schema.json) |
| Output state schema | Yes | [`specs/studio/v1/output-state.schema.json`](../../../specs/studio/v1/output-state.schema.json) |
| Notification schema | Yes | [`specs/studio/v1/notification.schema.json`](../../../specs/studio/v1/notification.schema.json) |
| Examples (real, generated) | Yes | [`specs/studio/v1/examples/`](../../../specs/studio/v1/examples/) |
| Test vectors | Yes | [`specs/studio/v1/test-vectors/`](../../../specs/studio/v1/test-vectors/) |

## Machine-readable Vision specification — `specs/vision/v1/`

| File | Normative? | Path |
|---|---|---|
| Overview | — | [`specs/vision/v1/README.md`](../../../specs/vision/v1/README.md) |
| Scene state schema | Yes | [`specs/vision/v1/scene-state.schema.json`](../../../specs/vision/v1/scene-state.schema.json) |
| Camera state schema | Yes | [`specs/vision/v1/camera-state.schema.json`](../../../specs/vision/v1/camera-state.schema.json) |
| Component visual state schema | Yes | [`specs/vision/v1/component-visual-state.schema.json`](../../../specs/vision/v1/component-visual-state.schema.json) |
| Material presentation schema | Yes | [`specs/vision/v1/material-presentation.schema.json`](../../../specs/vision/v1/material-presentation.schema.json) |
| Render result schema | Yes | [`specs/vision/v1/render-result.schema.json`](../../../specs/vision/v1/render-result.schema.json) |
| Image capture request schema | Yes | [`specs/vision/v1/image-capture-request.schema.json`](../../../specs/vision/v1/image-capture-request.schema.json) |
| Examples (real, generated) | Yes | [`specs/vision/v1/examples/`](../../../specs/vision/v1/examples/) |
| Test vectors | Yes | [`specs/vision/v1/test-vectors/`](../../../specs/vision/v1/test-vectors/) |

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

## Machine-readable Designer specification — `specs/designer/v1/`

| File | Normative? | Path |
|---|---|---|
| Overview | — | [`specs/designer/v1/README.md`](../../../specs/designer/v1/README.md) |
| Natural-language request schema | Yes | [`specs/designer/v1/natural-language-request.schema.json`](../../../specs/designer/v1/natural-language-request.schema.json) |
| Proposed field schema | Yes | [`specs/designer/v1/proposed-field.schema.json`](../../../specs/designer/v1/proposed-field.schema.json) |
| Clarification question schema | Yes | [`specs/designer/v1/clarification-question.schema.json`](../../../specs/designer/v1/clarification-question.schema.json) |
| Unsupported feature schema | Yes | [`specs/designer/v1/unsupported-feature.schema.json`](../../../specs/designer/v1/unsupported-feature.schema.json) |
| Designer diagnostic schema | Yes | [`specs/designer/v1/designer-diagnostic.schema.json`](../../../specs/designer/v1/designer-diagnostic.schema.json) |
| Design proposal schema | Yes | [`specs/designer/v1/design-proposal.schema.json`](../../../specs/designer/v1/design-proposal.schema.json) |
| Designer result schema | Yes | [`specs/designer/v1/designer-result.schema.json`](../../../specs/designer/v1/designer-result.schema.json) |
| Examples (real, generated) | Yes | [`specs/designer/v1/examples/`](../../../specs/designer/v1/examples/) |
| Test vectors | Yes | [`specs/designer/v1/test-vectors/`](../../../specs/designer/v1/test-vectors/) |

## Machine-readable Design Intent specification — `specs/design-intent/v1/`

| File | Normative? | Path |
|---|---|---|
| Overview | — | [`specs/design-intent/v1/README.md`](../../../specs/design-intent/v1/README.md) |
| Intent target schema | Yes | [`specs/design-intent/v1/intent-target.schema.json`](../../../specs/design-intent/v1/intent-target.schema.json) |
| Intent statement schema | Yes | [`specs/design-intent/v1/intent-statement.schema.json`](../../../specs/design-intent/v1/intent-statement.schema.json) |
| Intent relation schema | Yes | [`specs/design-intent/v1/intent-relation.schema.json`](../../../specs/design-intent/v1/intent-relation.schema.json) |
| Intent diagnostic schema | Yes | [`specs/design-intent/v1/intent-diagnostic.schema.json`](../../../specs/design-intent/v1/intent-diagnostic.schema.json) |
| Intent resolution schema | Yes | [`specs/design-intent/v1/intent-resolution.schema.json`](../../../specs/design-intent/v1/intent-resolution.schema.json) |
| Intent profile schema | Yes | [`specs/design-intent/v1/intent-profile.schema.json`](../../../specs/design-intent/v1/intent-profile.schema.json) |
| Design intent schema | Yes | [`specs/design-intent/v1/design-intent.schema.json`](../../../specs/design-intent/v1/design-intent.schema.json) |
| Controlled vocabulary source of truth | Yes | [`specs/design-intent/v1/vocabulary.json`](../../../specs/design-intent/v1/vocabulary.json) |
| Examples (real, generated) | Yes | [`specs/design-intent/v1/examples/`](../../../specs/design-intent/v1/examples/) |
| Test vectors | Yes | [`specs/design-intent/v1/test-vectors/`](../../../specs/design-intent/v1/test-vectors/) |

## Machine-readable Conversation specification — `specs/conversation/v1/`

| File | Normative? | Path |
|---|---|---|
| Overview | — | [`specs/conversation/v1/README.md`](../../../specs/conversation/v1/README.md) |
| Conversation action schema | Yes | [`specs/conversation/v1/conversation-action.schema.json`](../../../specs/conversation/v1/conversation-action.schema.json) |
| Clarification thread schema | Yes | [`specs/conversation/v1/clarification-thread.schema.json`](../../../specs/conversation/v1/clarification-thread.schema.json) |
| Clarification answer schema | Yes | [`specs/conversation/v1/clarification-answer.schema.json`](../../../specs/conversation/v1/clarification-answer.schema.json) |
| Conversation state schema | Yes | [`specs/conversation/v1/conversation-state.schema.json`](../../../specs/conversation/v1/conversation-state.schema.json) |
| Turn context schema | Yes | [`specs/conversation/v1/turn-context.schema.json`](../../../specs/conversation/v1/turn-context.schema.json) |
| Conversation turn schema | Yes | [`specs/conversation/v1/conversation-turn.schema.json`](../../../specs/conversation/v1/conversation-turn.schema.json) |
| Conversation summary schema | Yes | [`specs/conversation/v1/conversation-summary.schema.json`](../../../specs/conversation/v1/conversation-summary.schema.json) |
| Conversation session schema | Yes | [`specs/conversation/v1/conversation-session.schema.json`](../../../specs/conversation/v1/conversation-session.schema.json) |
| Conversation result schema | Yes | [`specs/conversation/v1/conversation-result.schema.json`](../../../specs/conversation/v1/conversation-result.schema.json) |
| Examples (real, generated) | Yes | [`specs/conversation/v1/examples/`](../../../specs/conversation/v1/examples/) |
| Test vectors | Yes | [`specs/conversation/v1/test-vectors/`](../../../specs/conversation/v1/test-vectors/) |

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
