"""Designer <-> Design Intent integration tests (Sprint 11).

Covers the boundary Sprint 11 adds to Designer v1: separating technical
JDL fields from aesthetic design intent, preserving intent across a
MODIFY, and proving that a pure-intent request never changes any JDL
field (the "no stale model" precondition — see
docs/bible/13-design-intent/353-intent-preservation.md and the frontend
gating logic in DesignerPanel.tsx, which uses exactly this `diff` signal).
"""

from __future__ import annotations

from jewelmind.designer.provider import FakeDesignerProvider
from jewelmind.designer.schemas import (
    NaturalLanguageDesignRequest,
    RawDesignerResponse,
    RawIntentStatement,
    RawProposedValue,
)
from jewelmind.designer.service import DesignerService
from jewelmind.domain.schema import JewelryDefinition


def S(target: str, concept: str, value: str, source: str | None = None) -> RawIntentStatement:
    return RawIntentStatement(target=target, concept=concept, value=value, sourceText=source or value)


def _request(text, mode="CREATE", current=None, current_intent=None, request_id="r1"):
    return NaturalLanguageDesignRequest(
        requestId=request_id,
        text=text,
        interactionMode=mode,
        currentJDL=current,
        currentDesignIntent=current_intent,
    )


class TestDesignerTechnicalVsIntentSeparation:
    def test_technical_and_aesthetic_are_reported_separately(self):
        raw = RawDesignerResponse(
            proposedCanonicalValues=[
                RawProposedValue(field="material.metal", value="oro rosa", sourceText="oro rosa"),
                RawProposedValue(field="setting.prongCount", value="sei", sourceText="sei griffe"),
            ],
            designIntentStatements=[S("ring", "VISUAL_WEIGHT", "delicato")],
        )
        service = DesignerService(provider=FakeDesignerProvider(response=raw))
        result = service.interpret(_request("Fammi un solitario delicato in oro rosa con sei griffe."))
        proposal = result.proposal

        assert {f.path for f in proposal.proposedFields} == {"material.metal", "setting.prongCount"}
        assert len(proposal.designIntent.statements) == 1
        assert proposal.designIntent.statements[0].value == "DELICATE"
        # the aesthetic statement must never leak into the technical JDL
        assert not any(f.path.startswith("band") for f in proposal.proposedFields)


class TestNoArbitraryNumericMapping:
    def test_delicate_band_never_changes_band_width(self):
        raw = RawDesignerResponse(
            designIntentStatements=[S("band", "VISUAL_WEIGHT", "delicate", "delicate band")]
        )
        service = DesignerService(provider=FakeDesignerProvider(response=raw))
        result = service.interpret(_request("make the band delicate"))
        assert result.proposal.candidateJDL.band.width == JewelryDefinition().band.width

    def test_bolder_never_increases_band_width_stone_diameter_or_prong_diameter(self):
        raw = RawDesignerResponse(designIntentStatements=[S("ring", "VISUAL_WEIGHT", "bold", "bolder")])
        current = JewelryDefinition()
        service = DesignerService(provider=FakeDesignerProvider(response=raw))
        result = service.interpret(_request("make it bolder", mode="MODIFY", current=current))
        candidate = result.proposal.candidateJDL
        assert candidate.band.width == current.band.width
        assert candidate.stone.diameter == current.stone.diameter
        assert candidate.setting.prongDiameter == current.setting.prongDiameter

    def test_pure_intent_request_produces_no_changed_jdl_diff(self):
        # This is exactly the signal the frontend uses to decide whether
        # applying a proposal should mark the current model stale.
        raw = RawDesignerResponse(designIntentStatements=[S("ring", "SIMPLICITY", "minimal")])
        current = JewelryDefinition()
        service = DesignerService(provider=FakeDesignerProvider(response=raw))
        result = service.interpret(_request("more minimal please", mode="MODIFY", current=current))
        assert not any(d.changed for d in result.proposal.diff)

    def test_a_real_technical_change_does_produce_a_changed_diff_entry(self):
        raw = RawDesignerResponse(
            proposedCanonicalValues=[RawProposedValue(field="material.metal", value="platinum")]
        )
        current = JewelryDefinition()
        service = DesignerService(provider=FakeDesignerProvider(response=raw))
        result = service.interpret(_request("use platinum", mode="MODIFY", current=current))
        changed = [d for d in result.proposal.diff if d.changed]
        assert len(changed) == 1
        assert changed[0].path == "material.metal"


class TestModifyExistingIntent:
    def test_intent_is_preserved_across_a_modify_that_only_changes_technical_fields(self):
        raw1 = RawDesignerResponse(designIntentStatements=[S("ring", "VISUAL_WEIGHT", "delicate")])
        service = DesignerService(provider=FakeDesignerProvider(response=raw1))
        first = service.interpret(_request("Fammi un anello delicato.", mode="CREATE"))
        stored_intent = first.proposal.designIntent

        raw2 = RawDesignerResponse(
            proposedCanonicalValues=[RawProposedValue(field="material.metal", value="platinum")]
        )
        service2 = DesignerService(provider=FakeDesignerProvider(response=raw2))
        second = service2.interpret(
            _request(
                "Change it to platinum.",
                mode="MODIFY",
                current=first.proposal.candidateJDL,
                current_intent=stored_intent,
            )
        )
        assert any(s.value == "DELICATE" for s in second.proposal.designIntent.statements)
        assert second.proposal.candidateJDL.material.metal == "platinum"


class TestMultilingualIntent:
    def test_italian_and_english_delicate_converge_on_the_same_canonical_value(self):
        raw_it = RawDesignerResponse(designIntentStatements=[S("ring", "VISUAL_WEIGHT", "delicato")])
        raw_en = RawDesignerResponse(designIntentStatements=[S("ring", "VISUAL_WEIGHT", "delicate")])
        it_result = DesignerService(provider=FakeDesignerProvider(response=raw_it)).interpret(
            _request("Vorrei un anello delicato.", request_id="it")
        )
        en_result = DesignerService(provider=FakeDesignerProvider(response=raw_en)).interpret(
            _request("I would like a delicate ring.", request_id="en")
        )
        assert it_result.proposal.designIntent.statements[0].value == "DELICATE"
        assert en_result.proposal.designIntent.statements[0].value == "DELICATE"


class TestFakeProviderIntent:
    def test_fake_provider_round_trips_intent_fields(self):
        raw = RawDesignerResponse(
            designIntentStatements=[S("stone", "VISUAL_EMPHASIS", "statement", "statement stone")]
        )
        service = DesignerService(provider=FakeDesignerProvider(response=raw))
        result = service.interpret(_request("Make the stone the visual focus."))
        assert result.proposal.designIntent.statements[0].target == "STONE"
        assert result.proposal.designIntent.statements[0].concept == "VISUAL_EMPHASIS"
