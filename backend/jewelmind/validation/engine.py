"""Deterministic validation engine for a JewelryDefinition.

This is the authoritative validator: the frontend may mirror a subset of
these rules for instant feedback, but the backend re-validates before any
geometry generation or export and rejects on errors regardless of what the
client believes.
"""

from __future__ import annotations

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.domain.stone_dimensions import (
    resolved_depth_mm,
    resolved_length_mm,
    resolved_width_mm,
)
from jewelmind.validation import rules as R
from jewelmind.validation.sizing import eu_size_to_inner_diameter, sizing_consistency


def _ring_rules(d: JewelryDefinition) -> list[R.ValidationResult]:
    out: list[R.ValidationResult] = []

    if not (10 < d.ring.innerDiameter < 30):
        out.append(
            R.ValidationResult(
                ruleId=R.RING_INNER_DIAMETER_RANGE,
                severity="error",
                message="Ring inner diameter must be greater than 10 mm and lower than 30 mm.",
                parameter="ring.innerDiameter",
            )
        )

    if not (1 < d.ring.size < 50):
        out.append(
            R.ValidationResult(
                ruleId=R.RING_SIZE_RANGE,
                severity="error",
                message="EU ring size must be greater than 1 and lower than 50.",
                parameter="ring.size",
            )
        )

    consistency = sizing_consistency(d.ring.size, d.ring.innerDiameter)
    if consistency is not None:
        implied = eu_size_to_inner_diameter(d.ring.size)
        out.append(
            R.ValidationResult(
                ruleId=R.RING_SIZE_DIAMETER_CONSISTENCY,
                severity=consistency,
                message=(
                    f"EU size {d.ring.size:g} implies an inner diameter of "
                    f"{implied:.2f} mm, which differs from the stored "
                    f"{d.ring.innerDiameter:g} mm. Sizing conventions vary; "
                    "review which value should take precedence."
                ),
                parameter="ring.innerDiameter",
                suggestedValue=round(implied, 2),
            )
        )

    return out


def _band_rules(d: JewelryDefinition) -> list[R.ValidationResult]:
    out: list[R.ValidationResult] = []

    if d.band.width < 1.5:
        out.append(
            R.ValidationResult(
                ruleId=R.BAND_WIDTH_MIN,
                severity="error",
                message="Band width below 1.5 mm is not supported.",
                parameter="band.width",
                suggestedValue=1.5,
            )
        )
    elif d.band.width > 12:
        out.append(
            R.ValidationResult(
                ruleId=R.BAND_WIDTH_MAX,
                severity="warning",
                message="Band width above 12 mm is unusually wide for a solitaire band.",
                parameter="band.width",
            )
        )

    if d.band.thickness < 1.4:
        out.append(
            R.ValidationResult(
                ruleId=R.BAND_THICKNESS_MIN,
                severity="error",
                message="Band thickness below 1.4 mm is not supported.",
                parameter="band.thickness",
                suggestedValue=1.4,
            )
        )
    elif d.band.thickness < 1.6:
        out.append(
            R.ValidationResult(
                ruleId=R.BAND_THICKNESS_MIN,
                severity="warning",
                message="Band thickness below 1.6 mm may be structurally fragile.",
                parameter="band.thickness",
                suggestedValue=1.6,
            )
        )

    return out


def _stone_depth_rule_applies(stone) -> bool:
    """Whether STONE_DEPTH_RANGE's premise holds for this stone.

    Returns False where the rule was never calibrated, rather than evaluating it
    against a dimension it does not describe (STONE-GOV-010's discipline).
    """

    if stone.source == "IMPORTED_CAD":
        return False
    if stone.profile == "SPHERICAL_REFERENCE" or stone.shape == "pearl":
        return False
    return True


