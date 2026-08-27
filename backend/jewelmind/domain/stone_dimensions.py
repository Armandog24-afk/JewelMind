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


def resolved_length_mm(stone: StoneSpec) -> float:
    """Major horizontal dimension (local Y axis at orientation=0)."""

    if stone.shape == "round":
        assert stone.diameter is not None  # enforced by StoneSpec's own validator
        return stone.diameter
    assert stone.length is not None
    return stone.length


def resolved_width_mm(stone: StoneSpec) -> float:
    """Minor horizontal dimension (local X axis at orientation=0)."""

    if stone.shape == "round":
        assert stone.diameter is not None
        return stone.diameter
    assert stone.width is not None
    return stone.width


def resolved_depth_mm(stone: StoneSpec) -> float:
    """Vertical dimension (local Z axis) — identical field for every shape."""

    return stone.depth
