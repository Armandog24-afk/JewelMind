---
id: JM-BIBLE-100
title: Rule Dependencies and Ordering
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-24
source_of_truth: true
depends_on:
  - JM-BIBLE-096
related_documents:
  - JM-BIBLE-A18
implementation_status: current
professional_validation: not_required
normative: true
---

# Rule Dependencies and Ordering

## Current evaluation order (fixed, not configurable)

`_RULE_GROUPS` in `backend/jewelmind/validation/engine.py` runs, in this exact order: ring rules, band rules, stone rules, prong rules, setting rules, manufacturing rules, geometry rules. This order is **stable and deterministic** — the same input always produces results in the same order — but it is not derived from any dependency graph; it simply mirrors the order fields appear in `JewelryDefinition`.

## Real dependency example

`JM-PRONG-003` ("stones larger than 8mm are typically more secure with six prongs") fires exactly when `stone.diameter > 8 and setting.prongCount == 4` (`backend/jewelmind/validation/engine.py::_prong_rules`). It reads the same `setting.prongCount` field `JM-PRONG-001` (the `{4, 6}` set-membership rule) reads, but does **not** actually depend on `JM-PRONG-001` having passed — both rules independently evaluate `prongCount` and can both fire on the same document (e.g. `prongCount: 4, stone.diameter: 9` fires only `JM-PRONG-003`; `prongCount: 5` fires only `JM-PRONG-001`, since 5 also fails `JM-PRONG-003`'s `== 4` check). `current-rule-registry.json` still lists `JM-PRONG-001` as a documentation-only dependency of `JM-PRONG-003` — a reader evaluating why `JM-PRONG-003` did or didn't fire benefits from knowing `JM-PRONG-001`'s outcome for context — not because the engine enforces or requires that ordering.

## Priority: stage + dependency, not arbitrary numbers

Per this Sprint's explicit preference, rule ordering is expressed as `stage` (`FORGE-0`..`FORGE-9`, see [`096-rule-evaluation-pipeline.md`](096-rule-evaluation-pipeline.md)) plus an optional `dependencies` list — never an arbitrary numeric priority field. This matches how `current-rule-registry.json` is structured: every rule declares a `stage`, and only `JM-PRONG-003` declares a `dependencies` entry.

## Short-circuit behavior

**None exists for rule evaluation itself.** As stated in [`096-rule-evaluation-pipeline.md`](096-rule-evaluation-pipeline.md), `validate_definition()` always evaluates every rule group to completion regardless of earlier errors — an `error` in `_ring_rules` does not skip `_band_rules`. Short-circuiting only happens **after** all rules have run, at the `has_errors()` gate before geometry generation (FORGE-6).

## When geometry rules cannot run because geometry does not exist

`GEOMETRY_INSPECTION`-category rules (currently only `FORGE-GEOM-001`) structurally cannot run before FORGE-6 has produced a `GeneratedModel` — there is no code path that attempts to evaluate them earlier, since `_fuse_metal()` is only ever called from inside `build_solitaire_ring()`. This is enforced by the pipeline's data dependency (the rule's implementation literally needs the fused shape as an argument), not by an explicit "skip if geometry absent" check.
