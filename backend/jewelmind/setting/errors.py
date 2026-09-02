"""Structured Setting System errors (brief section 50).

Aligned with the existing domain-error conventions: every error carries a
stable, documented code and a human-readable message that never embeds a
kernel stack trace. The API layer maps these the same way it maps every
other domain error.
"""

from __future__ import annotations


class SettingError(Exception):
    """Base class so callers can catch the whole family."""

    code = "SETTING_ERROR"


class SettingTypeUnsupportedError(SettingError):
    """No generator is registered for the requested `setting.type`
    (SETTING-GOV-012). Should be unreachable via JDL, since `SettingType`
    is a closed enum — kept as a real explicit guard rather than an
    implicit `KeyError`."""

    code = "SETTING_TYPE_UNSUPPORTED"


class SettingStoneCombinationUnsupportedError(SettingError):
    """The requested Setting family cannot be generated for this stone
    shape (SETTING-GOV-012). Raised rather than silently substituting a
    different setting family (SETTING-GOV-013)."""

    code = "SETTING_STONE_COMBINATION_UNSUPPORTED"


class SettingGenerationFailedError(SettingError):
    """A real kernel construction failure. Never downgraded to another
    setting family or to an empty component (SETTING-GOV-013)."""

    code = "SETTING_GENERATION_FAILED"


class SettingPlacementFailedError(SettingError):
    """A placement strategy could not produce positions for the requested
    stone/prong-count combination."""

    code = "SETTING_PLACEMENT_FAILED"


class BezelOutlineFailedError(SettingGenerationFailedError):
    """The stone outline could not be offset into a usable bezel path."""

    code = "BEZEL_OUTLINE_FAILED"


class BezelSolidInvalidError(SettingGenerationFailedError):
    """The bezel wall produced no solid, or an invalid one."""

    code = "BEZEL_SOLID_INVALID"


class SettingCapabilityMismatchError(SettingError):
    """A caller asked for a capability the registry does not mark
    generatable (SETTING-GOV-005/006)."""

    code = "SETTING_CAPABILITY_MISMATCH"


class StoneOutlineUnavailableError(SettingError):
    """No usable girdle outline could be obtained for a stone.

    Raised rather than substituting an approximation. A stone with no planar
    outline (the spherical pearl reference) or one whose outline the Stone
    System could not derive genuinely cannot be set by the current
    outline-driven families, and saying so is the honest answer
    (SETTING-GOV-013: never silently substitute).
    """

    code = "STONE_OUTLINE_UNAVAILABLE"
