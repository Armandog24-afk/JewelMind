"""Inspection version and kernel-tolerance constants.

`INSPECTION_VERSION` is independent of `GENERATOR_VERSION`
(`geometry/constants.py`) — a change to what inspection *measures* or how
it classifies a fact is a different axis of change than a change to what
geometry is *generated*. See
docs/bible/16-geometry-inspection/485-inspection-versioning.md.
"""

from __future__ import annotations

INSPECTION_VERSION = "1.0.0"

# A pure kernel/geometric contact tolerance — never a jewelry-domain
# tolerance. Two shapes are classified as touching/overlapping (as
# opposed to separated) when `Shape.distance()` reports at or below this
# value. OpenCascade's own default geometric confusion tolerance is
# 1e-7 mm; this is set one order of magnitude looser to stay robust to
# the small numerical noise real boolean/revolve operations can leave
# behind, while remaining many orders of magnitude tighter than any real
# jewelry dimension. See docs/bible/16-geometry-inspection/470-component-connectivity-model.md
# and INSPECT-GOV-012.
CONTACT_TOLERANCE_MM = 1e-6
