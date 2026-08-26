"""The Golden regression harness (QUALITY-GOV-015). Every function here
runs the real JDL -> validation -> geometry -> inspection pipeline; none
of them ever mock geometry, and none of them ever write to a Golden
baseline file except `accept_candidate_baseline`, which only ever runs
when a human explicitly calls it (QUALITY-GOV-003/004).
"""

from __future__ import annotations

from datetime import UTC, datetime

from jewelmind.geometry_quality.artifact_regression import (
    step_roundtrip_check,
    stl_structure_check,
)
from jewelmind.geometry_quality.compare import compare_snapshot
from jewelmind.geometry_quality.fingerprint import collect_fingerprint
from jewelmind.geometry_quality.models import (
    ArtifactExpectation,
    GoldenModel,
    QualityResult,
)
from jewelmind.geometry_quality.registry import list_golden_ids, load_design, load_golden
from jewelmind.geometry_quality.snapshot import generate_snapshot

DEFAULT_ARTIFACT_EXPECTATIONS = [
    ArtifactExpectation(artifactType="STEP", nonEmpty=True, minSolidCount=1),
    ArtifactExpectation(artifactType="STL", nonEmpty=True),
    ArtifactExpectation(artifactType="JSON", nonEmpty=True),
    ArtifactExpectation(artifactType="SPECIFICATION", nonEmpty=True),
]


def verify_golden(golden_id: str, *, check_artifacts: bool = False) -> QualityResult:
    try:
        golden = load_golden(golden_id)
    except FileNotFoundError:
        return QualityResult(
            goldenId=golden_id,
            status="BASELINE_MISSING",
            diff=None,
            message=f"No accepted baseline exists for '{golden_id}'; run generate-candidate then accept.",
        )

    design = load_design(golden_id)
    try:
        snapshot, model, _report = generate_snapshot(design)
    except Exception as exc:  # noqa: BLE001 - report, never crash the harness
        return QualityResult(goldenId=golden_id, status="ERROR", diff=None, message=str(exc))

    actual_fingerprint = collect_fingerprint(model)
    diff = compare_snapshot(
        golden_id, golden.geometrySnapshot, snapshot, golden.versionFingerprint, actual_fingerprint
    )

    if check_artifacts:
        diff.artifactChanges += step_roundtrip_check(model)
        diff.artifactChanges += stl_structure_check(model, design)
        # An artifact regression is always at least as severe as REGRESSION,
        # regardless of what the geometric comparison alone found (e.g. an
        # INFO-level numeric change must not mask a real artifact defect).
        if diff.artifactChanges and diff.severity in ("NONE", "INFO"):
            diff.severity = "REGRESSION"
            diff.requiresBaselineReview = True

    if diff.severity == "REGRESSION":
        status = "REGRESSION_DETECTED"
    elif diff.severity == "VERSION_REVIEW_REQUIRED":
        status = "VERSION_REVIEW_REQUIRED"
    elif golden.knownLimitations:
        status = "PASS_WITH_KNOWN_LIMITATIONS"
    else:
        status = "PASS"

    return QualityResult(
        goldenId=golden_id,
        status=status,
        diff=diff,
        message=diff.human_readable(),
    )


def verify_all_goldens(*, check_artifacts: bool = False) -> list[QualityResult]:
    return [verify_golden(golden_id, check_artifacts=check_artifacts) for golden_id in list_golden_ids()]


def generate_candidate_baseline(golden_id: str) -> GoldenModel:
    """Builds a candidate baseline from the CURRENT real pipeline. Returns
    it — never writes it to disk. See 507-golden-update-policy.md."""

    design = load_design(golden_id)
    try:
        existing: GoldenModel | None = load_golden(golden_id)
    except FileNotFoundError:
        existing = None

    snapshot, model, _report = generate_snapshot(design)
    fingerprint = collect_fingerprint(model)

    return GoldenModel(
        goldenId=golden_id,
        description=existing.description if existing else f"Candidate baseline for {golden_id}.",
        sourceJDLPath=f"goldens/solitaire-v1/{golden_id}/design.json",
        definitionHash=model.definition_hash,
        versionFingerprint=fingerprint,
        expectedComponents=sorted(c.componentId for c in snapshot.components),
        geometrySnapshot=snapshot,
        artifactExpectations=existing.artifactExpectations if existing else DEFAULT_ARTIFACT_EXPECTATIONS,
        baselineStatus="CANDIDATE",
        knownLimitations=existing.knownLimitations if existing else [],
        createdAt=datetime.now(UTC).isoformat(),
        acceptedAt=None,
        notes=existing.notes if existing else "",
    )


def accept_candidate_baseline(candidate: GoldenModel) -> GoldenModel:
    """Explicitly promotes a candidate to the accepted baseline on disk.
    Never called by `verify_golden`/`verify_all_goldens`, never called by
    CI, and never called automatically on a failing test
    (QUALITY-GOV-003)."""

    from jewelmind.geometry_quality.registry import save_golden

    accepted = candidate.model_copy(
        update={"baselineStatus": "STABLE", "acceptedAt": datetime.now(UTC).isoformat()}
    )
    save_golden(accepted)
    return accepted
