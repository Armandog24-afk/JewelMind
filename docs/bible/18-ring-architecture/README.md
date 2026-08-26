---
id: JM-BIBLE-RING-README
title: Ring Architecture v2 / Multi-Category Ready — Index
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-040
  - JM-BIBLE-120
related_documents:
  - JM-BIBLE-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Ring Architecture v2 / Multi-Category Ready — Index

This is **Sprint 16** of the Technical Bible: **Ring Architecture v2 / Multi-Category Ready**. The current solitaire was JewelMind's first vertical slice — a real, working implementation — but its own code and JDL schema conflated three distinct concepts: the platform (JewelMind), one product category (a ring), and one ring style/family (a solitaire). This Sprint formalizes the boundary between them so a future jewelry category — earrings, pendants, bracelets, necklaces, charms — can be added without rewriting the engine, **without implementing any of them**.

**Read this README, then [`520-jewelry-category-architecture.md`](520-jewelry-category-architecture.md), before changing anything in `backend/jewelmind/jewelry_category/`, `backend/jewelmind/ring/`, or how `ModelService.generate()` dispatches geometry generation.**

## The fundamental rule

> JewelMind ≠ RingEngine. Ring is one jewelry category, composed from reusable domain concepts, not the platform's architectural root.

```
JewelMind
  → JewelryCategory        (ring: CURRENT; earring/pendant/bracelet/necklace/charm: PLANNED)
    → RingDefinition v2    (composed, not monolithic)
      → RingFamily          (solitaire: CURRENT; 7 reserved families: PLANNED)
        → geometry builders (Sprint 5's Atlas — UNCHANGED this Sprint)
```

## What changed vs. what didn't

**Changed (architecture only):** `ModelService.generate()` now dispatches through `jewelmind.jewelry_category.dispatch.generate_jewelry()` instead of calling `build_solitaire_ring()` directly. A real `RingDefinition` v2 internal model is now built (and validated) from every real JDL definition on every generation, via `jewelmind.ring.adapter.ring_definition_from_jdl()`.

**Unchanged (by design, verified by the Golden Suite):** The real geometry-producing function is still `build_solitaire_ring()`, called with the exact same `JewelryDefinition` it always was. The current JDL schema (`domain/schema.py`) was not modified. Zero Golden baseline updates were required — see [`SPRINT-16-VALIDATION-REPORT.md`](SPRINT-16-VALIDATION-REPORT.md).

## Reading order

1. [`520-jewelry-category-architecture.md`](520-jewelry-category-architecture.md) — the governing rules (JEWELRY-ARCH-GOV-001 through N).
2. [`521-shared-vs-category-specific-domain.md`](521-shared-vs-category-specific-domain.md) — the audit this Sprint's design is built on.
3. Ring category: [`522-ring-architecture-overview.md`](522-ring-architecture-overview.md), [`523-ring-definition-model.md`](523-ring-definition-model.md), [`524-ring-family-model.md`](524-ring-family-model.md).
4. Ring sub-domains: [`525-ring-sizing-contract.md`](525-ring-sizing-contract.md), [`526-shank-contract.md`](526-shank-contract.md), [`527-shoulder-contract.md`](527-shoulder-contract.md), [`528-head-contract.md`](528-head-contract.md), [`529-stone-arrangement-contract.md`](529-stone-arrangement-contract.md), [`530-setting-attachment-contract.md`](530-setting-attachment-contract.md).
5. Composition and generation: [`531-ring-component-graph.md`](531-ring-component-graph.md), [`532-ring-generation-contract.md`](532-ring-generation-contract.md).
6. Migration: [`533-solitaire-migration-model.md`](533-solitaire-migration-model.md).
7. Multi-category readiness: [`534-multi-category-readiness-contract.md`](534-multi-category-readiness-contract.md), [`535-category-extension-test-model.md`](535-category-extension-test-model.md).
8. [`536-current-code-mapping-and-gaps.md`](536-current-code-mapping-and-gaps.md), [`537-open-ring-architecture-questions.md`](537-open-ring-architecture-questions.md).

## Appendices

[`jewelry-category-catalog.md`](../appendices/jewelry-category-catalog.md), [`ring-component-catalog.md`](../appendices/ring-component-catalog.md), [`ring-family-catalog.md`](../appendices/ring-family-catalog.md), [`shared-jewelry-system-catalog.md`](../appendices/shared-jewelry-system-catalog.md), [`ring-architecture-test-matrix.md`](../appendices/ring-architecture-test-matrix.md).

## Machine-readable specification

[`specs/jewelry-architecture/v1/`](../../../specs/jewelry-architecture/v1/README.md) (platform-level category identity/capability) and [`specs/ring/v2/`](../../../specs/ring/v2/README.md) (Ring-category domain contract, underneath JDL — never a second canonical JDL schema).

## The single most important finding of this Sprint

**A generic category dispatch boundary now exists and is real, not aspirational.** `jewelmind.jewelry_category.dispatch.generate_for_category()` takes a plain category string, an arbitrary payload, and a registry — it has never heard of `ring.size` or `band.width`. `backend/tests/test_jewelry_category_extension.py` proves this with a wholly unrelated, test-only `DummyPendantDefinition` that dispatches through the exact same function `ring` uses, without that dummy category ever appearing in the real production registry, Designer's capabilities, or the JDL schema.

## What was investigated, not invented

Every field mapping in [`533-solitaire-migration-model.md`](533-solitaire-migration-model.md) was verified against the real `domain/schema.py` and `ring/adapter.py` source, not assumed. A real circular-import bug was found and fixed during this Sprint's own implementation (see the validation report) — `jewelmind.ring` and `jewelmind.jewelry_category` importing each other's submodules at module-load time, before either package had finished initializing. This was fixed by deferring the cross-package import until the first real dispatch call, verified empirically from both import orders, not merely reasoned about.

## Validation of this sprint

See [`SPRINT-16-VALIDATION-REPORT.md`](SPRINT-16-VALIDATION-REPORT.md) for the checks run against this section and the findings from that pass.
