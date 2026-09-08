"""Compilation identity (pre-Sprint-27 persistence readiness).

IMPORTS NOTHING, DELIBERATELY. `identity.py` is pure and kernel-free so any
layer may compute a compilation hash from plain strings; `environment.py` reads
the real installed versions and does touch the kernel. Keeping the package init
empty means importing the pure half never pulls in CadQuery — which is what
lets Forge, tests and any future persistence layer use it freely.

Import the submodule you need directly:

    from jewelmind.compilation.identity import compilation_hash
    from jewelmind.compilation.environment import current_fingerprint
"""
