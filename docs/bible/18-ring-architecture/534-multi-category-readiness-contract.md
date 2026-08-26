---
id: JM-BIBLE-534
title: Multi-Category Readiness Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-RING-README
  - JM-BIBLE-520
related_documents:
  - JM-BIBLE-535
  - JM-BIBLE-536
implementation_status: current
professional_validation: not_required
normative: true
---

# Multi-Category Readiness Contract

**MANDATORY.** This document defines the acceptance criteria a future
jewelry category (earring, pendant, bracelet, necklace, charm) must
satisfy before it can move from `status: "planned"` to `status:
"current"`, and names the real Sprint-16 mechanism each criterion would
use. None of the nine items below is implemented for any category other
than `ring` this Sprint — this document describes the path, not a
completed migration.

## The nine acceptance criteria

### 1. Category definition

A new internal, composable domain model analogous to
[`RingDefinition`](../../../backend/jewelmind/ring/models.py), in its own
package (e.g. `jewelmind.earring.models`), plus — only if genuinely
required and only through the ADR/RFC process
([`520-jewelry-category-architecture.md`](520-jewelry-category-architecture.md)) —
new fields on `domain/schema.py::JewelryDefinition` gated by
JEWELRY-ARCH-GOV-004/008. `jewelmind.ring.models.RingDefinition` is the
real, working example this Sprint built to prove the pattern.

### 2. Category capability registration

Add one entry to
[`jewelry_category/registry.py::CATEGORY_CAPABILITIES`](../../../backend/jewelmind/jewelry_category/registry.py)
with `status="current"`, `generationSupported=True`, and the category's
real `supportedFamilies`/`sharedSystems`/`categorySpecificSystems` —
mirroring the existing `ring` entry. Every other category stays
`planned` / `generationSupported=False` until this happens
(JEWELRY-ARCH-GOV-003). `specs/jewelry-architecture/v1/category-registry.json`
is regenerated from this dict, never hand-edited
(JEWELRY-ARCH-GOV-015).

### 3. Category validator

Extend `validate_definition()`
([`validation/engine.py`](../../../backend/jewelmind/validation/engine.py))
with the category's real business rules, each carrying a new
`JM-<CATEGORY>-*` rule-ID prefix. That new prefix needs one new entry in
`jewelry_category/forge_scope.py::_SCOPE_BY_PREFIX` so
`rule_scope()`/`is_ring_specific()`/`is_shared_scope()` classify it
correctly — never a second validation engine, and never a rule scope
hand-duplicated per category (JEWELRY-ARCH-GOV-012).

### 4. Category generator

Register the category's real generator function in the dict returned by
[`jewelry_category/dispatch.py::_category_generators()`](../../../backend/jewelmind/jewelry_category/dispatch.py)
(currently `{"ring": generate_ring}`). The cross-package import must stay
deferred inside that lazily-evaluated, cached function — the exact
pattern that avoided the real circular-import bug documented in
[`532-ring-generation-contract.md`](532-ring-generation-contract.md); a
future category generator's own package should defer its import into
`jewelmind.jewelry_category` the same way `jewelmind.ring` does, to avoid
the identical class of bug.

### 5. Category-specific Forge rules

New rule IDs with the category's own domain prefix (e.g.
`JM-EARRING-*`), added to `validation/rules.py`/`validation/engine.py`
exactly like the existing `JM-RING-*`/`JM-BAND-*`/`JM-SETTING-*` rules —
same provenance-declaration and blocking-scope requirements as every
other Forge rule (see
[`../06-forge/090-forge-governance.md`](../06-forge/090-forge-governance.md)).
This Sprint's forge-scope classification work (item 3) is what makes
these rules distinguishable from ring-specific ones without a rewrite.

### 6. Optional category inspector

If the category's real geometry benefits from structural inspection, a
new module under
[`geometry/inspection/`](../../../backend/jewelmind/geometry/inspection/)
consuming that geometry the same way
[`inspector.py::inspect_model()`](../../../backend/jewelmind/geometry/inspection/inspector.py)
already does for rings — see
[`../16-geometry-inspection/README.md`](../16-geometry-inspection/README.md).
This is explicitly optional per that Sprint's own governance; nothing
about category addition forces it.

### 7. Studio editor

A new UI surface under `frontend/src/studio/`, following the pattern of
`ConfigurationPanel.tsx`, gated by the category's real
`CategoryCapability` (item 2) rather than assuming every definition has
ring fields — restating STUDIO-GOV-011's controlled-terminology rule
(never expose "Forge"/"Atlas"/"Alchemist"/"Foundry"/"Vision" in
user-facing copy) at the category-selection layer too.

### 8. Designer capability declaration

[`designer/capability.py`](../../../backend/jewelmind/designer/capability.py)'s
existing `_category_unsupported_message()` function already sources its
message from the real registry via `get_capability(category)` — see the
real leak fix documented in
[`536-current-code-mapping-and-gaps.md`](536-current-code-mapping-and-gaps.md).
Flipping a category from planned to current in step 2 above requires
**zero** additional Designer code change: the message and unsupported
status flip automatically because Designer reads the same
`CATEGORY_CAPABILITIES` dict, never a second, hand-maintained copy.

### 9. Golden suite

New Golden fixture(s) for the category, generated through
`generate_jewelry()` exactly like every solitaire fixture today, and
verified through `verify_all_goldens()` — see
[`../17-geometry-quality/README.md`](../17-geometry-quality/README.md)
and [`../17-geometry-quality/500-quality-governance.md`](../17-geometry-quality/500-quality-governance.md).
QUALITY-GOV-003/004/016/017 (never silently re-baseline; review and
accept, or fix) apply unchanged to a new category's fixtures.

## Platform-level systems that must never need rewriting

Per JEWELRY-ARCH-GOV-016, the following are all designed to accept a new
category through capability/generator registration alone (items 1-9
above), never a rewrite of the system itself:

- JDL infrastructure (`domain/schema.py`, `specs/jdl/v1/`)
- Forge engine (`validation/engine.py`, `specs/forge/v1/`)
- Alchemist orchestration (`services/model_service.py` sequencing)
- Atlas core (`geometry/`)
- Foundry (`exporters/`)
- Vision core (`frontend/src/vision/`, `ModelViewport.tsx`)
- Designer core (`designer/`)
- Conversation core (`conversation/`)
- Professional Validation (`professional_validation/`)
- Geometry Quality (`geometry_quality/`)

This Sprint did not test every one of these ten systems against a real
non-ring category (none is implemented) — the guarantee rests on the
architectural boundary these nine acceptance criteria describe, verified
this Sprint only for the platform-level dispatch/capability machinery
itself (`test_jewelry_category_extension.py`'s dummy-category proof —
see [`535-category-extension-test-model.md`](535-category-extension-test-model.md)),
not for a full second category's worth of Studio/Designer/Vision/Foundry
code. Treat this as a structural claim about the boundary, not an
empirical claim about a second category having actually been built and
exercised end-to-end.
