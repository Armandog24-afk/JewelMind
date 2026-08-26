"""Compares two GeometrySnapshots and produces a structured, human-readable
GeometryDiff (QUALITY-GOV-005) — exact invariants and floating-point
comparisons are always kept in distinct result lists, never merged into a
single pass/fail bit.
"""

from __future__ import annotations

from jewelmind.geometry_quality.models import (
    ArtifactChange,
    ExactChange,
    GeometryDiff,
    NumericFactDiff,
    RelationshipChange,
    TopologyChange,
    VersionFingerprint,
)
from jewelmind.geometry_quality.version import (
    ABSOLUTE_COMPARISON_TOLERANCE_MM,
    RELATIVE_COMPARISON_TOLERANCE,
)


def _numeric_diff(path: str, expected: float, actual: float) -> NumericFactDiff | None:
    if expected == actual:
        return None
    absolute_delta = abs(actual - expected)
    relative_delta = absolute_delta / abs(expected) if expected else None
    within = absolute_delta <= ABSOLUTE_COMPARISON_TOLERANCE_MM or (
        relative_delta is not None and relative_delta <= RELATIVE_COMPARISON_TOLERANCE
    )
    return NumericFactDiff(
        path=path,
        expected=expected,
        actual=actual,
        absoluteDelta=absolute_delta,
        relativeDelta=relative_delta,
        tolerance=RELATIVE_COMPARISON_TOLERANCE,
        withinTolerance=within,
    )


def _bbox_numeric_diffs(path_prefix: str, expected: dict, actual: dict) -> list[NumericFactDiff]:
    out = []
    for key in sorted(set(expected) | set(actual)):
        e, a = expected.get(key), actual.get(key)
        if e is None or a is None:
            continue
        diff = _numeric_diff(f"{path_prefix}.{key}", e, a)
        if diff:
            out.append(diff)
    return out


def _kernel_related_fields_differ(expected_fp: VersionFingerprint, actual_fp: VersionFingerprint) -> bool:
    return (
        expected_fp.kernelVersion != actual_fp.kernelVersion
        or expected_fp.ocpVersion != actual_fp.ocpVersion
        or expected_fp.atlasGeneratorVersion != actual_fp.atlasGeneratorVersion
    )


