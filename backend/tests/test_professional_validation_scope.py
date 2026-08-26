"""REVIEWER_SCOPE_TEST — the Sprint 13 brief's example: a record valid for
round solitaire + lost-wax casting must not automatically validate oval
halo + resin printing.
"""

from __future__ import annotations

from jewelmind.professional_validation.schemas import ValidationScope
from jewelmind.professional_validation.scope import scope_matches


def test_empty_scope_matches_any_context():
    assert scope_matches(ValidationScope(), {"stoneShape": "round", "manufacturingMethod": "anything"})


def test_matching_context_is_covered():
    scope = ValidationScope(stoneShape="round", manufacturingMethod="lost_wax_casting")
    assert scope_matches(scope, {"stoneShape": "round", "manufacturingMethod": "lost_wax_casting"})


def test_round_lost_wax_scope_does_not_cover_oval_resin_context():
    scope = ValidationScope(stoneShape="round", manufacturingMethod="lost_wax_casting")
    context = {"stoneShape": "oval", "manufacturingMethod": "direct_resin_printing"}
    assert not scope_matches(scope, context)


def test_a_scope_field_left_unset_never_narrows_the_match():
    scope = ValidationScope(manufacturingMethod="lost_wax_casting")
    # stoneShape is unset in the scope — the record makes no claim about
    # it either way, so any stoneShape is compatible with this scope.
    assert scope_matches(scope, {"manufacturingMethod": "lost_wax_casting", "stoneShape": "oval"})


def test_context_missing_a_constrained_field_does_not_match():
    scope = ValidationScope(manufacturingMethod="lost_wax_casting")
    assert not scope_matches(scope, {"stoneShape": "round"})
