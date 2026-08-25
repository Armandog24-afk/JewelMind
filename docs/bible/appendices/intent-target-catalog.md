---
id: JM-BIBLE-A65
title: "Appendix: Intent Target Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-DESIGN-INTENT-README
  - JM-BIBLE-330
related_documents:
  - JM-BIBLE-334
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Intent Target Catalog

The 10 canonical `IntentTarget` values (`backend/jewelmind/design_intent/schemas.py`), each re-validated against `KNOWN_TARGETS` and `TARGET_SYNONYMS` in `backend/jewelmind/design_intent/vocabulary.py`/`normalizer.py::normalize_target()`.

| `IntentTarget` | Real `TARGET_SYNONYMS` entries | Maps to an adjustable geometry component? |
|---|---|---|
| `JEWELRY_PRODUCT` | "jewelry", "gioiello", "product" | No — whole-piece descriptive label only |
| `RING` | "ring", "anello", "whole ring", "overall" | No — whole-piece descriptive label only |
| `BAND` | "band", "fascia" | Yes — `band` geometry component |
| `STONE` | "stone", "pietra", "diamond", "diamante" | Yes — `stone_reference` geometry component |
| `SETTING` | "setting", "castone" | Yes — `setting` geometry component |
| `PRONGS` | "prongs", "griffe" | Yes — `prongs` geometry component |
| `BASKET` | "basket" (no IT synonym registered) | Yes — `basket_support` geometry component |
| `MATERIAL_APPEARANCE` | none registered in `TARGET_SYNONYMS` | No — whole-piece descriptive label only; currently unreachable via any synonym, only via an exact `"MATERIAL_APPEARANCE"` token |
| `OVERALL_PROPORTION` | none registered in `TARGET_SYNONYMS` | No — whole-piece descriptive label only; currently unreachable via any synonym, only via an exact `"OVERALL_PROPORTION"` token |
| `VISUAL_HIERARCHY` | none registered in `TARGET_SYNONYMS` | No — whole-piece descriptive label only; currently unreachable via any synonym, only via an exact `"VISUAL_HIERARCHY"` token |

## Notes grounded in the real code

- `normalize_target()` first checks whether the raw token, upper-cased, is already one of the 10 canonical values (`KNOWN_TARGETS` in `normalizer.py`) before falling back to `TARGET_SYNONYMS`. This is why `MATERIAL_APPEARANCE`, `OVERALL_PROPORTION`, and `VISUAL_HIERARCHY` are real, valid targets in the schema even though no natural-language synonym currently reaches them — a provider (or future vocabulary update) supplying the exact token still resolves correctly.
- Per **INTENT-GOV-002**, `IntentStatement.target` is a required, non-optional field — `resolver.py::_resolve_statements` never constructs a statement without first confirming `normalize_target()` returned a real value; an unresolvable target is preserved verbatim in `unresolvedDescriptors` instead (verified by `backend/tests/test_design_intent.py::TestBuildDesignIntent::test_unknown_target_is_preserved_as_unresolved`).
- "Adjustable geometry component" here means: the target names a component that Atlas can currently regenerate independently (`band`, `stone_reference`, `setting`, `prongs`, `basket_support` — see `docs/bible/appendices/atlas-component-catalog.md`). Design Intent itself never writes to any of these components' JDL fields (INTENT-GOV-001); this column only records whether the target *names* something geometry-adjustable, for scoping future resolution work.
