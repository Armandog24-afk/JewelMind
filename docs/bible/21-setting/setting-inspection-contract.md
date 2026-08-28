---
id: JM-BIBLE-588
title: Setting Inspection Contract
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-27
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-SETTING-README
  - JM-BIBLE-580
related_documents:
  - JM-BIBLE-460
  - JM-BIBLE-462
implementation_status: current
professional_validation: not_required
normative: true
---

# Setting Inspection Contract

## The 8 new fact types

Added to `geometry/inspection/models.py::FactType`, emitted by `inspector.py::_setting_facts()`:

| `FactType` | Scope | Source |
|---|---|---|
| `SETTING_TYPE` | ASSEMBLY | `SettingGeometryResult` |
| `SETTING_COMPATIBILITY_STATUS` | ASSEMBLY | `SettingGeometryResult` |
| `SETTING_COMPONENT_COUNT` | ASSEMBLY | `SettingGeometryResult` |
| `SETTING_REQUESTED_PRONG_COUNT` | ASSEMBLY | prong family only |
| `SETTING_GENERATED_PRONG_COUNT` | ASSEMBLY | prong family only |
| `SETTING_PLACEMENT_STRATEGY` | ASSEMBLY | prong family only |
| `BEZEL_OUTLINE_SOURCE` | ASSEMBLY | bezel family only |
| `BEZEL_WALL_CONTINUOUS` | ASSEMBLY | bezel family only |

Registered in `specs/geometry-inspection/v2/fact-registry.json` (now 30 fact types, registry version `1.2.0`), and enforced against the live `FactType` literal by `test_fact_registry_covers_exactly_the_live_fact_type_values` — the drift guard added in Sprint 18, which caught these eight the moment they were added.

Per-component facts (solid count, volume, bounding box, topology validity) are unchanged: the setting component goes through the same generic component inspection every component does.

## Family-scoped facts are honest by construction

Prong facts are emitted **only** for prong settings, bezel facts **only** for bezel settings. A fact's *presence* therefore tells you what was built, and there is no need for a sentinel value meaning "not applicable".

`test_setting.py` asserts both directions: `test_prong_only_facts_are_absent_for_a_bezel` and `test_bezel_only_facts_are_absent_for_a_prong_setting`.

`_setting_facts()` also returns an empty list when a model carries no `setting_result` at all (a hand-constructed fixture, a test double) rather than inventing defaults.

## Facts, never judgements

Both potentially-misreadable facts are deliberately narrow (SETTING-GOV-016):

- **`BEZEL_WALL_CONTINUOUS`** answers exactly one question: is the bezel wall a single closed solid? It is `len(shape.Solids()) == 1`. It is **not** a claim that the stone is adequately held, that coverage is sufficient, or that the wall is manufacturable.
- **`SETTING_COMPATIBILITY_STATUS`** echoes the capability registry's recorded value. It is a *capability* fact, not an assessment of this particular geometry, and `EXPERIMENTAL` is a statement about the placement strategy's maturity rather than a defect in the produced solid.

No fact says "correct", "acceptable", "secure", or "manufacturable". Interpretation belongs to Forge and Professional Validation, and today no Forge rule consumes any `GeometricFact` at all (`forgeConsumptionStatus: "not_consumed"` for all 30).

## Three real leaks found by inspecting a bezel

Wiring bezel through inspection surfaced three genuine architectural assumptions that a code reading alone would not have caught. All three were found because a valid bezel assembly reported `status=FAIL`.

**1. `REQUIRED_COMPONENT_NAMES` hardcoded `prongs`.** Every bezel assembly was missing a "required" component that a bezel legitimately does not have. Fixed by making the requirement setting-family-aware:

```python
REQUIRED_COMPONENT_NAMES = ("band", "stone_reference", "basket_support")
SETTING_COMPONENT_NAMES  = ("prongs", "bezel")

def required_component_names(model):
    present = [n for n in SETTING_COMPONENT_NAMES if n in model.components]
    return (*REQUIRED_COMPONENT_NAMES, *(present or ["prongs"]))
```

The `or ["prongs"]` fallback matters: an assembly with **no** setting component at all still fails loudly rather than silently passing with a shorter requirement list.

**2. Prong count reported `FAIL` for a bezel.** `_prong_count()` returned `status="FAIL"` whenever the `prongs` component was absent. A bezel having no prongs is not a defect — it now returns `NOT_APPLICABLE` when some other setting component is present, and still `FAIL` when there is no setting at all. This is brief section 26's principle applied: not every absence is an error.

**3. Pairwise intersection inspection silently skipped `bezel`.** `_ALL_PAIRS` was a module-level constant built from the hardcoded 4-name tuple, so the `bezel` component was never in any inspected pair. Replaced with `_inspection_pairs(all_names)`, derived from the model's real components — so a bezel's relationships with the band, basket, and stone are genuinely inspected rather than quietly absent. This was the subtlest of the three: nothing failed, facts were simply missing.

`_boolean_operations()` was likewise widened to cover both setting components.

## Stone/setting intersection is not an error

A `StoneReference` is a reference volume, and setting geometry may intentionally overlap it — a prong grips the girdle, a bezel wall surrounds it. Reporting an intersection is correct; classifying it as a defect would be wrong (brief section 26).

The invariant that *is* enforced remains structural: `stoneMetalSeparation.fusedIntoProductionMetal` must be `False`, checked by component identity rather than by intersection volume (INSPECT-GOV-008). Asserted for both families by `test_stone_is_never_fused_into_production_metal`.

## Connectivity

For an assembly that requires attachment, a detached setting component is a real geometric defect. Verified through the existing connectivity methodology — no new overlap threshold was invented (brief section 27). `TestSettingConnectivity` asserts `productionConnectivity.isFullyConnected` and single-solid fusion for both families across `round` and `oval`.

## Verified output

| Configuration | `status` | `prongCount.status` | Facts |
|---|---|---|---|
| round + 6 prong | `PASS` | `PASS` | type, compatibility, componentCount, requested/generated count, strategy |
| round + bezel | `PASS` | `NOT_APPLICABLE` | type, compatibility, componentCount, outlineSource, wallContinuous |
| oval + prong | `PASS` | `PASS` | strategy = `OUTLINE_CARDINAL`, compatibility = `EXPERIMENTAL` |
| oval + bezel | `PASS` | `NOT_APPLICABLE` | outlineSource = `stone_girdle_outline` |

## Read-only

`_setting_facts()` reads the structured result the Setting System already produced and the components' metadata. It re-derives no geometry, mutates nothing, and every value it reports is a plain scalar — no CadQuery or OCP object reaches a fact (INSPECT-GOV-013/016/017).

## Cross-references

- [`../16-geometry-inspection/462-geometric-fact-model.md`](../16-geometry-inspection/462-geometric-fact-model.md) — the `GeometricFact` contract.
- [`code-mapping-and-gaps.md`](code-mapping-and-gaps.md) — the full leak audit.
