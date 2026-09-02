"""Structured Stone System v2 errors (brief sections 51/52).

Every error carries a stable `code`, following the convention established by
`jewelmind/setting/errors.py`. Codes are published contract: never rename or
reuse one (JDL-GOV-007's discipline, applied here).

No error message here may embed a parser stack trace, an internal server path,
or raw importer output (brief section 50; FOUNDRY-GOV-011). Import failures
carry a short, sanitized reason; the underlying exception is chained with
`raise ... from exc` so it stays available in server logs without reaching a
client response.
"""

from __future__ import annotations


class StoneError(Exception):
    """Base class for every Stone System error."""

    code = "STONE_ERROR"


# --------------------------------------------------------------- native shapes
class StoneShapeUnsupportedError(StoneError):
    """No registered generator for the requested shape."""

    code = "STONE_SHAPE_UNSUPPORTED"


class StoneShapeGenerationFailedError(StoneError):
    """A real construction failure. Raised rather than silently substituting a
    different shape (STONE-GOV-007/013)."""

    code = "STONE_SHAPE_GENERATION_FAILED"


class StoneShapeDimensionsInvalidError(StoneError):
    """Dimensions are missing, non-finite, or geometrically unusable for the
    requested shape (e.g. a tapered shape whose narrow width exceeds its wide
    width)."""

    code = "STONE_SHAPE_DIMENSIONS_INVALID"


class StoneProfileUnsupportedError(StoneError):
    """No registered builder for the requested 3D reference profile."""

    code = "STONE_PROFILE_UNSUPPORTED"


class StoneShapeProfileCombinationUnsupportedError(StoneError):
    """The outline shape and the 3D profile are each supported, but not in
    combination. Kept distinct from the two single-axis errors so a caller can
    tell "this profile does not exist" from "this profile does not apply to
    this outline"."""

    code = "STONE_SHAPE_PROFILE_COMBINATION_UNSUPPORTED"


# ------------------------------------------------------------- custom outlines
class CustomOutlineInvalidError(StoneError):
    """A custom outline failed validation. Never repaired silently
    (brief section 24)."""

    code = "CUSTOM_OUTLINE_INVALID"


class CustomOutlineSelfIntersectionError(CustomOutlineInvalidError):
    """A custom outline crosses itself. A subclass of the general invalid-outline
    error so a caller may catch either the specific or the general case."""

    code = "CUSTOM_OUTLINE_SELF_INTERSECTION"


# ------------------------------------------------------------- measured stones
class MeasuredStoneInsufficientDataError(StoneError):
    """A measured stone lacks the measurements needed to build any reference
    geometry. JewelMind never invents a missing measurement
    (STONEV2-GOV-006)."""

    code = "MEASURED_STONE_INSUFFICIENT_DATA"


# ------------------------------------------------------------- imported stones
class StoneSourceUnsupportedError(StoneError):
    """No registered handler for the requested `StoneSourceMode`."""

    code = "STONE_SOURCE_UNSUPPORTED"


class StoneImportFormatUnsupportedError(StoneError):
    """The file extension is not one this build can actually parse. Never
    claimed for a format the installed kernel cannot read (brief section 30)."""

    code = "STONE_IMPORT_FORMAT_UNSUPPORTED"


class StoneImportFailedError(StoneError):
    """The importer could not read the file. The message is sanitized."""

    code = "STONE_IMPORT_FAILED"


class StoneImportEmptyError(StoneError):
    """The file parsed, but contains no usable geometry."""

    code = "STONE_IMPORT_EMPTY"


class StoneImportUnitsUnknownError(StoneError):
    """Units could not be established and the caller did not declare them.
    JewelMind never guesses a unit (FOUNDRY-GOV-012, brief section 31)."""

    code = "STONE_IMPORT_UNITS_UNKNOWN"


class StoneImportGeometryInvalidError(StoneError):
    """The imported geometry parsed but is not usable as a stone reference
    (invalid topology, zero volume, non-finite bounds)."""

    code = "STONE_IMPORT_GEOMETRY_INVALID"


class StoneImportTooComplexError(StoneError):
    """The asset exceeds a declared resource limit (file size, triangle count,
    or face count). A safeguard against untrusted input, not a quality
    judgment (brief section 50)."""

    code = "STONE_IMPORT_TOO_COMPLEX"


class StoneImportOutlineUnavailableError(StoneError):
    """A usable girdle outline could not be derived from the imported
    geometry. Reported honestly rather than fabricating one
    (brief section 44)."""

    code = "STONE_IMPORT_OUTLINE_UNAVAILABLE"