def _stone_rules(d: JewelryDefinition) -> list[R.ValidationResult]:
    """Stone-domain rules, scoped to the stone sources they were calibrated for.

    Sprint 18: `STONE_DIAMETER_RANGE` is ROUND_ONLY (round was the only shape
    with a `diameter`); `STONE_DEPTH_RANGE` was generalized to the stone's real
    minimum horizontal extent, a genuine structural generalization (depth must
    not exceed the stone's own footprint) rather than a fabricated "equivalent
    diameter".

    Sprint 20 scoping, both found by actually running validation against the new
    sources rather than by reading the code:

    - A SPHERICAL reference (pearl) is exempt from `STONE_DEPTH_RANGE`. A
      sphere's depth IS its horizontal extent, so `depth < min_extent` can never
      hold and the rule fired on every valid pearl. The rule's premise — that a
      stone is wider than it is deep — simply does not describe a sphere. Marked
      REQUIRES_RULE_EVOLUTION rather than "fixed" by loosening the threshold,
      which would have weakened it for every other shape.

    - An IMPORTED stone is exempt from both dimension rules. Its true dimensions
      are a property of the asset, not of the document, so
      `resolved_length_mm()` correctly refuses to answer — and calling it here
      raised `StoneDimensionsUnavailableError` straight out of validation. Its
      real dimensions are reported by Geometry Inspection from the imported
      geometry; interpreting them is future rule work, not something to fake
      from the document.

    `stone.diameter` still has no range rule for `pearl`, and a non-round
    shape's `length`/`width` still have none individually. Both are real,
    recorded gaps — see docs/bible/22-stone-v2/code-mapping-and-gaps.md — not
    solved by inventing a threshold this Sprint (STONEV2-GOV-011).
    """

    out: list[R.ValidationResult] = []

    if d.stone.shape == "round":
        assert d.stone.diameter is not None
        if not (2 <= d.stone.diameter <= 15):
            out.append(
                R.ValidationResult(
                    ruleId=R.STONE_DIAMETER_RANGE,
                    severity="error",
                    message="Stone diameter must be between 2 mm and 15 mm.",
                    parameter="stone.diameter",
                )
            )

    if _stone_depth_rule_applies(d.stone):
        min_extent = min(resolved_length_mm(d.stone), resolved_width_mm(d.stone))
        if not (0.5 < resolved_depth_mm(d.stone) < min_extent):
            out.append(
                R.ValidationResult(
                    ruleId=R.STONE_DEPTH_RANGE,
                    severity="error",
                    message=(
                        "Stone depth must be greater than 0.5 mm and lower than the "
                        "stone's minimum horizontal extent."
                    ),
                    parameter="stone.depth",
                )
            )

    return out


def _prong_rules(d: JewelryDefinition) -> list[R.ValidationResult]:
    """PRONG_ONLY (Sprint 19). Every rule in this function reads a prong
    field, so none of them is meaningful for a bezel setting — a bezel has
    no prongs to count, size, or clear. Evaluating them anyway would block
    a perfectly valid bezel on `setting.prongCount`, which is exactly the
    mis-scoping brief section 32 calls out.

    Classification per rule:
      JM-PRONG-001 (count)             PRONG_ONLY
      JM-PRONG-002 (diameter min)      PRONG_ONLY
      JM-PRONG-003 (count vs size)     PRONG_ONLY + ROUND_ONLY (Sprint 18)
      JM-PRONG-004 (height vs basket)  PRONG_ONLY

    See docs/bible/21-setting/code-mapping-and-gaps.md for the full
    Setting-scoped rule table.
    """

    out: list[R.ValidationResult] = []

    if d.setting.type != "prong":
        return out

    if d.setting.prongCount not in (4, 6):
        out.append(
            R.ValidationResult(
                ruleId=R.PRONG_COUNT,
                severity="error",
                message="Prong count must be exactly 4 or 6.",
                parameter="setting.prongCount",
                suggestedValue=6,
            )
        )

    if d.setting.prongDiameter < 0.8:
        out.append(
            R.ValidationResult(
                ruleId=R.PRONG_DIAMETER_MIN,
                severity="error",
                message="Prong diameter below 0.8 mm is not supported.",
                parameter="setting.prongDiameter",
                suggestedValue=0.8,
            )
        )
    elif d.setting.prongDiameter < 1.0:
        out.append(
            R.ValidationResult(
                ruleId=R.PRONG_DIAMETER_MIN,
                severity="warning",
                message="Prong diameter below 1.0 mm may be structurally fragile.",
                parameter="setting.prongDiameter",
                suggestedValue=1.0,
            )
        )

    # ROUND_ONLY (Sprint 18): tuned for a round stone's diameter; applying
    # it to a non-round shape's length/width would need real, justified
    # generalization this Sprint does not provide — a REQUIRES_RULE_EVOLUTION
    # gap, not silently evaluated against a fake equivalent diameter (brief
    # section 44). See docs/bible/20-stone/578-current-code-mapping-and-gaps.md.
    stone_is_large_round = (
        d.stone.shape == "round" and d.stone.diameter is not None and d.stone.diameter > 8
    )
    if stone_is_large_round and d.setting.prongCount == 4:
        out.append(
            R.ValidationResult(
                ruleId=R.PRONG_COUNT_VS_STONE_SIZE,
                severity="warning",
                message="Stones larger than 8 mm are typically more secure with six prongs.",
                parameter="setting.prongCount",
                suggestedValue=6,
            )
        )

    if not (d.setting.prongHeight > d.setting.basketHeight):
        out.append(
            R.ValidationResult(
                ruleId=R.PRONG_HEIGHT_VS_BASKET,
                severity="error",
                message="Prong height must be greater than basket height.",
                parameter="setting.prongHeight",
            )
        )

    return out


