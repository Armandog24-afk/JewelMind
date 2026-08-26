---
id: JM-BIBLE-505
title: Comparison Tolerance Policy
version: 1.0.0
status: accepted
owner: JewelMind
last_updated: 2026-08-26
source_of_truth: true
depends_on:
  - JM-BIBLE-000
  - JM-BIBLE-QUALITY-README
  - JM-BIBLE-500
related_documents:
  - JM-BIBLE-504
  - JM-BIBLE-486
  - JM-BIBLE-137
implementation_status: current
professional_validation: not_required
normative: true
---

# Comparison Tolerance Policy

`backend/jewelmind/geometry_quality/version.py` defines two constants:

```python
ABSOLUTE_COMPARISON_TOLERANCE_MM = 1e-4
RELATIVE_COMPARISON_TOLERANCE = 1e-3
```

## These are never manufacturing tolerances

Restating QUALITY-GOV-006 plainly: these two constants exist for exactly one purpose — distinguishing a real geometry regression from harmless floating-point noise when comparing two software-generated `GeometrySnapshot`s. Neither number expresses a jewelry-manufacturing fit, a stone-setting clearance, a casting shrinkage allowance, or any other domain tolerance. A jewelry-domain tolerance belongs in `backend/jewelmind/validation/engine.py` with a Forge rule ID (per [`04-jewelry-domain/040-domain-governance.md`](../04-jewelry-domain/040-domain-governance.md)'s "no invented measurement" rule) — never here.

## How `_numeric_diff()` actually applies them

From `compare.py`:

```python
absolute_delta = abs(actual - expected)
relative_delta = absolute_delta / abs(expected) if expected else None
within = absolute_delta <= ABSOLUTE_COMPARISON_TOLERANCE_MM or (
    relative_delta is not None and relative_delta <= RELATIVE_COMPARISON_TOLERANCE
)
```

A numeric fact is `withinTolerance` if it passes **either** an absolute check (`0.0001` mm) **or** a relative check (`0.1%`) — an OR, not an AND. The absolute check dominates for facts near zero (where a relative percentage is meaningless or undefined, e.g. `expected == 0`); the relative check dominates for large facts (e.g. a bounding-box dimension in the tens of millimeters, where `0.0001mm` absolute would be unreasonably strict relative to expected float noise at that magnitude).

## The real empirical basis — not guessed

### 1. Local repeatability is bit-identical

`backend/tests/test_geometry_quality_harness.py::TestRepeatability::test_three_repeated_generations_are_bit_identical_locally` calls `generate_snapshot(default_definition())` three times on the same machine/kernel build and asserts all three dumped snapshots are exactly equal (`dumps[0] == dumps[1] == dumps[2]`). This confirms JewelMind's own determinism guarantee (ATLAS-GOV-003) holds in the environment that matters most for day-to-day development: repeated local regeneration of the same definition produces zero floating-point drift, not "drift within tolerance" — literally zero.

### 2. The only real observed drift is cross-platform, and it's small

[`486-inspection-determinism.md`](../16-geometry-inspection/486-inspection-determinism.md) records Sprint 14's own CI finding: a ~1.3e-5 relative divergence between Windows and Linux OCCT builds, on the smallest and most numerically sensitive quantity available — a near-tangent pairwise intersection volume between band and prongs. This is the one real, measured instance of cross-platform kernel float variance anywhere in JewelMind's test history at the time this Sprint's tolerance was set.

### 3. The tolerance is set with margin, not tightness, in mind

`RELATIVE_COMPARISON_TOLERANCE = 1e-3` is roughly two orders of magnitude (≈77×, and treated as "~100x" in the constant's own docstring) above the measured `1.3e-5` cross-platform bound. This is deliberate margin: the tolerance must absorb real cross-platform kernel noise on legitimate CI runs across different OCCT builds, while still catching an actual regression — which, per the version.py docstring's own reasoning, changes geometry by "orders of magnitude more" than a rounding-level amount (a genuine dimension bug, a dropped fillet, a wrong prong count, all move volumes/bounding boxes by percent-level or larger amounts, not by parts in ten-thousand).

## Distinct from Sprint 14's own tolerances

This is a **third**, distinct tolerance value in the codebase, not a duplicate of either existing one:

- [`486-inspection-determinism.md`](../16-geometry-inspection/486-inspection-determinism.md)'s in-memory determinism test uses `pytest.approx(rel=1e-9)` — far tighter, because it compares two `inspect_model()` calls against the *same in-memory shape*, where no new kernel reconstruction happens between calls.
- Sprint 14's `492-inspection-regression-model.md` historical-baseline comparison uses a looser `5%` tolerance for its own separate purpose (not read in full for this document; referenced here only to distinguish it, not to restate its content).
- This Sprint's `RELATIVE_COMPARISON_TOLERANCE = 1e-3` (0.1%) sits between those two — tighter than the 5% historical-baseline check, far looser than the `1e-9` same-object check, calibrated specifically against the one real cross-platform measurement available.

## What this tolerance does not claim

It does not claim that `1.3e-5` is the maximum possible cross-platform divergence for every geometry JewelMind will ever generate — it is the one real measurement available at the time this constant was set, on one specific near-tangent case. If a future CI run on a different platform combination, kernel version, or geometry shape produces a larger legitimate divergence, that is new evidence for revisiting this constant through the normal governance path (a documented, reasoned change to `version.py`, not a silent widening) — never a reason to declare the existing tolerance wrong after the fact without new data.
