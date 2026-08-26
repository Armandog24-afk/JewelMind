"""Runtime geometry inspection — Sprint 14 (Geometry Inspection v2).

Reports geometric facts about an already-generated `GeneratedModel`;
never interprets those facts as jewelry-domain or manufacturing
judgments (that remains Forge's job) and never mutates or repairs the
geometry it inspects. See docs/bible/16-geometry-inspection/README.md.

`inspect_model()` (`inspector.py`) is the one public entry point most
callers need; the other modules (`components`, `assembly`, `connectivity`,
`intersection`, `distance`, `topology`, `shape`) are individually usable
building blocks, not one giant inspector function.
"""

from jewelmind.geometry.inspection.inspector import inspect_model

__all__ = ["inspect_model"]
