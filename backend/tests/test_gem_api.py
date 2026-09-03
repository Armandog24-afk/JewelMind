"""The gem endpoints (Sprint 21, brief section 27).

Exercised through the real FastAPI app, so the tests cover what a client
actually receives — status codes, error bodies and response shapes — rather
than the functions behind the routes.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from jewelmind.api.app import create_app
from jewelmind.gem.registry import GEM_REGISTRY, current_gem_ids
from jewelmind.gem.resolution import GEM_SYSTEM_VERSION
from jewelmind.gem.visual import GEM_VISUAL_PROFILES

client = TestClient(create_app())


class TestRegistryEndpoint:
    def test_it_returns_every_current_entry_and_profile(self):
        response = client.get("/api/gems")
        assert response.status_code == 200
        body = response.json()
        assert body["registryVersion"] == GEM_SYSTEM_VERSION
        assert {g["gemId"] for g in body["gems"]} == set(current_gem_ids())
        assert len(body["visualProfiles"]) == len(GEM_VISUAL_PROFILES)

    def test_it_states_what_the_registry_is_not(self):
        note = client.get("/api/gems").json()["note"].lower()
        assert "not a gemological database" in note
        assert "certification" in note

    def test_no_entry_claims_professional_validation(self):
        for entry in client.get("/api/gems").json()["gems"]:
            assert entry["provenance"] != "PROFESSIONALLY_VALIDATED"


class TestDetailEndpoint:
    def test_it_returns_one_entry_with_its_visual_profile(self):
        response = client.get("/api/gems/corundum.ruby")
        assert response.status_code == 200
        body = response.json()
        assert body["gem"]["gemId"] == "corundum.ruby"
        assert body["visualProfile"]["profileId"] == (
            GEM_REGISTRY["corundum.ruby"].defaultVisualProfileId
        )

    def test_an_unknown_but_wellformed_id_is_a_404(self):
        response = client.get("/api/gems/tanzanite")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "GEM_NOT_FOUND"

    def test_a_malformed_id_is_a_400_and_never_a_lookup(self):
        response = client.get("/api/gems/Not_A_Valid_Id")
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "GEM_ID_INVALID"

    def test_an_error_body_exposes_no_server_path(self):
        for gem_id in ("Not_A_Valid_Id", "tanzanite"):
            body = client.get(f"/api/gems/{gem_id}").text
            assert "jewelmind\\" not in body
            assert "/backend/" not in body
            assert "Traceback" not in body


class TestResolveEndpoint:
    def test_it_resolves_an_alias_in_either_language(self):
        for term, expected in [("rubino", "corundum.ruby"), ("ruby", "corundum.ruby")]:
            body = client.post("/api/gems/resolve", json={"term": term}).json()
            assert body["gemId"] == expected
            assert body["gem"]["gemId"] == expected

    def test_an_unrecognized_term_resolves_to_null_rather_than_a_guess(self):
        body = client.post("/api/gems/resolve", json={"term": "tanzanite"}).json()
        assert body["gemId"] is None
        assert body["gem"] is None

    def test_an_empty_term_is_rejected_by_the_request_schema(self):
        assert client.post("/api/gems/resolve", json={"term": ""}).status_code == 422


class TestValidateEndpoint:
    def test_a_valid_identity_validates_and_resolves(self):
        response = client.post(
            "/api/gems/validate",
            json={"gem": {"gemId": "corundum.ruby", "origin": "NATURAL"}},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["valid"] is True
        assert body["results"] == []
        assert body["resolved"]["definition"]["gemId"] == "corundum.ruby"

    def test_an_inapplicable_origin_is_reported_as_invalid(self):
        body = client.post(
            "/api/gems/validate",
            json={"gem": {"gemId": "simulant.cubic_zirconia", "origin": "NATURAL"}},
        ).json()
        assert body["valid"] is False
        assert [r["ruleId"] for r in body["results"]] == ["JM-GEM-002"]

    def test_an_unregistered_gem_warns_without_blocking(self):
        body = client.post(
            "/api/gems/validate", json={"gem": {"gemId": "tanzanite"}}
        ).json()
        assert body["valid"] is True
        assert body["results"][0]["ruleId"] == "JM-GEM-001"
        assert body["results"][0]["severity"] == "warning"
        assert body["resolved"]["wasUnresolved"] is True

    def test_a_custom_gem_without_a_name_is_rejected_by_the_schema(self):
        response = client.post(
            "/api/gems/validate", json={"gem": {"gemId": "custom"}}
        )
        assert response.status_code == 422

    def test_validation_never_returns_a_gemological_claim(self):
        forbidden = ("hardness", "mohs", "durab", "recommend", "safe to")
        for gem in [
            {"gemId": "pearl", "origin": "NATURAL"},
            {"gemId": "beryl.emerald", "origin": "NATURAL"},
            {"gemId": "tanzanite"},
        ]:
            body = client.post("/api/gems/validate", json={"gem": gem}).json()
            for result in body["results"]:
                lowered = result["message"].lower()
                for term in forbidden:
                    assert term not in lowered, (gem, result)


class TestGemDoesNotForceRegeneration:
    def test_generating_twice_with_different_gems_reuses_the_geometry(self):
        """A semantic-only edit must not rebuild the model (brief section 24)."""

        from jewelmind.domain.defaults import default_definition

        base = default_definition().model_dump(mode="json")
        base["band"]["width"] = 2.63  # a width no other test uses, so the
        # cache entry this test relies on is its own

        ruby = {**base, "stone": {**base["stone"], "gem": {"gemId": "corundum.ruby"}}}
        sapphire = {
            **base,
            "stone": {**base["stone"], "gem": {"gemId": "corundum.sapphire"}},
        }

        first = client.post("/api/models/generate", json=ruby)
        assert first.status_code == 200, first.text
        second = client.post("/api/models/generate", json=sapphire)
        assert second.status_code == 200, second.text

        a, b = first.json(), second.json()
        # A different design (the gem changed) with the SAME geometry.
        assert a["definitionHash"] != b["definitionHash"]
        assert a["modelId"] != b["modelId"]
        assert (
            a["metadata"]["combinedMetalVolumeMm3"]
            == b["metadata"]["combinedMetalVolumeMm3"]
        )
        # Reuse, not a fast rebuild: an actual rebuild always takes measurable
        # time, so a reported duration of exactly zero is the observable proof.
        assert b["metadata"]["generationDurationSeconds"] == 0.0
        assert a["metadata"]["generationDurationSeconds"] > 0.0
