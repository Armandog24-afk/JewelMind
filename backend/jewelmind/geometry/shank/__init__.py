"""The Shank subsystem — Atlas-layer geometry infrastructure for building a
ring band/shank, deterministic and ring-agnostic at the primitive level
(profile, taper interpolation), with one Ring-aware entry point
(`build_shank`). See docs/bible/19-shank/README.md.
"""

from jewelmind.geometry.shank.builder import build_shank

__all__ = ["build_shank"]
