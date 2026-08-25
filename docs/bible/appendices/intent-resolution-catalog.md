---
id: JM-BIBLE-A67
title: "Appendix: Intent Resolution Catalog"
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-25
source_of_truth: true
depends_on:
  - JM-BIBLE-DESIGN-INTENT-README
  - JM-BIBLE-330
related_documents:
  - JM-BIBLE-348
implementation_status: current
professional_validation: not_required
normative: true
---

# Appendix: Intent Resolution Catalog

The 7 `ResolutionStatus` values (`backend/jewelmind/design_intent/schemas.py`). Verified by grepping every `resolutionStatus=`/`resolutionStatus":` assignment site in `backend/jewelmind/design_intent/resolver.py` and `conflicts.py` — only 2 of the 7 values are ever actually produced by v1 code.

| `ResolutionStatus` | Currently produced by real code? | Real condition |
|---|---|---|
| `UNRESOLVED` | No | Declared in the type; not assigned anywhere in `resolver.py`/`conflicts.py`. A statement that cannot be normalized is instead dropped entirely from `statements` and recorded as free text in `DesignIntent.unresolvedDescriptors` — it never becomes an `IntentStatement` with this status. |
| `PRESERVED` | Yes | The default for every successfully normalized, non-conflicting statement/relation — set unconditionally in `resolver.py::_resolve_statements` and `_resolve_relations` at construction time, since v1 registers zero deterministic subjective-to-numeric mappings (`349-deterministic-resolution-policy.md`). |
| `DETERMINISTICALLY_RESOLVED` | No | Would require a registered `IntentProfile` with a non-empty `jdlMapping` (`schemas.py`) — none exists in v1; reserved for a future deterministic-resolution mapping. |
| `USER_RESOLVED` | No | Would require a user-confirmation resolution step over an `IntentResolution` record — `IntentResolution` (`schemas.py`) is modeled but "not currently persisted anywhere" per its own docstring. |
| `PROFILE_RESOLVED` | No | Same gap as `DETERMINISTICALLY_RESOLVED` — depends on a registered `IntentProfile`, which does not exist in v1. |
| `UNSUPPORTED` | No | Declared but not assigned by any current code path; there is no "recognized target/concept but structurally unsupported" branch distinct from the unresolved-descriptor path today. |
| `CONFLICTING` | Yes | Set in `resolver.py::build_design_intent` via `model_copy(update={"resolutionStatus": "CONFLICTING"})` for every statement/relation whose id appears in `conflicting_ids(conflicts)` — i.e. every statement/relation that `conflicts.py::detect_conflicts()` flagged. |

## Notes grounded in the real code

- Because only `PRESERVED` and `CONFLICTING` are ever produced, `backend/tests/test_design_intent_schemas.py::test_deterministic_resolution_vectors_never_show_a_numeric_mapping` asserts exactly this: every vector in `specs/design-intent/v1/test-vectors/deterministic-resolution-vectors.json` has `resolutionStatus` in `("PRESERVED", "CONFLICTING")`.
- The 5 unproduced values are not dead code by mistake — they exist so a future, explicitly-approved resolution step (an `IntentProfile`, or a user-confirmation UI flow) has a real target shape to write into without a schema change, per **INTENT-GOV-018**.
