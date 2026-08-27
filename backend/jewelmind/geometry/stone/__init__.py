"""Stone System v1 (Sprint 18) — real, deterministic CAD reference geometry
for 7 stone shapes. Category-neutral: this package and everything under it
never imports `jewelmind.ring` (STONE-GOV-001, verified by
`backend/tests/test_stone_system_no_ring_dependency.py`).

Deliberately does NOT eagerly import `builder.py` here: `builder.py`
depends on `geometry.constants` (for `band_top_z`), and `geometry.constants`
itself depends on `geometry.stone.dimensions` (for `resolved_width_mm`,
used by `prong_center_radius()`) — an eager import here would recreate
exactly the circular-import bug Sprint 17 already fixed once for
`geometry/connection.py`. Import `jewelmind.geometry.stone.builder`
directly instead of `jewelmind.geometry.stone`.

See docs/bible/20-stone/README.md.
"""

from __future__ import annotations
