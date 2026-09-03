"""Structured Gem Identity errors.

Stable `code` attributes, following the convention established by
`jewelmind/setting/errors.py` and `jewelmind/stone/errors.py`. A published code
is contract: never rename or reuse one.

NOTE WHAT IS *NOT* AN ERROR HERE. An unresolvable gem ID does not raise — a
saved project referencing a removed entry must still load, resolving to
`unknown` with an observable `wasUnresolved` flag (brief sections 10/29). These
errors are for malformed input and incoherent state, not for absent data.
"""

from __future__ import annotations


class GemError(Exception):
    """Base class for every Gem Identity error."""

    code = "GEM_ERROR"


class GemIdInvalidError(GemError):
    """A gem ID is malformed.

    IDs are constrained so they can never become a filesystem path or a shell
    argument (brief section 37).
    """

    code = "GEM_ID_INVALID"


class GemNotFoundError(GemError):
    """A gem ID was required to exist and does not.

    Raised only by callers that genuinely need a real entry — an explicit
    lookup or a validation request. Normal resolution degrades to `unknown`
    instead.
    """

    code = "GEM_NOT_FOUND"


class GemOriginInvalidError(GemError):
    """The declared origin is not applicable to this gem type.

    Example: a cubic zirconia declared `NATURAL`. Refused rather than corrected,
    because correcting it would mean deciding what the user meant.
    """

    code = "GEM_ORIGIN_INVALID"


class GemIdentityIncoherentError(GemError):
    """The identity contradicts itself.

    Example: a `custom` gem with no `customName`, or a named non-custom gem.
    """

    code = "GEM_IDENTITY_INCOHERENT"


class GemTreatmentInvalidError(GemError):
    """A treatment record is malformed — most often `OTHER` with no note."""

    code = "GEM_TREATMENT_INVALID"


class GemVisualProfileNotFoundError(GemError):
    """A visual profile was required to exist and does not.

    Rendering never raises this: `get_visual_profile()` degrades to the generic
    fallback. It exists for validation, where an unresolvable reference is worth
    reporting.
    """

    code = "GEM_VISUAL_PROFILE_NOT_FOUND"
