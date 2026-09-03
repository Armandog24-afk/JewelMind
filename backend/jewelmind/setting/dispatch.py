"""Setting generator registry and dispatch (brief section 49).

A real registry, not an `if setting == ...` chain. Only implemented
families are registered — no placeholder entries for reserved families
(SETTING-GOV-005), so an unregistered type is a genuine, explicit error
rather than a silently empty setting (SETTING-GOV-012/013).

Built lazily inside a cached function rather than as a module-level
constant, matching the discipline
`jewelmind/jewelry_category/dispatch.py` adopted after a real
package-init circular import.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import lru_cache

from jewelmind.geometry.model import GeneratedComponent
from jewelmind.setting.errors import (
    SettingGenerationFailedError,
    SettingTypeUnsupportedError,
)
from jewelmind.setting.models import (
    SettingComponentFact,
    SettingDefinition,
    SettingGeometryResult,
)

SettingGenerator = Callable[
    [SettingDefinition], tuple[dict[str, GeneratedComponent], SettingGeometryResult]
]


@lru_cache(maxsize=1)
def setting_generators() -> dict[str, SettingGenerator]:
    from jewelmind.setting.bezel import generate_bezel_setting
    from jewelmind.setting.prong import generate_prong_setting

    return {
        "prong": generate_prong_setting,
        "bezel": generate_bezel_setting,
    }


def generate_setting(
    definition: SettingDefinition,
    stone_shape: object | None = None,
) -> tuple[dict[str, GeneratedComponent], SettingGeometryResult]:
    """Generate one complete setting: its family components, its head, its seat.

    THE SINGLE ENTRY POINT, extended additively in Sprint 23. A caller that
    passes only a definition with no `head` and no `seat` gets exactly the
    pre-Sprint-23 result, which is what keeps every existing caller and every
    Golden baseline unchanged.

    `stone_shape` is a KERNEL OBJECT passed as an ARGUMENT, never stored on a
    domain model. `SettingDefinition` stays kernel-neutral (SETTING-GOV, and the
    reason `stone_interface.py` already takes a `GeneratedComponent` rather than
    embedding one). It is needed only for seat relief, and only because relief
    is a boolean cut against the real generated stone rather than against an
    approximation of it.
    """

    generators = setting_generators()
    generator = generators.get(definition.settingType)
    if generator is None:
        raise SettingTypeUnsupportedError(
            f"No setting generator is registered for setting type "
            f"{definition.settingType!r}. Registered: {sorted(generators)}."
        )

    components, result = generator(definition)

    # HEAD (Sprint 23). Built only when the setting was asked for one. `None`
    # means the category integration builds its own support, which is what
    # every pre-Sprint-23 caller did — producing a head here regardless would
    # give those callers two.
    if definition.head is not None:
        from jewelmind.setting.head import HEAD_COMPONENT, build_head

        head_component = build_head(definition.head, definition.attachment)
        components = {**components, HEAD_COMPONENT: head_component}
        result = result.model_copy(
            update={
                "generatedComponents": [*result.generatedComponents, HEAD_COMPONENT],
                "productionComponents": [
                    *result.productionComponents,
                    HEAD_COMPONENT,
                ],
                "geometryFacts": [
                    *result.geometryFacts,
                    _component_fact(head_component),
                ],
                "headArchitecture": definition.head.architecture,
            }
        )

    # SEAT (Sprint 23). A CUT of the stone out of the metal, never a fuse — see
    # `seat.py`'s docstring for why that distinction is load-bearing.
    seat = definition.seat
    if seat is not None and seat.mode != "NONE":
        if stone_shape is None:
            raise SettingGenerationFailedError(
                f"Seat mode {seat.mode!r} was requested without the generated "
                "stone shape. Raised rather than skipping relief, which would "
                "report a seat that is not there."
            )
        from jewelmind.setting.seat import apply_seat_relief

        relieved: dict[str, GeneratedComponent] = {}
        diagnostics: list[str] = list(result.diagnostics)
        for name, component in components.items():
            if name not in result.productionComponents:
                # Only production metal is relieved. A reference component has
                # no metal to remove, and cutting one would be meaningless.
                relieved[name] = component
                continue
            updated, notes = apply_seat_relief(component, stone_shape, seat)
            relieved[name] = updated
            diagnostics.extend(notes)

        components = relieved
        result = result.model_copy(
            update={
                "geometryFacts": [
                    _component_fact(components[fact.componentId])
                    if fact.componentId in components
                    else fact
                    for fact in result.geometryFacts
                ],
                "diagnostics": diagnostics,
                "seatMode": seat.mode,
            }
        )

    return components, result


def _component_fact(component: GeneratedComponent) -> SettingComponentFact:
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
