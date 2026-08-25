"""Unit tests for the Conversation Engine's deterministic building blocks."""

from __future__ import annotations

from jewelmind.conversation import clarifications, context, references, state
from jewelmind.conversation.actions import classify_action
from jewelmind.conversation.schemas import ConversationSession
from jewelmind.design_intent.schemas import DesignIntent
from jewelmind.domain.schema import JewelryDefinition


def _session(**overrides) -> ConversationSession:
    base = state.new_session(JewelryDefinition(), DesignIntent(sourceText=""), "2026-01-01T00:00:00Z")
    return base.model_copy(update=overrides)


class TestHashing:
    def test_definition_hash_is_deterministic(self):
        a = state.new_session(JewelryDefinition(), DesignIntent(sourceText=""), "t")
        b = state.new_session(JewelryDefinition(), DesignIntent(sourceText=""), "t")
        assert a.currentJDLHash == b.currentJDLHash
        assert a.currentIntentHash == b.currentIntentHash

    def test_hash_changes_when_definition_changes(self):
        default = JewelryDefinition()
        new_material = default.material.model_copy(update={"metal": "platinum"})
        changed = default.model_copy(update={"material": new_material})
        assert state.definition_hash(default) != state.definition_hash(changed)

    def test_intent_hash_changes_when_intent_changes(self):
        empty = DesignIntent(sourceText="")
        from jewelmind.design_intent.schemas import IntentStatement

        with_statement = empty.model_copy(
            update={
                "statements": [
                    IntentStatement(
                        intentId="i1", target="RING", concept="VISUAL_WEIGHT", value="DELICATE",
                        provenance="AI_NORMALIZED", confidenceClass="EXACT", sourceText="delicate",
                        resolutionStatus="PRESERVED",
                    )
                ]
            }
        )
        assert state.intent_hash(empty) != state.intent_hash(with_statement)

    def test_is_proposal_stale_true_when_jdl_differs(self):
        from jewelmind.designer.schemas import DesignerProposal

        current = JewelryDefinition()
        proposal = state.make_proposal(
            "turn-1", current, DesignIntent(sourceText=""),
            DesignerProposal(
                proposalId="p1", sourceText="x", interactionMode="MODIFY", candidateJDL=current,
                proposalStatus="COMPLETE", designIntent=DesignIntent(sourceText=""),
            ),
        )
        edited = current.model_copy(update={"band": current.band.model_copy(update={"width": 9.9})})
        assert state.is_proposal_stale(proposal, edited, DesignIntent(sourceText="")) is True
        assert state.is_proposal_stale(proposal, current, DesignIntent(sourceText="")) is False


class TestReferences:
    def test_explicit_target_english(self):
        assert references.find_explicit_target("make the band wider") == "BAND"

    def test_explicit_target_italian(self):
        assert references.find_explicit_target("allarga la fascia") == "BAND"

    def test_preserve_phrase_with_target(self):
        assert references.find_preserve_target("leave the stone as is") == "STONE"
        assert references.find_preserve_target("lascia la pietra così") == "STONE"

    def test_preserve_phrase_without_target_returns_none(self):
        assert references.find_preserve_target("leave it") is None

    def test_material_word_is_safe_implicit_target(self):
        target, ambiguous = references.resolve_implicit_target("make it rose gold", None)
        assert target == "MATERIAL_APPEARANCE"
        assert ambiguous is False

    def test_bare_pronoun_with_no_context_is_ambiguous(self):
        target, ambiguous = references.resolve_implicit_target("make it wider", None)
        assert target is None
        assert ambiguous is True

    def test_bare_pronoun_resolves_to_last_referenced_target(self):
        target, ambiguous = references.resolve_implicit_target("make it wider", "BAND")
        assert target == "BAND"
        assert ambiguous is False

    def test_explicit_target_present_is_never_ambiguous(self):
        target, ambiguous = references.resolve_implicit_target("make the band wider", None)
        assert target == "BAND"
        assert ambiguous is False


