---
id: JM-BIBLE-559
title: Open Shank Questions
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-SHANK-README
  - JM-BIBLE-540
related_documents:
  - JM-BIBLE-554
  - JM-BIBLE-553
  - JM-BIBLE-557
implementation_status: current
professional_validation: not_required
normative: false
---

# Open Shank Questions

This document records genuinely open questions this Sprint identified but did not resolve. None of these is a decision — each is a real question a future Sprint, RFC, or ADR would need to answer. Nothing here should be read as already-planned or already-agreed; that is the reason `normative: false` on this document, unlike every other document in this section.

## Should Forge gain variable-shank-aware rule evaluation?

`BAND_WIDTH_MIN` (`JM-BAND-001`) currently checks only `d.band.width`, the base head value — never the tapered minimum a `TOWARD_BOTTOM` width taper can produce at the bottom (see [`554-shank-forge-boundary.md`](554-shank-forge-boundary.md)). Whether this should be closed, and if so how a rule should express "evaluate against the minimum across the shank's length" rather than "evaluate against one scalar field," is open. Resolving it means a rule-version-impact analysis under [`06-forge/108-rule-versioning.md`](../06-forge/108-rule-versioning.md) (this would be a MAJOR change to `BAND_WIDTH_MIN`'s semantics) and, per [`06-forge/090-forge-governance.md`](../06-forge/090-forge-governance.md), likely the standard code+docs+tests change rather than a new rule family — but the exact evaluation semantics (minimum only? both endpoints? something else?) have not been decided.

## Should Geometry Inspection gain a dedicated per-`u` measurement fact?

Today, `widthSamplesMm`/`thicknessSamplesMm` are CONSTRUCTION_PARAMETER values computed from the same `taper_ratio()` call that built the geometry — nothing independently re-measures a tapered shank's actual width/thickness at an arbitrary `u` from the resulting solid (see [`553-shank-inspection-contract.md`](553-shank-inspection-contract.md)). Whether this gap is worth closing — and if so, whether it belongs as a new `FactType` in `geometry/inspection/models.py` with its own measurement function — is open. Per [`16-geometry-inspection/460-inspection-governance.md`](../16-geometry-inspection/460-inspection-governance.md), a new inspection family of this kind requires an RFC; if the resulting fact were ever intended to feed a Forge rule, closing the Forge-side question above would also require it.

## Should the outer-rim fillet be implemented for tapered shanks?

`_build_tapered_shank()` never applies the outer-rim fillet (`filletApplied: false`, `filletSkippedReason` always set) — there is no single "circle at radius X" to select once the radius varies by angle (SHANK-GOV-014, `outer_rim_fillet_on_tapered_shank: planned` in the capability registry). Whether and how to implement this is open: it would require a different, per-section fillet strategy than the uniform path's single-selector approach, and its design has not been explored. Per [`540-shank-governance.md`](540-shank-governance.md#when-an-adr-is-required), this is one of the changes explicitly named as requiring an ADR before implementation.

## Should `TOWARD_HEAD` or a non-linear taper curve be added?

Only `NONE` and `TOWARD_BOTTOM` exist in `BandTaperMode` today. Whether a `TOWARD_HEAD` mode (tapering toward the head instead of the bottom — which would also raise the question of what happens to `topZMm`'s current head-anchoring guarantee, see [`550-head-connection-interface.md`](550-head-connection-interface.md)) or a non-linear interpolation curve should be added is open, and unresolved is which kind of change it would be: [`540-shank-governance.md`](540-shank-governance.md#when-an-rfc-is-required) states that widening `BandTaperMode` requires an RFC even though it is architecturally an additive JDL change, because it changes the taper model itself, not just adds a field — but whether a non-linear curve would additionally require a bigger model change (and its own ADR) beyond a new enum member has not been decided.

## Should Designer be allowed to propose `widthTaper`/`thicknessTaper`?

`designer_taper_proposal` is `planned`, `jdlExposed: false` in the capability registry — taper fields are not in Designer's `KNOWN_JDL_FIELD_PATHS` this Sprint, so Designer cannot currently propose them at all. Whether to add this capability, and if so what field-provenance and capability-gating rules would apply (per [`12-designer/README.md`](../12-designer/README.md)'s existing `capability.py` gating pattern for every other field), is open and was explicitly out of this Sprint's scope.

## Does the `SECTION_COUNT=72` STEP-roundtrip discrepancy warrant deeper investigation now?

[`558-current-code-mapping-and-gaps.md`](558-current-code-mapping-and-gaps.md) records a ~0.26% bounding-box discrepancy observed once at `SECTION_COUNT=72` during tuning, not reproducible at `SECTION_COUNT=48` across 4 retested configurations. Whether this was a one-off environment artifact, a real kernel sensitivity to section count that happens not to manifest at 48, or something else, was not root-caused. This is open specifically because `SECTION_COUNT` is exactly the kind of constant SHANK-GOV-008 protects — any future change to it should treat re-investigating this discrepancy as a required step, not an optional one, but no owner or timeline for that investigation exists today.

## Should `golden-update-register.md` be updated for SOL-010/011/012?

[`555-shank-golden-strategy.md`](555-shank-golden-strategy.md) records that the appendix does not yet list the three new Golden cases this Sprint added, despite QUALITY-GOV-018 requiring it. This is not a design question like the others above — it is a small, concrete documentation gap — but it is included here because closing it was out of scope for the file set this Sprint's brief defined, and it should not be silently forgotten once a future change next touches that appendix.

## How these questions should be used

None of the above should be read as a commitment or a roadmap item. Each is included because it was surfaced by real work done this Sprint — a real code boundary, a real gap in what a rule or a fact type currently checks, or a real registry entry left `planned` — and each requires a real decision-making process (RFC, ADR, or a scoped follow-up Sprint) before it becomes anything more than a question. A future coding agent should treat resolving one of these as a reason to update this document (moving the resolved item into the relevant normative document and removing it from here), not as a reason to silently start implementing it.
