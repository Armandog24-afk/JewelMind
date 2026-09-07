"""Stone components for a resolved arrangement (Sprint 24).

The bridge between "one built stone" and "the stone components this model has".
Given the stone the builder produced and the compiled arrangement, it returns
one component per GENERATED instance, each placed by
`geometry/stone/instance.py` and named by the arrangement's own naming
contract.

WHY THE SAME BUILT SOLID IS REUSED. Every instance resolving the `primary`
stone specification is an occurrence OF that stone, so rebuilding it per
instance would repeat identical kernel work and — worse — risk two occurrences
of "the same stone" differing in the last bits. The solid is built once and
placed many times, which is also why a member's `scale` is a transform rather
than a different set of stone dimensions.

NO ARRANGEMENT MEANS ONE COMPONENT, returned unplaced. That is the whole
single-stone compatibility story: the historical `stone_reference` name, the
builder's own shape object, no transform applied.
"""

from __future__ import annotations

from typing import Any

from jewelmind.geometry.model import GeneratedComponent
from jewelmind.geometry.stone.instance import place_stone_instance

#: The component name a single-stone design's stone takes. Duplicated as a
#: literal rather than imported from `jewelmind.arrangement.compile`, because
#: `geometry.stone` must not depend on the arrangement package for a string —
#: `test_multi_stone_families.py` asserts the two agree.
PRIMARY_STONE_COMPONENT = "stone_reference"


def stone_components(
    stone: GeneratedComponent,
    arrangement_result: Any | None,
) -> dict[str, GeneratedComponent]:
    """One component per generated stone instance.

    `arrangement_result` is typed `Any` for the same reason `GeneratedModel`
    types it that way: this module must not import `jewelmind.arrangement`. The
    concrete type is `ResolvedArrangement`.

    An instance reported `NOT_GENERATED` produces no component and is not
    silently turned into one — its reason is already recorded on the resolved
    arrangement (ARRANGE-GOV-009).
    """

    if arrangement_result is None:
        return {PRIMARY_STONE_COMPONENT: stone}

    components: dict[str, GeneratedComponent] = {}
    for instance in arrangement_result.instances:
        if instance.generationStatus != "GENERATED":
            continue
        name = instance.componentName or PRIMARY_STONE_COMPONENT
        components[name] = place_stone_instance(
            stone,
            name,
            x_mm=instance.transform.xMm,
            y_mm=instance.transform.yMm,
            z_mm=instance.transform.zMm,
            rotation_deg=instance.transform.rotationDeg,
            scale=instance.overrides.scale,
            orientation_deg=instance.overrides.orientationDeg,
            instance_id=instance.instanceId,
            role=instance.role,
        )

    if not components:
        # An arrangement that generated nothing still leaves the design with its
        # stone: returning an empty map would drop the stone entirely, which is
        # a silently smaller model rather than an honest one.
        return {PRIMARY_STONE_COMPONENT: stone}
    return components
