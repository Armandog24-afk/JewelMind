"""Classifies the impact of a rule/object version change on an existing
professional validation record.

See docs/bible/15-professional-validation/432-validation-versioning.md and
docs/bible/06-forge/103-professional-validation-lifecycle.md's existing
rule: "A MAJOR change to a validated rule ... invalidates that specific
validation record — the rule reverts to preliminary until re-reviewed at
the new version." This module makes that rule a real, testable function
instead of prose alone.
"""

from __future__ import annotations

from typing import Literal

VersionImpact = Literal["VALIDATION_VERSION_UNCHANGED", "REVIEW_REQUIRED", "REVALIDATION_REQUIRED"]


def _parts(version: str) -> tuple[str, ...]:
    return tuple(version.split("."))


def classify_version_impact(validated_version: str, current_version: str) -> VersionImpact:
    """Classifies what a version change means for a record validated at
    `validated_version`, given the object is now at `current_version`.

    - Identical version -> VALIDATION_VERSION_UNCHANGED: the record still
      applies as-is.
    - Same MAJOR component, different version -> REVIEW_REQUIRED: a human
      should confirm the change (e.g. wording/documentation) didn't affect
      what was actually validated, but this function never assumes that on
      its own.
    - Different MAJOR component -> REVALIDATION_REQUIRED: per Forge's own
      MAJOR-version-change rule, a validated record never survives a MAJOR
      change automatically.

    This function only compares version strings — it has no opinion on
    whether a specific change is actually safe; that judgment belongs to
    engineering/domain review (see
    docs/bible/15-professional-validation/434-implementation-change-impact.md).
    """

    if validated_version == current_version:
        return "VALIDATION_VERSION_UNCHANGED"

    validated_parts = _parts(validated_version)
    current_parts = _parts(current_version)
    if validated_parts[0] != current_parts[0]:
        return "REVALIDATION_REQUIRED"
    return "REVIEW_REQUIRED"
