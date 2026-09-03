"""Canonical form and deterministic fingerprinting (Sprint 22).

WHY NORMALIZATION EXISTS. Two documents that mean the same arrangement must
produce the same bytes and the same fingerprint. Without canonicalization,
reordering an `instances` list — something a UI does incidentally — would change
the fingerprint and make an identical arrangement look like a different one.

WHAT NORMALIZATION MAY AND MAY NOT DO. It may reorder, round and wrap: sort by
ID, fold an angle into [0, 360), quantize a coordinate. It may NEVER change what
the arrangement means — no repairing a malformed transform, no filling a missing
reference, no dropping a duplicate. Those are validation failures, and a
normalizer that quietly fixed them would hide a real defect (the discipline
Sprint 20 established for custom outlines: validate and reject, never repair).

THE ROUNDING IS DELIBERATE. Coordinates are quantized to `COORDINATE_DECIMALS`
before hashing so a value that differs only in floating-point noise fingerprints
identically. This is a SOFTWARE comparison tolerance for identity purposes, in
the same spirit as `geometry_quality/version.py`'s comparison tolerances — never
a manufacturing tolerance and never a claim about achievable precision.
"""

from __future__ import annotations

import hashlib
import json

from jewelmind.arrangement.capability import RESOLVER_VERSION
from jewelmind.arrangement.models import (
    ArrangementDefinition,
    ArrangementRelation,
    InstanceTransform,
    ResolvedArrangement,
)

#: Decimal places retained when hashing a coordinate or angle. 1e-6 mm is far
#: below anything meaningful in jewelry and far above float noise, so it
#: separates "the same placement" from "a different placement" without ever
#: being mistaken for a tolerance a workshop could hold.
COORDINATE_DECIMALS = 6

#: Relation kinds whose member order carries no meaning, and may therefore be
#: sorted. `MIRRORED_PAIR` is absent: its first member is the original and its
#: second the reflection, so sorting would lose which is which.
_ORDER_INSENSITIVE_RELATIONS = frozenset(
    {"ALIGNED_WITH", "EVENLY_SPACED_WITH", "CONCENTRIC_WITH", "SHARES_TRANSFORM_WITH"}
)


def normalize_angle_deg(angle: float) -> float:
    """Fold an angle into [0, 360) and quantize it.

    370° and 10° are the same rotation, and an arrangement that fingerprinted
    them differently would report two identical designs as distinct.
    """

    folded = angle % 360.0
    # `-0.0 % 360.0` is 0.0 in Python, but an explicit round keeps the sign of
    # zero out of the serialized form entirely.
    return round(folded + 0.0, COORDINATE_DECIMALS)


def normalize_transform(transform: InstanceTransform) -> InstanceTransform:
    return InstanceTransform(
        xMm=round(transform.xMm + 0.0, COORDINATE_DECIMALS),
        yMm=round(transform.yMm + 0.0, COORDINATE_DECIMALS),
        zMm=round(transform.zMm + 0.0, COORDINATE_DECIMALS),
        rotationDeg=normalize_angle_deg(transform.rotationDeg),
    )


def normalize_relation(relation: ArrangementRelation) -> ArrangementRelation:
    if relation.kind in _ORDER_INSENSITIVE_RELATIONS:
        members = sorted(relation.members)
    else:
        members = list(relation.members)
    return relation.model_copy(update={"members": members})


def normalize_definition(definition: ArrangementDefinition) -> ArrangementDefinition:
    """Canonical ordering and quantization for an arrangement definition.

    Sorting is by the authoritative ID in every case — never by array position,
    never by insertion order.
    """

    instances = [
        instance.model_copy(
            update={
                "placement": instance.placement.model_copy(
                    update={
                        "transform": normalize_transform(instance.placement.transform)
                    }
                ),
                "overrides": instance.overrides.model_copy(
                    update={
                        "orientationDeg": (
                            normalize_angle_deg(instance.overrides.orientationDeg)
                            if instance.overrides.orientationDeg is not None
                            else None
                        )
                    }
                ),
            }
        )
        for instance in sorted(definition.instances, key=lambda i: i.instanceId)
    ]
    groups = [
        group.model_copy(update={"transform": normalize_transform(group.transform)})
        for group in sorted(definition.groups, key=lambda g: g.groupId)
    ]
    patterns = sorted(definition.patterns, key=lambda p: p.patternId)
    relations = [
        normalize_relation(relation)
        for relation in sorted(definition.relations, key=lambda r: r.relationId)
    ]
    return ArrangementDefinition(
        instances=instances,
        groups=groups,
        patterns=patterns,
        relations=relations,
    )


def canonical_json(definition: ArrangementDefinition) -> str:
    """Canonical serialization of a normalized arrangement.

    `sort_keys=True` plus the tightest separators, matching
    `utils/hashing.py::canonical_json`'s conventions exactly so the two
    representations cannot diverge in style. `allow_nan=False`: a non-finite
    value must fail here rather than serialize to a token no JSON reader
    accepts — the schema already rejects it, and this is defence in depth.
    """

    normalized = normalize_definition(definition)
    return json.dumps(
        normalized.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def arrangement_fingerprint(definition: ArrangementDefinition) -> str:
    """Deterministic fingerprint of an arrangement's own content.

    SEPARATE FROM `definitionHash` AND `geometryHash`, which is a requirement
    rather than a convenience: the same arrangement reused in two different
    rings has one fingerprint and two definition hashes, and that is what makes
    an arrangement addressable as a thing in its own right.

    The resolver version participates, because a change to the resolution
    arithmetic changes what the same declarative content MEANS. A stored
    fingerprint therefore stops matching when the arithmetic changes, instead of
    silently claiming an old resolution is still current.

    16 hex characters from SHA-256, exactly like `definition_hash()`.
    """

    payload = f"{RESOLVER_VERSION}|{canonical_json(definition)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def resolved_canonical_json(resolved: ResolvedArrangement) -> str:
    """Canonical serialization of a RESOLVED arrangement.

    Used by tests and specs to prove that resolving the same definition twice
    produces identical bytes, not merely equal-looking objects.
    """

    return json.dumps(
        resolved.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
