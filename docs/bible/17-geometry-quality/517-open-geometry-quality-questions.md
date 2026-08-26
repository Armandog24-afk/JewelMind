---
id: JM-BIBLE-517
title: Open Geometry Quality Questions
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-QUALITY-README
  - JM-BIBLE-500
  - JM-BIBLE-516
related_documents:
  - JM-BIBLE-QUALITY-README
implementation_status: current
professional_validation: not_required
normative: false
---

# Open Geometry Quality Questions

These are open product and policy questions raised while building Sprint 15, not decisions. None are answered by this document — each requires either a product decision, an RFC, or an ADR per [`500-quality-governance.md`](500-quality-governance.md) before being acted on.

1. **Should Golden coverage expand automatically when a future sprint (e.g. "Ring Architecture v2") generalizes beyond the solitaire?** Today `goldens/solitaire-v1/` is scoped entirely to `build_solitaire_ring()`; a second ring family would need its own suite (`goldens/<new-family>-v1/`) under the same `registry.py::suite_dir(suite_id=...)` mechanism, which already accepts a `suite_id` parameter — but nothing today defines a policy for when a new geometric family becomes "Golden-worthy," or how many cases a new family's initial suite should have.

2. **Should the Golden harness functions record their own performance timing?** [`515-performance-baseline-model.md`](515-performance-baseline-model.md) documents that none of `verify_golden()`/`verify_all_goldens()`/`generate_candidate_baseline()`/`accept_candidate_baseline()` currently measure their own elapsed time, distinct from the inspection-layer timing they indirectly inherit. Is that acceptable indefinitely, or should a `PERFORMANCE_OBSERVATION`-typed signal (the enum value already exists in `QualitySignalType` but nothing produces it) eventually be populated?

3. **Should a `goldenModelId` field be added to `ReviewCase` for reproducibility?** [`514-professional-validation-boundary.md`](514-professional-validation-boundary.md) confirmed this field does not exist anywhere in `backend/jewelmind/professional_validation/schemas.py` today. If a professional reviewer is ever asked to review a case that happens to also be a Golden case, would cross-referencing the two by ID add real value, or would `ReviewCase.definitionHash` (which already exists) already be sufficient for that purpose without introducing a second cross-package reference?

4. **Should the `fastSuite`/`fullSuite` split be exercised by an actual separate CI job once the Golden case count grows?** [`512-ci-regression-gating.md`](512-ci-regression-gating.md) documents that both arrays are real in `manifest.json` but unread by any current code path — `verify_all_goldens()` always runs all 9. At what case count, or at what measured per-case cost, would a targeted-vs-full CI split actually pay for itself over the current single-job approach?

5. **Is the `RELATIVE_COMPARISON_TOLERANCE` of `1e-3` still appropriate once a second ring family exists with very different absolute volume magnitudes?** [`505-comparison-tolerance-policy.md`](505-comparison-tolerance-policy.md) sets this value with two orders of magnitude of margin above a real measured ~1.3e-5 cross-platform kernel divergence, observed specifically on the current solitaire's smallest, most near-tangent intersection volume (band↔prongs). A geometrically very different family (e.g. a much larger or much smaller assembly, or one with different near-tangent conditions) could have a different real noise floor — should the tolerance become per-suite, or does the current single global constant remain appropriate until a second family's own noise floor is actually measured?

6. **Should `compare_snapshot()` special-case an `inspectionVersion` difference the same way it special-cases kernel-related fields?** [`513-regression-failure-triage.md`](513-regression-failure-triage.md)'s INSPECTION_SEMANTIC_CHANGE category is currently identified entirely by human judgment — `_kernel_related_fields_differ()` checks `kernelVersion`/`ocpVersion`/`atlasGeneratorVersion` but not `inspectionVersion`. Would adding `inspectionVersion` to that check (or a parallel one) usefully separate "the kernel changed" from "our own measurement code changed" in the automated severity, or would it blur a distinction that's actually clearer left to a human reading the diff?

7. **Should a future `compilationHash` (still unimplemented per [`08-alchemist/175-definition-hash-vs-compilation-hash.md`](../08-alchemist/175-definition-hash-vs-compilation-hash.md)) absorb `VersionFingerprint`'s fields, or remain a separate concept?** The two overlap conceptually (both want to capture compiler/rule-set/kernel version alongside design identity) but serve different scopes today — `VersionFingerprint` is Golden-suite-scoped, `compilationHash` is proposed as a general `GeneratedModel` identity. Should they eventually converge into one mechanism?

8. **What is the right policy for a Golden case that starts failing purely because a Forge rule it depends on (e.g. JM-PRONG-003 for SOL-009) changes version or threshold?** [`511-current-solitaire-golden-suite.md`](511-current-solitaire-golden-suite.md) documents SOL-009 as `PASS_WITH_KNOWN_LIMITATIONS` because of a Forge warning, not because of a `compare_snapshot()` finding — but a future Forge rule-threshold change (a MAJOR rule-version bump per FORGE-GOV-007) could in principle change which goldens trigger which warnings without changing any geometry at all. Should `knownLimitations` text itself be versioned or re-verified against the live Forge registry, or is treating it as static prose (as it is today) sufficient?

## Cross-references

- [`500-quality-governance.md`](500-quality-governance.md) — the governance process any answer to these questions must go through.
- [`516-current-code-mapping-and-gaps.md`](516-current-code-mapping-and-gaps.md) — the gaps these questions are drawn from.
- `../16-geometry-inspection/495-open-inspection-questions.md` — the Sprint 14 sibling this document follows in structure.

No question in this document is committed to any future sprint by virtue of appearing here.
