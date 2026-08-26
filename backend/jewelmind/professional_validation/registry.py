"""Loads and interprets the active professional-validation registry.

The active registry (`specs/professional-validation/v1/current-validation-registry.json`)
is the ONLY file this module ever reads to compute validated-rule/object
counts. Example and template `ValidationRecord` fixtures live under
`specs/professional-validation/v1/examples/` — a structurally separate
location — so they can never be accidentally counted here, and this
module additionally rejects any record it loads with `isTemplate=True` as
a second, independent guard (PROVAL-GOV-001).
"""

from __future__ import annotations

import json
from pathlib import Path

from jewelmind.professional_validation.errors import TemplateRecordInRegistryError
from jewelmind.professional_validation.schemas import ValidationRecord, ValidationStatus

_VALIDATED_STATUSES: frozenset[ValidationStatus] = frozenset({"VALIDATED", "VALIDATED_WITH_CONDITIONS"})


def registry_path() -> Path:
    """The real, single active registry file — repo-root-relative, resolved
    from this file's own location so it works regardless of the caller's
    current working directory."""

    return (
        Path(__file__).resolve().parents[3]
        / "specs"
        / "professional-validation"
        / "v1"
        / "current-validation-registry.json"
    )


def load_active_registry(path: Path | None = None) -> list[ValidationRecord]:
    """Loads every `ValidationRecord` in the active registry.

    Raises `TemplateRecordInRegistryError` if any loaded record is marked
    `isTemplate=True` — the active registry must never contain one.
    """

    resolved = path or registry_path()
    data = json.loads(resolved.read_text(encoding="utf-8"))
    records = [ValidationRecord.model_validate(entry) for entry in data.get("records", [])]
    for record in records:
        if record.isTemplate:
            raise TemplateRecordInRegistryError(
                f"Record '{record.recordId}' is marked isTemplate=True but was found in the "
                "active registry — templates/examples must never be counted as real validation."
            )
    return records


def count_by_status(records: list[ValidationRecord], status: ValidationStatus) -> int:
    return sum(1 for r in records if r.status == status)


def count_validated(records: list[ValidationRecord]) -> int:
    """The number of records whose status means "a real reviewer accepted
    this, unconditionally or with stated conditions" — VALIDATED and
    VALIDATED_WITH_CONDITIONS. Everything else (NOT_REVIEWED,
    REVIEW_PLANNED, UNDER_REVIEW, INSUFFICIENT_EVIDENCE, REJECTED,
    REVALIDATION_REQUIRED, SUPERSEDED) does not count."""

    return sum(1 for r in records if r.status in _VALIDATED_STATUSES)


def validated_object_ids(records: list[ValidationRecord]) -> list[str]:
    return [r.target.objectId for r in records if r.status in _VALIDATED_STATUSES]
