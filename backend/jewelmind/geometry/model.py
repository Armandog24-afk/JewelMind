"""Structured result types returned by the geometry builders."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import cadquery as cq


@dataclass(frozen=True)
class BoundingBox:
    xmin: float
    xmax: float
    ymin: float
    ymax: float
    zmin: float
    zmax: float

    @classmethod
    def from_shape(cls, shape: cq.Shape) -> BoundingBox:
        bb = shape.BoundingBox()
        return cls(bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)

    def union(self, other: BoundingBox) -> BoundingBox:
        return BoundingBox(
            xmin=min(self.xmin, other.xmin),
            xmax=max(self.xmax, other.xmax),
            ymin=min(self.ymin, other.ymin),
            ymax=max(self.ymax, other.ymax),
            zmin=min(self.zmin, other.zmin),
            zmax=max(self.zmax, other.zmax),
        )

    def as_dict(self) -> dict[str, float]:
        return {
            "xmin": self.xmin,
            "xmax": self.xmax,
            "ymin": self.ymin,
            "ymax": self.ymax,
            "zmin": self.zmin,
            "zmax": self.zmax,
        }


@dataclass
class GeneratedComponent:
    """One named solid produced by a geometry builder function."""

    name: str
    shape: cq.Shape
    volume_mm3: float
    bounding_box: BoundingBox
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GeneratedModel:
    """The full solitaire ring assembly plus its metadata."""

    definition_hash: str
    generator_version: str
    generation_duration_s: float
    components: dict[str, GeneratedComponent]
    combined_metal: cq.Shape
    combined_metal_volume_mm3: float
    bounding_box: BoundingBox
    warnings: list[str]
    #: The structured Setting System outcome (Sprint 19). Typed as `Any` to
    #: keep this dataclass free of a `jewelmind.setting` import — the
    #: concrete type is `jewelmind.setting.models.SettingGeometryResult`.
    #: Optional so any caller constructing a `GeneratedModel` directly
    #: (fixtures, test doubles) keeps working.
    setting_result: Any = None

    #: Identity of the GEOMETRY alone, excluding fields that provably do not
    #: drive it (gem identity, metal, manufacturing method, project name, mesh
    #: tolerances — each exclusion verified by generating geometry with it
    #: varied, see `utils/hashing.py`). Two definitions differing only by gem
    #: share this hash, which is what lets built geometry be reused across a
    #: purely semantic edit (Sprint 21, brief section 19).
    #:
    #: Placed last, with a default, because this is a dataclass: a defaulted
    #: field cannot precede a required one. Empty means "not computed", which
    #: is what a hand-constructed test fixture produces.
    geometry_hash: str = ""

    def component_volumes(self) -> dict[str, float]:
        return {name: c.volume_mm3 for name, c in self.components.items()}
