---
id: JM-BIBLE-138
title: Component Naming and Identity
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-131
related_documents: []
implementation_status: current
professional_validation: not_required
normative: true
---

# Component Naming and Identity

## Canonical current component names, exactly as they appear in code

`"band"`, `"stone_reference"`, `"prongs"`, `"basket_support"` — the literal dict keys in `GeneratedModel.components` (`solitaire.py::build_solitaire_ring`) and the literal `name=` argument passed to `GeneratedComponent` in each builder. These are also the literal filenames used for preview STL export (`{name}.stl`, `preview/mesh.py::_component_filename`).

## Persistent conceptual identity vs. generated instance identity

- **Persistent conceptual identity**: the four names above are fixed identifiers for "the band of a solitaire ring," "the stone reference," etc. — stable across every generation of every solitaire, regardless of parameter values.
- **Generated instance identity**: a specific `GeneratedComponent` instance, tied to one `definitionHash`. Two different definitions produce two different component instances with the same conceptual name (`"band"`) but different geometry.
- **Component index**: not applicable at the top level — there is no numeric index for `band`/`stone_reference`/`basket_support` (exactly one of each always exists). It only becomes relevant for prongs (below).

## Prong identity — actual current behavior, before proposing anything

**Individual prongs have no persistent name or identity today.** `build_prongs()` returns a single `GeneratedComponent` named `"prongs"` whose `shape` is one `cq.Compound` containing N unnamed solids, and whose `metadata["positions"]` is a plain list of `{x, y}` dicts with no accompanying index-to-solid mapping guarantee beyond list order. There is no `prong_0`, `prong_1`, ... identity anywhere in the current codebase — this is a conceptual naming scheme this document considers for a *future* per-prong identity model, not a description of anything implemented.

If per-prong identity were introduced in the future, `prong_0`, `prong_1`, ... (matching `_prong_positions()`'s index order, which is itself deterministic — see [`123-coordinate-system-and-orientation.md`](123-coordinate-system-and-orientation.md)) would be the natural, already-deterministic basis for it, since `_prong_positions()` always returns positions in the same `i=0..count-1` order for a given count. This is recorded as open question `ATLAS-OQ-005` in [`151-open-atlas-questions.md`](151-open-atlas-questions.md), not implemented here.

## Deterministic naming

All current naming is deterministic: the same four component names are produced every time, in the same dict-insertion order (`band`, `stone_reference`, `prongs`, `basket_support`, per `solitaire.py`'s literal dict construction), for every valid definition.
