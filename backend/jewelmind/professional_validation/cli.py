"""`validate-review-record` — structural validation only, never a
judgment about whether professional feedback is correct.

Checks a candidate `ValidationRecord` JSON file for:
  - schema validity (every required field present, every enum value real);
  - the reviewer reference is a non-empty string (existence of a real
    reviewer profile is not checked here — this tool has no reviewer
    database to check against; see docs/bible/15-professional-validation/
    README.md for why that's an explicit, deliberate v1 scope limit);
  - target/version are present;
  - every `evidenceIds` entry is a non-empty string;
  - `decision` is one of the allowed `ValidationDecisionType` values;
  - `scope` is present (may be entirely empty — an unscoped record is
    valid, just maximally narrow in what it can be assumed to cover).

It never decides whether the feedback itself is correct — see item 49 of
the Sprint 13 brief.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from jewelmind.professional_validation.schemas import ValidationRecord


class ReviewRecordCheckResult:
    def __init__(self, valid: bool, errors: list[str], record: ValidationRecord | None):
        self.valid = valid
        self.errors = errors
        self.record = record


def validate_review_record_file(path: Path) -> ReviewRecordCheckResult:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return ReviewRecordCheckResult(False, [f"Could not read/parse JSON: {exc}"], None)

    return validate_review_record_dict(raw)


def validate_review_record_dict(raw: dict) -> ReviewRecordCheckResult:
    errors: list[str] = []
    try:
        record = ValidationRecord.model_validate(raw)
    except ValidationError as exc:
        for e in exc.errors():
            loc = ".".join(str(p) for p in e["loc"])
            errors.append(f"{loc}: {e['msg']}")
        return ReviewRecordCheckResult(False, errors, None)

    if not record.reviewerId.strip():
        errors.append("reviewerId must not be empty.")
    if not record.target.objectId.strip():
        errors.append("target.objectId must not be empty.")
    if not record.target.version.strip():
        errors.append("target.version must not be empty.")
    if any(not eid.strip() for eid in record.evidenceIds):
        errors.append("evidenceIds must not contain an empty string.")
    if record.decision in ("ACCEPTED_WITH_CONDITIONS",) and not (record.conditions or "").strip():
        errors.append("decision ACCEPTED_WITH_CONDITIONS requires non-empty conditions (PROVAL-GOV-010).")

    return ReviewRecordCheckResult(not errors, errors, record)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="validate-review-record")
    parser.add_argument("path", type=Path, help="Path to a candidate ValidationRecord JSON file.")
    args = parser.parse_args(argv)

    result = validate_review_record_file(args.path)
    if result.valid:
        print(f"OK: {args.path} is a structurally valid ValidationRecord.")
        return 0

    print(f"INVALID: {args.path}", file=sys.stderr)
    for error in result.errors:
        print(f"  - {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
