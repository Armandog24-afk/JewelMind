"""Canonical Stone dimension resolution (STONE-GOV-005/006) — lives in the
`domain/` layer (not `geometry/` or `validation/`) specifically so both
Atlas geometry construction (`geometry/stone/builder.py`,
`geometry/constants.py::prong_center_radius()`) and Forge validation
(`validation/engine.py::_stone_rules()`) can depend on it without
creating a Forge -> Atlas or Atlas -> Forge coupling that didn't exist
before this Sprint — `domain/` is the one layer both already depend on.

Separates the public JDL `StoneSpec` fields (which differ by shape for
backward compatibility: `round` keeps `diameter`, every other shape uses
`length`/`width`) from the single, deterministic geometric contract every
other module actually consumes.

LENGTH is the major horizontal dimension (mapped to the local Y axis, the
same axis the band revolves around — see
docs/bible/20-stone/565-stone-coordinate-and-orientation.md). WIDTH is the
minor horizontal dimension (local X axis). DEPTH is always the vertical
dimension (local Z axis), unchanged from pre-Sprint-18 behavior.

For `round`, `length == width == diameter` — a real, documented internal
normalization (STONE-GOV-005: shape and dimensions are separate concepts;
this is what lets every other module treat every shape uniformly without
special-casing round).
"""

from __future__ import annotations

from jewelmind.domain.schema import StoneSpec

#: Shapes whose single horizontal size is a diameter. `pearl` joins `round`
#: here: a sphere has one horizontal size, not two.
_ROUND_LIKE: frozenset[str] = frozenset({"round", "pearl"})


def _custom_outline_extents_mm(stone: StoneSpec) -> tuple[float, float]:
    """Length and width of a custom outline, straight from its own points.

    Computed here rather than delegated so that this module stays free of any
    geometry-kernel import — Forge depends on it, and Forge must never pull in
    CadQuery. The arithmetic is a bounding box over already-declared points, so
    it is exact and needs no kernel.
    """

    from jewelmind.stone.models import UNIT_TO_MM

    outline = stone.customOutline
    if outline is None:  # pragma: no cover - guarded by StoneSpec's validator
        raise StoneDimensionsUnavailableError(
            "A custom-outline stone has no outline to derive dimensions from."
        )
    factor = UNIT_TO_MM[outline.unit]
    xs = [p.x * factor for p in outline.points]
    ys = [p.y * factor for p in outline.points]
    return max(ys) - min(ys), max(xs) - min(xs)


class StoneDimensionsUnavailableError(Exception):
    """A stone's dimensions cannot be determined from the design document alone.

    Raised only for `IMPORTED_CAD`, where the true dimensions are a property of
    the imported asset rather than of the document. Callers that need them must
    read the normalized stone definition, which carries the real measured
    values. Raised rather than guessed: inventing a size for an imported stone
    would silently misplace every component built around it.
    """

    code = "STONE_DIMENSIONS_UNAVAILABLE"


def resolved_length_mm(stone: StoneSpec) -> float:
    """Major horizontal dimension (local Y axis at orientation=0)."""

    if stone.source == "CUSTOM_OUTLINE":
        return _custom_outline_extents_mm(stone)[0]
    if stone.source == "IMPORTED_CAD":
        raise StoneDimensionsUnavailableError(
            "An imported stone's length comes from the imported asset, not from "
            "the design document."
        )
    if stone.shape in _ROUND_LIKE:
        assert stone.diameter is not None  # enforced by StoneSpec's own validator
        return stone.diameter
    assert stone.length is not None
    return stone.length


def resolved_width_mm(stone: StoneSpec) -> float:
    """Minor horizontal dimension (local X axis at orientation=0)."""

    if stone.source == "CUSTOM_OUTLINE":
        return _custom_outline_extents_mm(stone)[1]
    if stone.source == "IMPORTED_CAD":
        raise StoneDimensionsUnavailableError(
            "An imported stone's width comes from the imported asset, not from "
            "the design document."
        )
    if stone.shape in _ROUND_LIKE:
        assert stone.diameter is not None
        return stone.diameter
    assert stone.width is not None
    return stone.width


def resolved_depth_mm(stone: StoneSpec) -> float:
    """Vertical dimension (local Z axis) — identical field for every shape.

    A pearl's depth IS its diameter: reporting a separately-supplied `depth`
    for a sphere would describe geometry that is not built.
    """

    if stone.source == "IMPORTED_CAD":
        raise StoneDimensionsUnavailableError(
            "An imported stone's depth comes from the imported asset, not from "
            "the design document."
        )
    if stone.shape == "pearl" and stone.diameter is not None:
        return stone.diameter
    return stone.depth
