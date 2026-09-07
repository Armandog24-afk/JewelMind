"""Multi-Stone Families v1 — semantic structure for common multi-stone designs.

DELIBERATELY IMPORTS NOTHING, and that is load-bearing rather than stylistic.

`jewelmind.domain.schema` imports `jewelmind.family.models` for the `family`
field's type, while `jewelmind.family.compile` reaches the arrangement resolver.
The graph is acyclic only because this package init pulls in no submodule — the
same trap `jewelmind/stone/__init__.py`, `jewelmind/gem/__init__.py` and
`jewelmind/arrangement/__init__.py` already document.

Import a submodule explicitly:

    from jewelmind.family.models import FamilyDefinition
    from jewelmind.family.compile import compile_family

See docs/bible/26-multi-stone-families/README.md.
"""
