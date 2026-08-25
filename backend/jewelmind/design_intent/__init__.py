"""Design Intent Model v1 — a formal semantic layer for aesthetic intent.

Design Intent is not geometry, not JDL, and not a manufacturing rule. It
represents what a user meant aesthetically ("delicate", "minimal",
"classic") as a structured, reviewable, preservable model — separate from
the deterministic `JewelryDefinition` that Forge/Alchemist/Atlas consume.
See docs/bible/13-design-intent/README.md and 330-intent-governance.md.
"""

from __future__ import annotations
