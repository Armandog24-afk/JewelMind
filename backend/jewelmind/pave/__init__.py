"""Pavé & Microsetting Engine v1 (Sprint 26).

IMPORTS NOTHING, DELIBERATELY, and that is load-bearing rather than tidy:
`domain/schema.py` imports `jewelmind.pave.models`, so an eager package init
would make the import graph cyclic — the same trap `jewelmind/stone/`,
`jewelmind/gem/`, `jewelmind/arrangement/`, `jewelmind/family/` and
`jewelmind/halo/` each document.

Import the submodule you need directly:

    from jewelmind.pave.models import PaveDefinition
    from jewelmind.pave.compile import compose_pave
"""
