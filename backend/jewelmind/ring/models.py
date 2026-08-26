"""RingDefinition v2 — the internal, composable ring domain model.

Ring is one jewelry category (`jewelmind.jewelry_category`), composed
from reusable domain concepts rather than one monolithic solitaire
object — see docs/bible/18-ring-architecture/523-ring-definition-model.md.
Every sub-model states its real current implementation depth in its own
docstring (CURRENT/PARTIAL/PLANNED); nothing here invents geometry that
does not exist.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from jewelmind.domain.schema import BandProfile, BandTaperSpec, RingSizeSystem, SettingType, StoneSpec

#: The full recognized ring-family vocabulary — "solitaire" is CURRENT
#: (see families.py::RING_FAMILY_GENERATORS); every other value is a
#: reserved, PLANNED family name that proves RingDefinition v2 is not
#: solitaire-specific, never implemented this Sprint (brief section 10).
RingFamilyId = Literal[
    "solitaire",
    "three_stone",
    "toi_et_moi",
    "halo",
    "eternity",
    "signet",
    "plain_band",
    "cluster",
]

StoneArrangementType = Literal["SINGLE_CENTER"]


class RingModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RingSizing(RingModel):
    """CURRENT. Maps 1:1 from `JewelryDefinition.ring` — see
    525-ring-sizing-contract.md for the size/innerDiameter authority
    question this does not resolve, only documents."""

    sizeSystem: RingSizeSystem
    size: float
    innerDiameter: float


class ShankDefinition(RingModel):
    """CURRENT: uniform shank, plus real width/thickness taper (Sprint
    17). Maps 1:1 from `JewelryDefinition.band`. Future PLANNED
    variation: split, cathedral, knife-edge, Euro profiles — see
    docs/bible/19-shank/556-current-band-migration.md."""

    profile: BandProfile
    widthMm: float
    thicknessMm: float
    widthTaper: BandTaperSpec
    thicknessTaper: BandTaperSpec


class ShoulderDefinition(RingModel):
    """IMPLICIT/PARTIAL. The current solitaire has no independently
    modeled shoulder geometry — the shank flows directly into the head
    with no distinct transition component. This model exists so the
    contract has a real place to attach real geometry in a future
    sprint, not because current geometry has a shoulder to describe —
    see 527-shoulder-contract.md."""

    modeled: Literal[False] = False


class RingHeadDefinition(RingModel):
    """PARTIAL. The structural integration of the setting into the ring
    — currently just the basket support height. Deliberately excludes
    prong/setting fields, which belong to `SettingAttachmentDefinition`
    (a setting is reusable outside rings; how it attaches to a ring head
    is ring-specific) — see 528-head-contract.md."""

    basketHeightMm: float


class StoneArrangementDefinition(RingModel):
    """CURRENT (single center stone only). A potentially SHARED jewelry
    concept beyond rings — see 529-stone-arrangement-contract.md. Future
    PLANNED: MULTI_STONE, THREE_STONE, HALO, CLUSTER, PAVE_ARRAY."""

    arrangement: StoneArrangementType
    stone: StoneSpec


class SettingAttachmentDefinition(RingModel):
    """CURRENT (prong only). The setting itself, separated from how it
    structurally attaches to a ring head — see
    530-setting-attachment-contract.md."""

    settingType: SettingType
    prongCount: int
    prongDiameterMm: float
    prongHeightMm: float


class RingDefinition(RingModel):
    """The composed RingDefinition v2 — see 523-ring-definition-model.md.
    Built from a real `JewelryDefinition` by
    `jewelmind.ring.adapter.ring_definition_from_jdl()`; never
    hand-constructed from invented values."""

    family: RingFamilyId
    sizing: RingSizing
    shank: ShankDefinition
    shoulders: ShoulderDefinition
    head: RingHeadDefinition
    stoneArrangement: StoneArrangementDefinition
    setting: SettingAttachmentDefinition
