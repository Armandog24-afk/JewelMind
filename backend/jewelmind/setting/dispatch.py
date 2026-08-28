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
from jewelmind.setting.errors import SettingTypeUnsupportedError
from jewelmind.setting.models import SettingDefinition, SettingGeometryResult

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
) -> tuple[dict[str, GeneratedComponent], SettingGeometryResult]:
    """Dispatch to the registered generator for `definition.settingType`."""

    generators = setting_generators()
    generator = generators.get(definition.settingType)
    if generator is None:
        raise SettingTypeUnsupportedError(
            f"No setting generator is registered for setting type "
            f"{definition.settingType!r}. Registered: {sorted(generators)}."
        )
    return generator(definition)
