"""Halo System v1 (Sprint 25).

IMPORTS NOTHING, DELIBERATELY, and that is load-bearing rather than tidy:
`domain/schema.py` imports `jewelmind.halo.models`, while
`jewelmind.halo.effective`-side composition needs `JewelryDefinition`. The
import graph is acyclic only because this package's init pulls in no submodule
— the same trap `jewelmind/stone/`, `jewelmind/gem/`, `jewelmind/arrangement/`
and `jewelmind/family/` each document.

Import the submodule you need directly:

    from jewelmind.halo.models import HaloDefinition
    from jewelmind.halo.compile import compose_halo
"""
