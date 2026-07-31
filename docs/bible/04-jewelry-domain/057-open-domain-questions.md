---
id: JM-BIBLE-057
title: Open Domain Questions
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-07-31
source_of_truth: true
depends_on: []
related_documents:
  - JM-BIBLE-058
  - JM-BIBLE-054
implementation_status: current
professional_validation: not_required
---

# Open Domain Questions

A prioritized register of unresolved questions surfaced while writing
this Sprint. None are answered by guessing — each row states its current
**provisional treatment** (what JewelMind does today in the absence of an
answer), not a resolution.

| ID | Question | Category | Reason it matters | Affected modules | Risk | Required expert profile | Priority | Blocking? | Current provisional treatment |
|---|---|---|---|---|---|---|---|---|---|
| JM-DQ-001 | Are "signet" and "chevalier" fully synonymous across regional jewelry traditions, or do they denote subtly different structures? | terminology | Affects whether they should be one taxonomy entry or two | [`042-ring-taxonomy.md`](042-ring-taxonomy.md) | Low — naming only | Jewelry historian or multilingual bench jeweler | low | non-blocking | Treated as one PLANNED candidate |
| JM-DQ-002 | Is "pavé" ever used, in any professional context, to name a ring style rather than a setting/decorative treatment? | terminology | Prevents a future contributor from misclassifying it as a ring category | [`042-ring-taxonomy.md`](042-ring-taxonomy.md), [`047-setting-domain.md`](047-setting-domain.md) | Medium — a wrong classification could shape a future schema incorrectly | Bench jeweler or jewelry-industry copywriter | medium | non-blocking | Documented explicitly as setting/decorative, not structural |
| JM-DQ-003 | What is the professionally correct minimum band width and thickness for common metals (gold, platinum, silver) at typical solitaire proportions? | band construction | `JM-BAND-001`/`JM-BAND-002` thresholds are currently engineering guesses | [`045-band-domain.md`](045-band-domain.md), `validation/engine.py` | High — a wrong threshold could pass a structurally fragile design or reject a valid one | Bench jeweler / CAD-for-jewelry specialist | high | non-blocking (current thresholds remain in place as PRELIMINARY) | `JM-BAND-001`/`002` enforced as-is, labeled preliminary |
| JM-DQ-004 | Should the comfort-fit inner-edge flare amount (`_COMFORT_FLARE_MM = 0.3`) vary with band width/thickness rather than being fixed? | geometry | Affects whether comfort-fit is realistic across the full parameter range | [`045-band-domain.md`](045-band-domain.md), `geometry/components/band.py` | Medium | CAD-for-jewelry specialist | medium | non-blocking | Fixed constant used for all inputs |
| JM-DQ-005 | Is the `prong_center_radius` "× 0.3" girdle-overlap factor a reasonable approximation of real prong-to-stone contact, or does it need to vary by stone size/prong diameter? | stone setting | Directly affects whether the visual/dimensional grip approximation is meaningful at all sizes | [`048-prong-domain.md`](048-prong-domain.md), `geometry/constants.py` | Medium | Bench jeweler / stone setter | medium | non-blocking | Fixed factor used for all inputs |
| JM-DQ-006 | What professionally validated minimum prong diameter exists for common metals at typical stone sizes? | stone setting | `JM-PRONG-002`'s 0.8/1.0mm thresholds are engineering guesses | [`048-prong-domain.md`](048-prong-domain.md), `validation/engine.py` | High | Stone setter | high | non-blocking | `JM-PRONG-002` enforced as-is, labeled preliminary |
| JM-DQ-007 | At what stone size (if any single threshold is even appropriate) should 6 prongs be recommended over 4 for security, and does this vary by metal or stone shape? | stone setting | `JM-PRONG-003`'s 8mm threshold is an unvalidated heuristic behind a genuine security concern | [`048-prong-domain.md`](048-prong-domain.md), `validation/engine.py` | High — real setting security risk if the threshold is wrong and trusted | Stone setter | high | non-blocking | `JM-PRONG-003` enforced as a warning only, labeled preliminary |
| JM-DQ-008 | Is a plain hollow cylindrical wall a structurally adequate basket approximation, or does real basket design require a fundamentally different shape (e.g. distinct upper/lower rings with connectors)? | geometry | Determines whether the current simplification is "close enough" or misleading | [`049-basket-and-support-domain.md`](049-basket-and-support-domain.md) | Medium | CAD-for-jewelry specialist | medium | non-blocking | Current hollow-cylinder implementation used unconditionally |
| JM-DQ-009 | What are real density values for each of the five currently-supported metals/alloys, and from what authoritative source? | materials | Needed before any weight-estimation feature | [`050-material-domain.md`](050-material-domain.md) | Medium — wrong density silently produces a wrong weight estimate if ever implemented | Materials engineer / refiner | medium | blocking (for any future weight feature specifically) | No density data exists in code at all today |
| JM-DQ-010 | What casting shrinkage compensation (if any) is appropriate for lost-wax casting in each supported metal? | manufacturing | Needed before any dimensional-compensation feature | [`051-manufacturing-context.md`](051-manufacturing-context.md) | High — wrong compensation produces incorrectly-sized cast pieces | Casting specialist | high | blocking (for any future compensation feature) | No shrinkage compensation implemented at all |
| JM-DQ-011 | What is a professionally appropriate minimum feature size for direct resin printing, and does it vary by resin type/printer? | manufacturing | `JM-MANUFACTURING-001`'s 0.8mm threshold is generic | [`051-manufacturing-context.md`](051-manufacturing-context.md), `validation/engine.py` | High | 3D-printing-for-jewelry specialist | high | non-blocking | `JM-MANUFACTURING-001` enforced as a generic warning, labeled preliminary |
| JM-DQ-012 | Beyond EU/French, which sizing systems (US, UK, Japanese, etc.) should JewelMind support, and what are the correct conversion formulas between them? | sizing systems | Current system supports only one convention | [`044-solitaire-domain-model.md`](044-solitaire-domain-model.md), `validation/sizing.py` | Medium — international users cannot size correctly today | Jewelry retailer / sizing-standard reference | medium | non-blocking | Only `sizeSystem: "EU"` accepted; documented as a known limitation |
| JM-DQ-013 | Should `preview.meshTolerance`/`angularTolerance` have professionally meaningful defaults tied to manufacturing method (e.g. tighter tolerance for casting masters), or are they purely a preview-quality knob? | tolerances | Currently treated as preview-only; may matter more for STL-based manufacturing | [`052-parametric-dependency-model.md`](052-parametric-dependency-model.md), `exporters/stl_exporter.py` | Medium | CAD/manufacturing specialist | medium | non-blocking | Fixed schema defaults (0.1mm / 0.2 rad) used regardless of manufacturing method |
| JM-DQ-014 | Do professionals expect STEP exports to include construction history/parametric features (a "smart" STEP), or is a dumb B-Rep solid (current behavior) sufficient for downstream use? | export expectations | Affects whether current STEP export meets real workflow needs | [`03-decisions/ADR-010-step-and-stl-export-strategy.md`](../03-decisions/ADR-010-step-and-stl-export-strategy.md) | Low-medium | CAD-for-jewelry specialist | low | non-blocking | Dumb B-Rep solid exported, per CadQuery's standard STEP output |
| JM-DQ-015 | What professional review workflow (who reviews, what they check, what "approved" means) should JewelMind eventually formalize beyond the current static disclaimer text? | professional workflow | The current disclaimer is a blanket statement, not a structured review process | [`058-professional-validation-register.md`](058-professional-validation-register.md), [LAW-010](../00-foundation/004-jewelmind-constitution.md#LAW-010) | Medium | Jewelry-industry process consultant | medium | non-blocking | Static disclaimer text only; no structured review workflow exists |
| JM-DQ-016 | Should a failed boolean-fuse fallback path (multi-solid compound) be exercised by a dedicated failure-injection test, rather than relying on code inspection alone? | geometry | Current test suite verifies the success path; the fallback path's correctness is inferred from reading the code, not directly tested | [`053-domain-invariants.md`](053-domain-invariants.md), `geometry/assemblies/solitaire.py` | Low-medium (engineering risk, not a jewelry-domain question) | Software engineer (not a jewelry professional) | low | non-blocking | Fallback logic exists and is documented; no dedicated test forces the fuse to fail |

## Priority summary

- **High priority (professional input would materially change a
  currently-trusted safety-relevant threshold):** JM-DQ-003, JM-DQ-006,
  JM-DQ-007, JM-DQ-010, JM-DQ-011.
- **Blocking for a specific future feature (not blocking current
  operation):** JM-DQ-009 (weight estimation), JM-DQ-010 (dimensional
  compensation).
- **Everything else:** medium or low priority, non-blocking.

No question above is answered with an invented number in this document
or anywhere else in this Sprint's documentation.