def _bezel_rules(d: JewelryDefinition) -> list[R.ValidationResult]:
    """BEZEL_ONLY (Sprint 19). Deliberately ENGINEERING_INVARIANT rules
    only: both check that a dimension is positive, which is a
    constructibility fact, not a jewelry-domain threshold.

    No minimum bezel wall thickness or height is asserted. Such a minimum
    would be a professional manufacturing threshold, and no sourced value
    exists — inventing one is forbidden by SETTING-GOV-010. This is a real,
    documented gap, not an oversight: see
    docs/bible/21-setting/code-mapping-and-gaps.md.
    """

    out: list[R.ValidationResult] = []

    if d.setting.type != "bezel":
        return out

    if d.setting.bezelWallThickness <= 0:
        out.append(
            R.ValidationResult(
                ruleId=R.BEZEL_WALL_THICKNESS_POSITIVE,
                severity="error",
                message="Bezel wall thickness must be positive.",
                parameter="setting.bezelWallThickness",
            )
        )

    if d.setting.bezelWallHeight <= 0:
        out.append(
            R.ValidationResult(
                ruleId=R.BEZEL_WALL_HEIGHT_POSITIVE,
                severity="error",
                message="Bezel wall height must be positive.",
                parameter="setting.bezelWallHeight",
            )
        )

    return out


def _setting_rules(d: JewelryDefinition) -> list[R.ValidationResult]:
    out: list[R.ValidationResult] = []

    if d.setting.basketHeight <= 0:
        out.append(
            R.ValidationResult(
                ruleId=R.SETTING_BASKET_HEIGHT_POSITIVE,
                severity="error",
                message="Basket height must be positive.",
                parameter="setting.basketHeight",
            )
        )
    elif d.setting.basketHeight > 8:
        out.append(
            R.ValidationResult(
                ruleId=R.SETTING_BASKET_HEIGHT_MAX,
                severity="warning",
                message="Basket height above 8 mm is unusually tall.",
                parameter="setting.basketHeight",
            )
        )

    return out


def _manufacturing_rules(d: JewelryDefinition) -> list[R.ValidationResult]:
    out: list[R.ValidationResult] = []

    if d.manufacturing.method != "direct_resin_printing":
        return out

    # setting.prongDiameter is excluded here: JM-PRONG-002 already errors
    # below 0.8 mm for prongs regardless of manufacturing method, so this
    # check only needs to cover dimensions with no stricter existing rule.
    structural_params = {
        "band.thickness": d.band.thickness,
        "band.width": d.band.width,
    }
    for parameter, value in structural_params.items():
        if value < 0.8:
            out.append(
                R.ValidationResult(
                    ruleId=R.MANUFACTURING_MIN_FEATURE,
                    severity="warning",
                    message=(
                        f"{parameter} is below 0.8 mm; direct resin printing may not "
                        "reliably resolve features this thin."
                    ),
                    parameter=parameter,
                    suggestedValue=0.8,
                )
            )

    return out


def _geometry_rules(d: JewelryDefinition) -> list[R.ValidationResult]:
    out: list[R.ValidationResult] = []

    outer_diameter = d.ring.innerDiameter + 2 * d.band.thickness
    if d.band.thickness <= 0 or outer_diameter <= d.ring.innerDiameter:
        out.append(
            R.ValidationResult(
                ruleId=R.GEOMETRY_OUTER_BAND_POSITIVE,
                severity="error",
                message="Band thickness must produce a positive outer band dimension.",
                parameter="band.thickness",
            )
        )

    if d.band.width <= 0:
        out.append(
            R.ValidationResult(
                ruleId=R.GEOMETRY_OUTER_BAND_POSITIVE,
                severity="error",
                message="Band width must be positive to produce valid band geometry.",
                parameter="band.width",
            )
        )

    return out


_RULE_GROUPS = (
    _ring_rules,
    _band_rules,
    _stone_rules,
    _prong_rules,
    _bezel_rules,
    _setting_rules,
    _manufacturing_rules,
    _geometry_rules,
)


def validate_definition(definition: JewelryDefinition) -> list[R.ValidationResult]:
    """Run every deterministic validation rule against `definition`.

    Returns the full, deterministically ordered list of results (errors,
    warnings, and information) — never raises for an invalid definition.
    Callers decide whether to block generation/export based on severities.
    """

    results: list[R.ValidationResult] = []
    for group in _RULE_GROUPS:
        results.extend(group(definition))
    return results


def has_errors(results: list[R.ValidationResult]) -> bool:
    return any(r.severity == "error" for r in results)
