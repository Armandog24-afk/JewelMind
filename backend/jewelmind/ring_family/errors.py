"""Structured Ring Family errors (Sprint 28).

Aligned with the existing domain-error conventions: every error carries a
stable, documented code and a human-readable message that never embeds a kernel
stack trace or a server path.
"""

from __future__ import annotations


class RingFamilyError(Exception):
    """Base class so callers can catch the whole family."""

    code = "RING_FAMILY_ERROR"


class RingFamilyVariantMismatchError(RingFamilyError):
    """The declared variant belongs to a different family than
    `jewelry.style` names.

    Refused rather than resolved by precedence: two authorities over one family
    have no determinate resolution, the same reason `JM-FAMILY-001` refuses a
    stone family and an arrangement together.
    """

    code = "RING_FAMILY_VARIANT_MISMATCH"


class RingFamilyUnsupportedVariantError(RingFamilyError):
    """The requested variant has no derivation.

    Should be unreachable via JDL, since `RingFamilyVariantId` is a closed enum
    — kept as a real explicit guard rather than an implicit `KeyError`.
    """

    code = "RING_FAMILY_VARIANT_UNSUPPORTED"


class RingFamilyDerivationConflictError(RingFamilyError):
    """The family would derive a block the document already declares itself.

    Raised rather than overwriting: a family that silently replaced an author's
    own halo or stone family would discard what they wrote, and a family that
    silently skipped its own derivation would report a variant it did not build.
    The caller has to choose.
    """

    code = "RING_FAMILY_DERIVATION_CONFLICT"


class RingFamilyGeometryUnsupportedError(RingFamilyError):
    """A requested configuration cannot be built.

    Raised rather than degrading to a nearby family, which would report one
    structure and deliver another (SETTING-GOV-013's discipline, restated for
    ring structure).
    """

    code = "RING_FAMILY_GEOMETRY_UNSUPPORTED"
