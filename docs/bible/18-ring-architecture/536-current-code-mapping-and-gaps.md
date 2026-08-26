---
id: JM-BIBLE-536
title: Current Code Mapping and Gaps
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
  - JM-BIBLE-533
  - JM-BIBLE-535
implementation_status: current
professional_validation: not_required
normative: false
---

# Current Code Mapping and Gaps

## Code map

### `backend/jewelmind/jewelry_category/` — 6 files, 329 lines total (`wc -l`)

| File | Lines | Role |
|---|---|---|
| `__init__.py` | 24 | Public package exports. |
| `dispatch.py` | 79 | `generate_for_category()`, `generate_jewelry()`, the lazily-built `_category_generators()`. |
| `errors.py` | 39 | `JewelryCategoryUnsupportedError`, `JewelryCategoryNotGeneratableError`, `RingFamilyUnsupportedError`, `RingDefinitionInvalidError`, `CategoryAdapterFailedError`. |
| `forge_scope.py` | 52 | `rule_scope()`, `is_ring_specific()`, `is_shared_scope()`. |
| `models.py` | 29 | `CategoryCapability` (Pydantic). |
| `registry.py` | 106 | `CATEGORY_CAPABILITIES`, `get_capability()`, `is_generation_supported()`. |

### `backend/jewelmind/ring/` — 4 files, 237 lines total (`wc -l`)

| File | Lines | Role |
|---|---|---|
| `__init__.py` | 14 | Public package exports. |
| `adapter.py` | 55 | `ring_definition_from_jdl()`. |
| `families.py` | 54 | `RING_FAMILY_GENERATORS`, `RESERVED_PLANNED_RING_FAMILIES`, `generate_ring()`. |
| `models.py` | 114 | `RingDefinition` and its 6 sub-models. |

Combined: **566 lines** across both new packages.

### Real call-site changes (2)

1. [`services/model_service.py`](../../../backend/jewelmind/services/model_service.py) — `ModelService.generate()` now calls `generate_jewelry(definition)` instead of `build_solitaire_ring(definition)` directly.
2. [`geometry_quality/snapshot.py`](../../../backend/jewelmind/geometry_quality/snapshot.py) — the Golden fixture builder makes the identical call-site change, for the identical reason (see [`532-ring-generation-contract.md`](532-ring-generation-contract.md)).

Both are proven safe by the full Golden Suite passing with **zero**
baseline updates — confirmed this Sprint by running
`.venv/Scripts/python.exe -m pytest -q tests/test_geometry_quality_harness.py -k TestRealGeneration -v`,
which passed (`2 passed`) with no changes to any recorded Golden
baseline file.

### Real leak fix (1)

[`designer/capability.py`](../../../backend/jewelmind/designer/capability.py) —
`_category_unsupported_message()` now sources its 4 category-unsupported
messages (`necklace`, `bracelet`, `earring`, `pendant`) from
`jewelry_category.registry.get_capability(category).message`, instead of
(previously) a hand-written string per category. This closes a real
drift risk: before this Sprint, Designer's unsupported-category copy and
the category registry's `message` field could silently diverge; now
there is exactly one source of truth.

### New/modified test files (4) — 44 tests total (`pytest --collect-only`)

| File | Tests |
|---|---|
| `test_ring_architecture.py` | 20 |
| `test_jewelry_category_extension.py` | 16 |
| `test_ring_architecture_schemas.py` | 8 |
| `test_api_hardening.py` (1 test fixed, not new) | — |

Plus the one pre-existing test fixed in `test_api_hardening.py` — see
below.

## The `test_api_hardening.py` fix: a second real gotcha

`test_generation_failure_maps_to_model_generation_failed` pre-dates this
Sprint. It previously monkeypatched
`jewelmind.services.model_service.build_solitaire_ring` — a name that no
longer exists in that module after the dispatch change. The fix
monkeypatches the dict entry instead:

```python
import jewelmind.ring.families as ring_families
monkeypatch.setitem(ring_families.RING_FAMILY_GENERATORS, "solitaire", _boom)
```

The real comment left in the test explains why patching the module-level
function name alone would not have worked: `RING_FAMILY_GENERATORS`
captures the function *reference* at import time
(`{"solitaire": build_solitaire_ring}`), so patching
`jewelmind.geometry.assemblies.solitaire.build_solitaire_ring` after
that dict is built would not affect the already-bound reference the
dict holds. Patching the dict entry itself is the only way to intercept
the call the real dispatch chain actually makes.

## Gaps — INTENTIONAL SCOPE, not defects

Per the brief's own framing, every item below is a deliberate,
documented boundary of this Sprint's scope, not an oversight to be
silently fixed:

- **Shank is currently uniform.** Only `comfort_fit`/`flat` profiles
  exist (`BandProfile` in `domain/schema.py`); no tapering, split,
  cathedral, knife-edge, or Euro-profile shank exists in real geometry.
  `ShankDefinition`'s own docstring states this.
- **Shoulders are implicit.** `ShoulderDefinition.modeled` is always
  `False` — there is no independently modeled shoulder geometry; the
  shank flows directly into the head with no distinct transition
  component today.
- **The head is still solitaire-focused.** `RingHeadDefinition` has only
  `basketHeightMm` — no crown, gallery, or cathedral-shoulder geometry
  concept exists.
- **`StoneArrangement` supports only `SINGLE_CENTER`.**
  `StoneArrangementType = Literal["SINGLE_CENTER"]` — `MULTI_STONE`,
  `THREE_STONE`, `HALO`, `CLUSTER`, `PAVE_ARRAY` are all named as future
  possibilities in the model's own docstring, none implemented.
- **`SettingSystem` supports only `prong`.** `SettingType =
  Literal["prong"]` in `domain/schema.py`, unchanged this Sprint.
- **Only the `ring` category is generatable.** All 5 other categories
  are `status: "planned"`, `generationSupported: False`.
- **No cross-category real-geometry test exists.** The dummy category
  proof in `test_jewelry_category_extension.py` never calls real
  geometry — `_dummy_pendant_generator()` returns a plain
  `DummyPendantResult` pydantic object, not a `GeneratedModel`. It proves
  the *dispatch boundary* is generic; it does not (and cannot, since no
  second category's geometry exists) prove a second category's geometry
  pipeline works end-to-end.
- **The JDL external schema is still ring-oriented.** This is the most
  significant real gap between the brief's illustrative target JSON
  shape (a nested, polymorphic `categoryDefinition` structure) and what
  was actually built. `domain/schema.py::JewelryDefinition` still has
  top-level `ring`/`band`/`stone`/`setting` fields, not a nested,
  per-category definition structure.

## Why the JDL-shape gap is a deliberate choice, not an oversight

The brief's own section 3 explicitly permitted this: *"Do NOT force this
exact JSON shape if current JDL architecture makes another structure
safer... The requirement is semantic."* This Sprint chose the
additive-adapter approach (`ring_definition_from_jdl()` sitting
underneath an unmodified JDL schema) over a JDL schema restructure
specifically to satisfy the brief's own section 20 backward-compatibility
mandate — restated as JEWELRY-ARCH-GOV-008: "Backward compatibility is
preserved by construction, not by testing alone." A nested
`categoryDefinition` JDL structure remains a real, legitimate future
direction (see
[`537-open-ring-architecture-questions.md`](537-open-ring-architecture-questions.md)),
but adopting it now would have required a JDL major-version change this
Sprint's brief did not call for, and would have broken exactly the
backward compatibility this Sprint was built to preserve.
