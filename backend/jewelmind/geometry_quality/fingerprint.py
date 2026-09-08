"""Collects the real version fingerprint for a generated model
(QUALITY-GOV-009) — every field is read from an actual running version
constant/library, never invented.

Sprint 6/7 identified missing version fingerprint information; this
closes the gap for the fields that matter to geometry regression, without
a broader compiler-orchestration refactor (see
docs/bible/17-geometry-quality/510-version-fingerprint-policy.md).

DERIVED, NOT DUPLICATED. The version-reading logic moved to
`jewelmind/compilation/environment.py` when `compilationHash` was implemented,
because the cache key and this report must never disagree about which kernel
built a model. This module now reports the same environment plus the two fields
the Golden suite needs and the compilation identity deliberately excludes:
`jdlSchemaVersion` (already inside `definitionHash`) and `inspectionVersion`
(read-only measurement, which cannot affect geometry) — see
`jewelmind/compilation/identity.py::CompilationFingerprint` for why.
"""

from __future__ import annotations

from jewelmind.compilation.environment import current_fingerprint
from jewelmind.domain.schema import SCHEMA_VERSION
from jewelmind.geometry.inspection.version import INSPECTION_VERSION
from jewelmind.geometry.model import GeneratedModel
from jewelmind.geometry_quality.models import VersionFingerprint


def collect_fingerprint(model: GeneratedModel) -> VersionFingerprint:
    environment = current_fingerprint()
    return VersionFingerprint(
        jdlSchemaVersion=SCHEMA_VERSION,
        forgeRuleSetVersion=environment.forgeRuleSetVersion,
        compilerVersion=environment.compilerVersion,
        # The MODEL'S OWN stamped generator, not the environment's: a snapshot
        # must report what actually built the geometry it describes, which for
        # a reused or reloaded model need not be this process's constant.
        atlasGeneratorVersion=model.generator_version,
        inspectionVersion=INSPECTION_VERSION,
        kernelVersion=environment.kernelVersion,
        ocpVersion=environment.ocpVersion,
    )
