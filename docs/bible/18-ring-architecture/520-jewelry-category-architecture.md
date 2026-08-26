---
id: JM-BIBLE-520
title: Jewelry Category Architecture Governance
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-RING-README
related_documents:
  - JM-BIBLE-090
  - JM-BIBLE-120
  - JM-BIBLE-460
  - JM-BIBLE-500
implementation_status: current
professional_validation: not_required
normative: true
---

# Jewelry Category Architecture Governance

16 non-negotiable rules for `backend/jewelmind/jewelry_category/` and `backend/jewelmind/ring/`. Mirrors the INSPECT-GOV/QUALITY-GOV governance pattern established in Sprints 14-15.

**JEWELRY-ARCH-GOV-001 — Ring is one jewelry category, never JewelMind's architectural root.** No module outside `jewelmind.ring`/`jewelmind.geometry`/`jewelmind.validation` (Sprint-5-and-earlier ring-specific code, unchanged this Sprint) may assume every `JewelryDefinition` has ring fields as a platform-level given.

**JEWELRY-ARCH-GOV-002 — The category dispatch boundary must stay generic.** `jewelmind.jewelry_category.dispatch.generate_for_category()` never imports or references `jewelmind.ring` at its own module-import time — only inside a lazily-evaluated function, called on first real dispatch. Verified by `backend/tests/test_jewelry_category_extension.py`.

**JEWELRY-ARCH-GOV-003 — Never advertise a `planned` category as generatable.** `CategoryCapability.generationSupported` is `False` for every category except `ring`; `generate_for_category()` raises `JewelryCategoryNotGeneratableError` before ever consulting a generator registry for a planned category.

**JEWELRY-ARCH-GOV-004 — Category-specific fields must not become global fields merely because Ring was first.** `ring.size`/`ring.innerDiameter` remain under `JewelryDefinition.ring`; a future `earring.postType` must never migrate to a shared top-level field just because `ring` did something similar.

**JEWELRY-ARCH-GOV-005 — RingHead and SettingAttachment stay separate concepts.** A setting (e.g. a prong setting) is a concept potentially reusable outside rings; how it structurally attaches to a ring is ring-specific. `RingHeadDefinition` never owns prong/setting fields; `SettingAttachmentDefinition` never owns basket-height.

**JEWELRY-ARCH-GOV-006 — StoneArrangement is a potentially shared jewelry concept, not Ring-owned data.** `StoneArrangementDefinition` wraps the existing `StoneSpec` rather than duplicating stone fields, so a future category can reuse the same stone contract without inheriting anything ring-specific.

**JEWELRY-ARCH-GOV-007 — Shared systems (material, manufacturing, stone, setting, preview) are consumed, never re-implemented, by Ring Architecture.** `RingDefinition` never defines its own `MaterialDefinition`/`ManufacturingContext` — those remain `domain/schema.py::MaterialSpec`/`ManufacturingSpec`, used as-is.

**JEWELRY-ARCH-GOV-008 — Backward compatibility is preserved by construction, not by testing alone.** The real JDL schema (`domain/schema.py`) was not modified this Sprint; `ring_definition_from_jdl()` is a pure adapter reading an unmodified `JewelryDefinition`, never a competing input format.

**JEWELRY-ARCH-GOV-009 — Geometry output must remain identical unless a change is explicitly reviewed and accepted.** `jewelmind.ring.families.generate_ring()` dispatches to the exact same, unmodified `build_solitaire_ring()` Sprint 5 built — this Sprint is an architecture change, never a geometry change (restates QUALITY-GOV-016/017 at this layer).

**JEWELRY-ARCH-GOV-010 — A planned ring family is a recognized value, never a fake implementation.** `RingFamilyId` (models.py) includes 7 reserved future families; `RING_FAMILY_GENERATORS` (families.py) registers only `solitaire`. Requesting a recognized-but-unregistered family raises `RingFamilyUnsupportedError` — never a silent fallback to solitaire.

**JEWELRY-ARCH-GOV-011 — A test-only category proves extensibility and must never reach production.** The dummy category defined in `test_jewelry_category_extension.py` is never added to `CATEGORY_CAPABILITIES`, any generator registry, Designer's capabilities, or the JDL schema — verified structurally by a real test, not merely by convention.

**JEWELRY-ARCH-GOV-012 — Forge rule scope is derived, never hand-duplicated per category.** `jewelmind.jewelry_category.forge_scope.rule_scope()` classifies a rule ID by its existing `JM-<DOMAIN>-NNN` prefix; it never introduces a second rule-ID vocabulary or modifies `validation/engine.py`.

**JEWELRY-ARCH-GOV-013 — Professional validation status is never altered by this refactor.** Sprint 13's active validation registry stays untouched; an architecture-only change is never evidence of, or grounds for changing, professional review status.

**JEWELRY-ARCH-GOV-014 — Golden baselines are never regenerated to absorb an architecture change.** If `verify_all_goldens()` reports a regression after a Ring Architecture change, the code is fixed, or the diff is reviewed and explicitly accepted — never silently re-baselined (QUALITY-GOV-003/004 apply unchanged).

**JEWELRY-ARCH-GOV-015 — Category capability is machine-readable and singly-sourced.** `specs/jewelry-architecture/v1/category-registry.json` is generated from `CATEGORY_CAPABILITIES`, never hand-maintained as a second, driftable copy; `backend/tests/test_ring_architecture_schemas.py` re-derives it live to catch drift.

**JEWELRY-ARCH-GOV-016 — A future category's requirements must never force a rewrite of platform-level systems.** JDL infrastructure, the Forge engine, Alchemist orchestration, Atlas core, Foundry, Vision core, Designer core, Conversation core, Professional Validation, and Geometry Quality are all designed to accept a new category through capability/generator registration alone — see [`534-multi-category-readiness-contract.md`](534-multi-category-readiness-contract.md).
