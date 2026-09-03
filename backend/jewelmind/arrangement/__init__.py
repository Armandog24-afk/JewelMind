"""Stone Arrangement Engine v1 — category-neutral multi-stone representation.

DELIBERATELY IMPORTS NOTHING, and that is load-bearing rather than stylistic.

`jewelmind.domain.schema` imports `jewelmind.arrangement.models` for its
vocabularies, while `jewelmind.arrangement.jdl_adapter` imports
`jewelmind.domain.schema`. The graph is acyclic only because this package init
pulls in no submodule — exactly the trap `jewelmind/stone/__init__.py` and
`jewelmind/gem/__init__.py` already document.

Import a submodule explicitly:

    from jewelmind.arrangement.models import ArrangementDefinition
    from jewelmind.arrangement.resolve import resolve_arrangement

See docs/bible/24-arrangement/README.md.
"""
