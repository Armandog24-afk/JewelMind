"""Small CadQuery edge selectors used by fragile cosmetic operations (fillets).

Kept separate from the component builders so a selector bug is easy to spot
and the builders stay readable.
"""

from __future__ import annotations

from cadquery import selectors


class FlatCircleAtRadius(selectors.Selector):
    """Selects circular edges lying in a Z-constant plane at a given radius.

    Used to fillet only the flat top/bottom rim edges of a revolved band,
    while excluding the vertical revolve seam edge (which is not flat).
    """

    def __init__(self, radius: float, tol: float = 1e-3):
        self.radius = radius
        self.tol = tol

    def filter(self, object_list):
        selected = []
        for obj in object_list:
            bb = obj.BoundingBox()
            r = max(bb.xmax, bb.zmax, -bb.xmin, -bb.zmin)
            is_flat = (bb.ymax - bb.ymin) < self.tol
            if is_flat and abs(r - self.radius) < self.tol:
                selected.append(obj)
        return selected
