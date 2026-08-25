"""Designer v1 — controlled natural-language design interpretation.

Designer turns a natural-language design request into a structured,
reviewable `DesignerProposal`. It never writes geometry, never bypasses
JDL/Forge validation, and never carries jewelry-domain authority — see
docs/bible/12-designer/README.md and 290-designer-governance.md.
"""

from __future__ import annotations
