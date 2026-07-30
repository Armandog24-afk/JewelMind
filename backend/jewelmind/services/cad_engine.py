"""One-time CadQuery/OpenCascade readiness probe.

`backend/jewelmind/geometry/**` imports `cadquery` unconditionally at
module scope, so anything that transitively imports the geometry package
(generation, export, preview) will raise ImportError at import time if
CadQuery is broken or missing. That import chain must stay *lazy* (see
`jewelmind/api/routes.py`'s `_get_model_service()`) so the rest of the
backend — health checks, validation — keeps working even when the CAD
engine cannot load. This module performs an isolated, standalone check
so `/api/health` can report the true status without depending on that
lazy-loaded chain at all.

The check goes beyond a bare `import cadquery`: it also builds a trivial
solid, which catches the case where the Python package imports fine but
the native OpenCascade bindings fail to actually initialize (e.g. a
missing shared library in a stripped-down container).
"""

from __future__ import annotations


def probe_cad_engine() -> tuple[bool, str | None]:
    """Return (ready, error_message). Never raises."""

    try:
        import cadquery as cq

        cq.Workplane("XY").box(1, 1, 1).val().Volume()
    except Exception as exc:  # noqa: BLE001 - any failure at all means "not ready"
        return False, f"{type(exc).__name__}: {exc}"
    return True, None


# Computed once at import time: the CAD engine's availability cannot change
# during a running process (it's a native binding resolved once at import),
# so re-probing on every /api/health call would be pure wasted work.
_READY, _ERROR = probe_cad_engine()


def cad_engine_ready() -> bool:
    return _READY


def cad_engine_error() -> str | None:
    return _ERROR
