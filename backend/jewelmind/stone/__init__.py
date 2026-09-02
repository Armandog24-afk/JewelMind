"""JewelMind Stone System v2 — shared, category-neutral stone infrastructure.

This package deliberately imports NOTHING at package-init time.

Sprint 18 and Sprint 20 both hit real circular imports caused by an eager
package `__init__.py`: a low-level module (`geometry/constants.py`) needs a
value from this package, while this package's own submodules need values from
that module. An eager re-export here closes that loop and fails with a
partially-initialized-module `ImportError`. Callers therefore import the
submodule directly:

    from jewelmind.stone.models import StoneSourceMode      # yes
    from jewelmind.stone import StoneSourceMode             # no

Do not add convenience re-exports here. See
docs/bible/22-stone-v2/stone-source-architecture.md.

ARCHITECTURAL BOUNDARY (STONEV2-GOV-001): nothing in this package may import
`jewelmind.ring` or any other jewelry category, and nothing may import
`JewelryDefinition` (which would smuggle an entire category domain across in
one import). Stone is consumed BY categories and settings; it never depends on
them. Enforced by AST inspection in
`backend/tests/test_stone_v2_no_category_dependency.py`.
"""
