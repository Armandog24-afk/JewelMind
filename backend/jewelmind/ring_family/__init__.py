"""Ring Families v2 (Sprint 28) — parametric ring families.

A ring family is a PARAMETRIC RELATION between a ring's size, its structure,
its stones and its setting. It is not a preset: a family DERIVES the blocks it
owns from a small set of family parameters, so changing one parameter
regenerates the design rather than requiring the author to rebuild it.

Deliberately NON-EAGER (imports nothing) — the same discipline
`jewelmind/{stone,gem,arrangement,family,halo,pave}/__init__.py` each document.
It is load-bearing: `domain/schema.py` imports `ring_family.models`, so an
eager package init would make the import graph cyclic.

See docs/bible/30-ring-families/README.md.
"""

