"""The explicit Shank -> RingHead connection interface (SHANK-GOV-010, see
docs/bible/19-shank/550-head-connection-interface.md).

Lives in the Atlas geometry layer, not `jewelmind.ring` — `prongs.py`/
`basket.py` are Atlas-layer component builders (Sprint 5) that must not
depend on the higher-level Ring domain package, matching the same
layering `jewelmind.geometry.constants` already has (Ring depends on
Atlas, never the reverse). Before Sprint 17, `prongs.py`/`basket.py` each
independently imported `band_top_z()`/`prong_center_radius()` — real,
correct values, but reached through two separate, unrelated names rather
than one explicit interface. This module is a thin, behavior-preserving
re-export: the underlying computation is unchanged, but Shank -> RingHead
geometry integration now has one real name to read.

Every field here stays exact for a tapered Shank too — see
docs/bible/19-shank/548-taper-model.md: taper always preserves the full
base width/thickness exactly at the head (u=0), so `topZMm` never moves
when a taper is requested.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from jewelmind.domain.schema import JewelryDefinition
from jewelmind.geometry.constants import EMBED_MM, band_top_z, prong_center_radius


class ShankConnectionInterface(BaseModel):
    model_config = ConfigDict(extra="forbid")

    topZMm: float
    embedMm: float
    headCenterRadiusMm: float


def shank_connection_interface(definition: JewelryDefinition) -> ShankConnectionInterface:
    return ShankConnectionInterface(
        topZMm=band_top_z(definition),
        embedMm=EMBED_MM,
        headCenterRadiusMm=prong_center_radius(definition),
    )