def compare_snapshot(
    golden_id: str,
    expected,
    actual,
    expected_fingerprint: VersionFingerprint,
    actual_fingerprint: VersionFingerprint,
) -> GeometryDiff:
    exact_changes: list[ExactChange] = []
    numeric_changes: list[NumericFactDiff] = []
    relationship_changes: list[RelationshipChange] = []
    topology_changes: list[TopologyChange] = []
    artifact_changes: list[ArtifactChange] = []

    # -- assembly-level exact invariants --------------------------------
    assembly_exact_fields = (
        "componentCount",
        "productionComponentCount",
        "referenceComponentCount",
        "productionConnectivityGroups",
        "productionIsFullyConnected",
    )
    for field in assembly_exact_fields:
        e, a = getattr(expected.assembly, field), getattr(actual.assembly, field)
        if e != a:
            exact_changes.append(ExactChange(path=f"assembly.{field}", expected=e, actual=a))
    numeric_changes += _bbox_numeric_diffs(
        "assembly.boundingBox", expected.assembly.boundingBox, actual.assembly.boundingBox
    )

    # -- design-consistency exact invariants (QUALITY-GOV-013/014) ------
    for field in (
        "requestedProngCount",
        "generatedProngCount",
        "prongCountMatches",
        "stoneReferenceIsProductionMetal",
    ):
        e, a = getattr(expected.designConsistency, field), getattr(actual.designConsistency, field)
        if e != a:
            exact_changes.append(ExactChange(path=f"designConsistency.{field}", expected=e, actual=a))

    # -- per-component ----------------------------------------------------
    expected_by_id = {c.componentId: c for c in expected.components}
    actual_by_id = {c.componentId: c for c in actual.components}
    missing = sorted(set(expected_by_id) - set(actual_by_id))
    added = sorted(set(actual_by_id) - set(expected_by_id))
    if missing:
        exact_changes.append(ExactChange(path="components.missing", expected=missing, actual=[]))
    if added:
        exact_changes.append(ExactChange(path="components.unexpected", expected=[], actual=added))

    for component_id in sorted(set(expected_by_id) & set(actual_by_id)):
        e, a = expected_by_id[component_id], actual_by_id[component_id]
        for field in ("role", "present", "fallbackUsed"):
            ev, av = getattr(e, field), getattr(a, field)
            if ev != av:
                exact_changes.append(
                    ExactChange(path=f"components.{component_id}.{field}", expected=ev, actual=av)
                )
        if e.solidCount != a.solidCount:
            topology_changes.append(
                TopologyChange(
                    componentId=component_id,
                    field="solidCount",
                    expected=e.solidCount or 0,
                    actual=a.solidCount or 0,
                )
            )
        if e.topology and a.topology:
            for key in sorted(set(e.topology) | set(a.topology)):
                ev, av = e.topology.get(key), a.topology.get(key)
                if ev is not None and av is not None and ev != av:
                    topology_changes.append(
                        TopologyChange(componentId=component_id, field=key, expected=ev, actual=av)
                    )
        if e.volumeMm3 is not None and a.volumeMm3 is not None:
            diff = _numeric_diff(f"components.{component_id}.volumeMm3", e.volumeMm3, a.volumeMm3)
            if diff:
                numeric_changes.append(diff)
        if e.boundingBox and a.boundingBox:
            numeric_changes += _bbox_numeric_diffs(
                f"components.{component_id}.boundingBox", e.boundingBox, a.boundingBox
            )

    # -- relationships ------------------------------------------------------
    expected_rel = {(r.componentA, r.componentB): r for r in expected.relationships}
    actual_rel = {(r.componentA, r.componentB): r for r in actual.relationships}
    for pair in sorted(set(expected_rel) & set(actual_rel)):
        e, a = expected_rel[pair], actual_rel[pair]
        if e.connected != a.connected:
            relationship_changes.append(
                RelationshipChange(
                    componentA=pair[0],
                    componentB=pair[1],
                    field="connected",
                    expected=e.connected,
                    actual=a.connected,
                )
            )
        if e.intersectionStatus != a.intersectionStatus:
            relationship_changes.append(
                RelationshipChange(
                    componentA=pair[0],
                    componentB=pair[1],
                    field="intersectionStatus",
                    expected=e.intersectionStatus,
                    actual=a.intersectionStatus,
                )
            )
        if e.minDistanceMm is not None and a.minDistanceMm is not None:
            path = f"relationships.{pair[0]}-{pair[1]}.minDistanceMm"
            diff = _numeric_diff(path, e.minDistanceMm, a.minDistanceMm)
            if diff:
                numeric_changes.append(diff)

    # -- severity -------------------------------------------------------
    regression_numeric = [n for n in numeric_changes if not n.withinTolerance]
    kernel_differs = _kernel_related_fields_differ(expected_fingerprint, actual_fingerprint)

    if exact_changes or relationship_changes or regression_numeric:
        severity = "REGRESSION"
        requires_review = True
    elif topology_changes:
        severity = "VERSION_REVIEW_REQUIRED" if kernel_differs else "REGRESSION"
        requires_review = True
    elif numeric_changes:
        severity = "INFO"
        requires_review = False
    else:
        severity = "NONE"
        requires_review = False

    return GeometryDiff(
        goldenId=golden_id,
        expectedFingerprint=expected_fingerprint,
        actualFingerprint=actual_fingerprint,
        exactChanges=exact_changes,
        numericChanges=numeric_changes,
        relationshipChanges=relationship_changes,
        topologyChanges=topology_changes,
        artifactChanges=artifact_changes,
        severity=severity,
        requiresBaselineReview=requires_review,
    )
