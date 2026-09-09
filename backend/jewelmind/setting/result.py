"""Building one setting family's result record (Sprint 27).

WHY THIS IS SHARED. Every generator returns a `SettingGeometryResult` carrying
the same six structural facts — which components it generated, which of those
are production metal, the component facts, the compatibility status, the
resolved mode and the provenance of each component. Sprint 19 and Sprint 23
each wrote that block by hand in one generator, which was fine at two
generators and would be six copies at six.

THE PROVENANCE IS BUILT HERE PRECISELY SO IT CANNOT BE FORGOTTEN. A generator
that returns a component without saying which mode, which stone and which
placements it came from ships an anonymous component, and
`test_extended_setting_modes.py` asserts every generated component has a
provenance row. Deriving both lists from the same argument makes that
impossible to get wrong in one direction only.

Nothing here builds or measures geometry: it takes already-built components and
records facts about them.
"""

from __future__ import annotations

from collections.abc import Sequence

from jewelmind.geometry.model import GeneratedComponent
from jewelmind.setting.models import (
    CompatibilityStatus,
    SettingComponentFact,
    SettingComponentProvenance,
    SettingDefinition,
    SettingGeometryResult,
)


def component_fact(component: GeneratedComponent) -> SettingComponentFact:
    """A kernel-neutral fact record for one generated component.

    Facts only — a count, a volume, a box. No judgement about whether any of
    them is good (SETTING-GOV-016).
    """

    box = component.bounding_box
    return SettingComponentFact(
        componentId=component.name,
        solidCount=len(component.shape.Solids()),
        volumeMm3=component.volume_mm3,
        boundingBoxMinMm=(box.xmin, box.ymin, box.zmin),
        boundingBoxMaxMm=(box.xmax, box.ymax, box.zmax),
    )


def family_result(
    definition: SettingDefinition,
    components: Sequence[GeneratedComponent],
    status: CompatibilityStatus,
    stone_instance_ids: Sequence[str] = (),
    diagnostics: Sequence[str] = (),
    **extra: object,
) -> SettingGeometryResult:
    """The result record for a family whose components are all production metal.

    `stone_instance_ids` are the arrangement instances this setting holds beyond
    the design's own stone. OPAQUE, carried and never resolved: nothing under
    `jewelmind/setting/` may import the arrangement layer
    (SETTINGV2-GOV-011), so the association is recorded and the arrangement
    stays the authority on where those instances are.

    `extra` carries the family-specific reported facts — requested-vs-generated
    counts, the bezel variant, the professional-review requirement. Passed
    through to the model rather than enumerated here so this helper does not
    have to grow a parameter every time a family reports one more number, and
    `extra="forbid"` on the model still rejects a typo.
    """

    names = [component.name for component in components]
    ids = sorted(set(stone_instance_ids))
    return SettingGeometryResult(
        settingId=definition.settingId,
        settingType=definition.settingType,
        generatedComponents=names,
        productionComponents=names,
        referenceComponents=[],
        attachmentInterfaces=[definition.attachment],
        geometryFacts=[component_fact(component) for component in components],
        diagnostics=list(diagnostics),
        compatibilityStatus=status,
        settingModeId=definition.settingModeId,
        settingModeFingerprint=definition.settingModeFingerprint,
        componentProvenance=[
            SettingComponentProvenance(
                componentId=name,
                settingModeId=definition.settingModeId,
                sourceStoneId=definition.stone.stoneId,
                sourceStoneInstanceIds=ids,
                classification="PRODUCTION",
            )
            for name in names
        ],
        stoneInstanceAssignments={name: ids for name in names},
        **extra,  # type: ignore[arg-type]
    )
