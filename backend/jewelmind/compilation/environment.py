"""Reading the real compilation environment.

THE ONE PLACE that asks the running system which versions it is. Every value
comes from an actual version constant or installed library — none is invented,
and none is defaulted to a plausible string when it cannot be read (an
unreadable component becomes `None`, which
`identity.py::CompilationFingerprint.components()` records as an explicit
`absent` rather than dropping).

SEPARATE FROM `identity.py` on purpose. Computing a hash from strings must stay
pure and kernel-free; reading a kernel version cannot be. Splitting them means
the pure half is importable anywhere, and only this half touches CadQuery.

DELIBERATELY NOT CACHED. Reading a handful of module constants and one JSON
file costs nothing next to a CAD rebuild, and a memoized fingerprint would go
stale exactly when it mattered most — in a long-running process across a
hot-reloaded rule registry.
"""

from __future__ import annotations

import json
from pathlib import Path

import cadquery as cq

from jewelmind import __version__ as compiler_version
from jewelmind.compilation.identity import CompilationFingerprint
from jewelmind.geometry.constants import GENERATOR_VERSION

#: The live Forge rule registry, the same file `geometry_quality/fingerprint.py`
#: reads. Resolved from this module's own location rather than a working
#: directory, so it is correct however the process was started.
_FORGE_REGISTRY_PATH = (
    Path(__file__).resolve().parents[3]
    / "specs"
    / "forge"
    / "v1"
    / "current-rule-registry.json"
)


def forge_rule_set_version() -> str:
    """The aggregate Forge rule-set version.

    THIS NOW EXISTS, which it did not when
    `174-determinism-and-version-fingerprint.md` was written: that document's
    table records "No aggregate exists (each rule is independently `1.0.0`)",
    and `specs/forge/v1/current-rule-registry.json` has since gained a real
    `registryVersion`. The fingerprint reads the real value.

    Returns `"unknown"` when the file cannot be read — an honest report of an
    unreadable registry, and stable enough to hash.
    """

    try:
        data = json.loads(_FORGE_REGISTRY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "unknown"
    return str(data.get("registryVersion", "unknown"))


def ocp_version() -> str | None:
    """The installed OpenCascade (OCP) build, or `None` if it cannot be read.

    `None` rather than a guess: OCP does not always expose `__version__`, and
    reporting the CadQuery version in its place would claim to identify a build
    this code never inspected.
    """

    try:
        import OCP
    except Exception:  # noqa: BLE001 - an unimportable kernel binding is a fact
        return None
    version = getattr(OCP, "__version__", None)
    return str(version) if version is not None else None


def current_fingerprint() -> CompilationFingerprint:
    """The fingerprint of the environment this process is running in.

    Knowable BEFORE any geometry is built, which is what makes it usable as a
    cache key: every component is a module constant or an installed library
    version, not a property of a generated model.
    """

    return CompilationFingerprint(
        compilerVersion=compiler_version,
        geometryGeneratorVersion=GENERATOR_VERSION,
        forgeRuleSetVersion=forge_rule_set_version(),
        kernelVersion=cq.__version__,
        ocpVersion=ocp_version(),
    )