class TestClarifications:
    def test_numeric_answer_parses(self):
        thread = clarifications.open_clarification("t1", "Width?", "band.width", "NUMERIC", "now")
        value, accepted = clarifications.try_resolve_answer(thread, "2.7 mm")
        assert accepted is True
        assert value == 2.7

    def test_numeric_answer_rejects_non_numeric(self):
        thread = clarifications.open_clarification("t1", "Width?", "band.width", "NUMERIC", "now")
        value, accepted = clarifications.try_resolve_answer(thread, "wider")
        assert accepted is False
        assert value is None

    def test_enum_choice_matches_case_insensitively(self):
        thread = clarifications.open_clarification(
            "t1", "Metal?", "material.metal", "ENUM_CHOICE", "now",
            allowed_choices=["yellow_gold_18k", "rose_gold_18k"],
        )
        value, accepted = clarifications.try_resolve_answer(thread, "ROSE_GOLD_18K")
        assert accepted is True
        assert value == "rose_gold_18k"

    def test_enum_choice_rejects_unknown_option(self):
        thread = clarifications.open_clarification(
            "t1", "Metal?", "material.metal", "ENUM_CHOICE", "now", allowed_choices=["yellow_gold_18k"]
        )
        _, accepted = clarifications.try_resolve_answer(thread, "titanium")
        assert accepted is False

    def test_confirmation_yes_no(self):
        thread = clarifications.open_clarification("t1", "Proceed?", None, "CONFIRMATION", "now")
        assert clarifications.try_resolve_answer(thread, "yes") == ("yes", True)
        assert clarifications.try_resolve_answer(thread, "no") == ("no", True)
        assert clarifications.try_resolve_answer(thread, "maybe")[1] is False

    def test_close_answered_sets_status(self):
        thread = clarifications.open_clarification("t1", "Width?", "band.width", "NUMERIC", "now")
        closed = clarifications.close_answered(thread, "2.7", 2.7, "later")
        assert closed.status == "ANSWERED"
        assert closed.answer == "2.7"
        assert thread.status == "OPEN"  # original never mutated


class TestActionClassification:
    def test_pending_clarification_always_wins(self):
        thread = clarifications.open_clarification("t1", "Q?", None, "FREE_TEXT", "now")
        session = _session(pendingClarification=thread)
        assert classify_action("anything at all", session) == "ANSWER_CLARIFICATION"

    def test_noop_phrase_with_nothing_pending(self):
        session = _session()
        assert classify_action("ok", session) == "NO_CHANGE"
        assert classify_action("Perfetto.", session) == "NO_CHANGE"

    def test_undo_marker(self):
        session = _session()
        assert classify_action("undo that", session) == "CANCEL_INTERACTION"

    def test_start_over_marker(self):
        session = _session()
        assert classify_action("let's start over", session) == "CREATE_DESIGN_PROPOSAL"

    def test_preserve_phrase_short_message(self):
        session = _session()
        assert classify_action("leave the stone as is", session) == "PRESERVE_TARGET"

    def test_default_routes_to_modify(self):
        session = _session()
        assert classify_action("Fammi un solitario in oro rosa.", session) == "MODIFY_DESIGN_PROPOSAL"


class TestContext:
    def test_build_turn_context_reflects_pending_clarification(self):
        thread = clarifications.open_clarification("t1", "Width?", "band.width", "NUMERIC", "now")
        session = _session(pendingClarification=thread)
        ctx = context.build_turn_context(session, "CURRENT")
        assert ctx.pendingClarificationQuestion == "Width?"

    def test_compact_summary_preserves_accepted_decisions_from_older_turns(self):
        from jewelmind.conversation.schemas import ConversationTurn

        turns = [
            ConversationTurn(
                turnId=f"t{i}", sequence=i, sourceText="x", timestamp="now",
                interpretedAction="ACCEPT_PROPOSAL", accepted=True,
                technicalChanges=["material.metal"],
                relatedJDLHashBefore="h", relatedJDLHashAfter="h",
                relatedIntentHashBefore="h", relatedIntentHashAfter="h",
                result="ok",
            )
            for i in range(1, 10)
        ]
        session = _session(turns=turns)
        summary = context.compact_summary(session)
        assert "material.metal" in summary.acceptedDecisions
