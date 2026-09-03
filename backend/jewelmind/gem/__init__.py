"""JewelMind Gem Identity & Material System — shared, category-neutral.

This package deliberately imports NOTHING at package-init time.

Sprints 18 and 20 both hit real circular imports caused by an eager package
`__init__.py`, and the same graph exists here: `domain/schema.py` imports
`jewelmind.gem.models` for the canonical gem vocabulary, while
`jewelmind.gem.normalize` imports `domain/schema.py`. That is only acyclic
because importing this package pulls in no submodule. Callers import the
submodule directly:

    from jewelmind.gem.models import GemOrigin      # yes
    from jewelmind.gem import GemOrigin             # no

ARCHITECTURAL BOUNDARY (GEM-GOV-001): nothing in this package may import a
jewelry category (`jewelmind.ring`, `jewelmind.jewelry_category`, ...), and
nothing may import `JewelryDefinition`. A gem's identity has nothing to do with
whether it sits in a ring, an earring or a pendant. Enforced by AST inspection
in `backend/tests/test_gem_no_category_dependency.py`.

WHAT THIS PACKAGE IS NOT: a gemological database. The registry is an
extensible foundation for identifying and rendering gems, not a certification
source. Nothing here is professionally validated.
"""
