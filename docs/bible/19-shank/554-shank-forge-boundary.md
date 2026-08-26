---
id: JM-BIBLE-554
title: Shank Forge Boundary
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-SHANK-README
  - JM-BIBLE-540
  - JM-BIBLE-090
related_documents:
  - JM-BIBLE-553
  - JM-BIBLE-526
implementation_status: current
professional_validation: not_required
normative: true
---

# Shank Forge Boundary

## No jewelry threshold lives in `geometry/shank/`

Verified directly against the source: no file under `geometry/shank/` imports `jewelmind.validation`, and no numeric jewelry-domain constant (a minimum band width, a manufacturability threshold, a comfort guideline) appears anywhere in `profile.py`, `taper.py`, `builder.py`, or `capability.py`. The only fixed numeric values in the package are `SECTION_COUNT = 48` (a construction/sampling parameter, tuned for geometric volume convergence — see [`551-shank-generation-pipeline.md`](551-shank-generation-pipeline.md)) and `COMFORT_FLARE_MM = 0.3`/the fillet-radius constants (both pre-Sprint-17, kernel/shape parameters, not jewelry-domain rules). This satisfies FORGE-GOV-005 directly: geometry code cannot silently introduce jewelry-domain thresholds; a numeric jewelry-domain constant belongs in `validation/` with a rule ID.

## What Shank may report vs. what only Forge may interpret

Shank's real, current reporting surface toward the rest of the system is narrow and construction-time only:

- `widthSamplesMm`/`thicknessSamplesMm` (`{headMm, bottomMm}`) on tapered metadata — two fixed samples, at `u=0.0` (head) and `u=0.5` (bottom), computed from `taper_ratio()`. This is not an arbitrary-`u` query function; Shank does not expose a general `widthAt(u)`/`thicknessAt(u)` capability today, only these two named samples.
- The base, untapered `definition.band.width`/`definition.band.thickness` values, unchanged, still available to any caller via the JDL itself.

Only Forge (`backend/jewelmind/validation/engine.py`) may take either of these values and decide whether they satisfy or violate a jewelry-domain rule — Shank itself never makes that judgment (restating ATLAS-GOV-002/FORGE-GOV-005 for this subsystem, per SHANK-GOV-006/013).

## The real, existing gap: Forge does not see the tapered minimum

`validation/engine.py::_band_rules()` currently evaluates exactly one band-width rule:

```python
if d.band.width < 1.5:
    out.append(R.ValidationResult(ruleId=R.BAND_WIDTH_MIN, severity="error", ...))
```

This checks `d.band.width` — the base, head-anchored value — and nothing else. For a `TOWARD_BOTTOM` width taper, the actual minimum width anywhere on the shank is `d.band.width * bottomRatio` at `u=0.5`, which can be meaningfully smaller than `d.band.width` itself (e.g. `bottomRatio=0.6` on a 2.4mm base band tapers to 1.44mm at the bottom — below the 1.5mm threshold `BAND_WIDTH_MIN` enforces at the head, yet the rule as written would not flag it, because it never reads `widthTaper` at all). `jewelmind.jewelry_category.forge_scope.rule_scope()` still classifies `BAND_WIDTH_MIN` (`JM-BAND-001`) as `ring_shank` scope, unchanged this Sprint — see [`18-ring-architecture/526-shank-contract.md`](../18-ring-architecture/526-shank-contract.md).

This is recorded here as an honest, real, unresolved gap — not silently assumed to already work, and not something this Sprint's brief asked to be fixed. Variable-shank-aware Forge rule semantics (evaluating a threshold against the tapered minimum, not just the base value) do not exist yet. This gap is marked **REQUIRES_RULE_EVOLUTION**: closing it means changing `BAND_WIDTH_MIN`'s evaluation logic (a MAJOR rule-version change per FORGE-GOV-007/[`06-forge/108-rule-versioning.md`](../06-forge/108-rule-versioning.md), since it changes what values a passing document must satisfy), and doing so correctly requires Shank to expose more than the two fixed head/bottom samples it currently does — see [`553-shank-inspection-contract.md`](553-shank-inspection-contract.md) for the corresponding Inspection-side gap, and [`559-open-shank-questions.md`](559-open-shank-questions.md) for this open question.

## The same gap applies to thickness

`_band_rules()` also evaluates `d.band.thickness` against `BAND_THICKNESS_MIN`: an `error` below 1.4mm, a `warning` below 1.6mm, both against `d.band.thickness` — the base head value, exactly as with `BAND_WIDTH_MIN`. A `TOWARD_BOTTOM` thickness taper has the identical gap: the tapered minimum thickness at `u=0.5` (`d.band.thickness * bottomRatio`) is never read by this rule either. This is recorded here as the same class of gap as the width case above, not a second, separately-discovered issue — closing one would naturally prompt closing the other, since both rules share the same "reads only the base scalar" limitation.

## Why the boundary is preserved, not worked around

It would be possible to make `geometry/shank/builder.py` itself refuse to build a tapered shank whose bottom width falls under some hardcoded number, but doing so would violate FORGE-GOV-005 and SHANK-GOV-006/012 at once: it would put a jewelry-domain judgment inside geometry construction code, and it would make Shank subjective-descriptor-adjacent rather than purely geometric. The correct fix, when undertaken, is entirely on the Forge side — extending `_band_rules()` (or a successor) to read `d.band.widthTaper`/`d.band.thicknessTaper` and evaluate against the derived minimum, with its own rule-version bump, its own updated `current-rule-registry.json` entry, and its own tests, per FORGE-GOV-007/014. Nothing in `geometry/shank/` should change to close this gap.

## Summary

| Layer | Responsibility for taper | Current state |
|---|---|---|
| `geometry/shank/` | Report construction-time samples only | `widthSamplesMm`/`thicknessSamplesMm` (head/bottom), no threshold logic |
| `geometry/inspection/` | Measure geometric facts | Generic component facts only, see [`553-shank-inspection-contract.md`](553-shank-inspection-contract.md) |
| `validation/engine.py` | Interpret thresholds | `BAND_WIDTH_MIN`/`BAND_THICKNESS_MIN` evaluate the base value only — tapered minimum not evaluated (REQUIRES_RULE_EVOLUTION) |

See [`559-open-shank-questions.md`](559-open-shank-questions.md) for this gap recorded as an open question rather than a scheduled fix.
