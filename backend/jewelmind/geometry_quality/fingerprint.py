"""Collects the real version fingerprint for a generated model
(QUALITY-GOV-009) — every field is read from an actual running version
constant/library, never invented.

Sprint 6/7 identified missing version fingerprint information; this
closes the gap for the fields that matter to geometry regression, without
a broader compiler-orchestration refactor (see
docs/bible/17-geometry-quality/510-version-fingerprint-policy.md).
"""

from __future__ import annotations

import json
from pathlib import Path

import cadquery as cq

from jewelmind import __version__ as compiler_version
from jewelmind.domain.schema import SCHEMA_VERSION
from jewelmind.geometry.inspection.version import INSPECTION_VERSION
from jewelmind.geometry.model import GeneratedModel
from jewelmind.geometry_quality.models import VersionFingerprint

_FORGE_REGISTRY_PATH = (
    Path(__file__).resolve().parents[3] / "specs" / "forge" / "v1" / "current-rule-registry.json"
)


def _forge_registry_version() -> str:
    try:
        data = json.loads(_FORGE_REGISTRY_PATH.read_text(encoding="utf-8"))
        return str(data.get("registryVersion", "unknown"))
    except OSError:
        return "unknown"


def _ocp_version() -> str | None:
    try:
        import OCP

        return getattr(OCP, "__version__", None)
    except Exception:
        return None


def collect_fingerprint(model: GeneratedModel) -> VersionFingerprint:
    return VersionFingerprint(
        jdlSchemaVersion=SCHEMA_VERSION,
        forgeRuleSetVersion=_forge_registry_version(),
        compilerVersion=compiler_version,
        atlasGeneratorVersion=model.generator_version,
        inspectionVersion=INSPECTION_VERSION,
        kernelVersion=cq.__version__,
        ocpVersion=_ocp_version(),
    )
