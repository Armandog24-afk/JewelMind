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

from jewelmind.domain.schema import (
    BandArchitecture,
    BandProfile,
    BandTaperSpec,
    RingSizeSystem,
    SettingType,
    StoneSpec,
)

#: The full recognized ring-family vocabulary.
#:
#: Sprint 16 introduced this with `solitaire` CURRENT and everything else a
#: reserved PLANNED name, to prove `RingDefinition` v2 was not
#: solitaire-specific. Sprint 28 made SIX of them real: `solitaire`,
#: `three_stone`, `halo`, `split_shank`, `bypass` and `signet` each have at
#: least one executable variant in `ring_family/models.py::VARIANT_FAMILY`, and
#: `families.py::RING_FAMILY_GENERATORS` dispatches every one.
#:
#: `toi_et_moi`, `eternity`, `plain_band` and `cluster` remain reserved with
#: real technical reasons in `ring_family/models.py::RESERVED_RING_FAMILIES` —
#: two of them because the capability already exists as a STONE family and a
#: ring family of the same name would be a second authority over one placement.
RingFamilyId = Literal[
    "solitaire",
    "three_stone",
    "halo",
    "split_shank",
    "bypass",
    "signet",
    # Reserved: recognized names with no generator. See
    # `ring_family/models.py::RESERVED_RING_FAMILIES` for each one's reason.
    "toi_et_moi",
    "eternity",
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
    """CURRENT: uniform, split and bypass shanks, plus real width/thickness
    taper. Maps 1:1 from `JewelryDefinition.band`.

    THE 1:1 CLAIM IS LOAD-BEARING, which is why the five architecture fields
    are here: Sprint 28 added them to `BandSpec` and left this model behind,
    making the docstring false until it was fixed. SHANK-GOV requires this
    mirror to move whenever `BandSpec` does, for exactly that reason.

    Still PLANNED: knife-edge and Euro profiles, and more than two rails — see
    docs/bible/19-shank/556-current-band-migration.md and
    docs/bible/30-ring-families/coverage-review.md.
    """

    profile: BandProfile
    widthMm: float
    thicknessMm: float
    widthTaper: BandTaperSpec
    thicknessTaper: BandTaperSpec

    #: Sprint 28. Normally DERIVED from the ring-family variant rather than set
    #: directly, which is why the ring family is the layer that decides them
    #: and this one only records what the document ended up saying.
    architecture: BandArchitecture = "UNIFORM"
    splitSeparationMm: float = 1.2
    splitJoinSpanDeg: float = 200.0
    bypassSeparationMm: float = 1.0
    bypassOverlapDeg: float = 60.0


class ShoulderDefinition(RingModel):
    """The shank-to-head transition.

    `modeled: False` was `Literal[False]` from Sprint 16 until Sprint 28,
    because the shank genuinely flowed straight into the head with no distinct
    transition component. Ring Families v2 gave the shoulder real geometry —
    `geometry/shoulder.py` builds two arches for a cathedral solitaire and four
    for a split shank — so the literal became a false claim and had to change
    rather than be documented around.

    STILL `False` FOR MOST DESIGNS, and that is the honest answer rather than a
    gap: a classic solitaire has no shoulder component, and reporting one would
    describe geometry that is not there. `architecture` names which builder
    produced it, or `NONE`.

    See 527-shoulder-contract.md and
    docs/bible/30-ring-families/execution-boundary.md.
    """

    #: Whether this design has an independently modeled shoulder component.
    modeled: bool = False

    #: The shoulder architecture that built it, or `NONE`. Read from the
    #: resolved ring family rather than inferred, so it cannot disagree with the
    #: component that was actually generated.
    architecture: Literal["NONE", "CATHEDRAL", "SPLIT_RAILS"] = "NONE"


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
