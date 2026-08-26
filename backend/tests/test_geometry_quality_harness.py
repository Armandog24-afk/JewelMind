"""GOLDEN_REAL_GENERATION_TEST, GOLDEN_HUMAN_READABLE_DIFF_TEST,
GOLDEN_NO_AUTO_UPDATE_TEST, and the mandated intentional-failure and
repeatability tests (brief sections 36-37).
"""

from __future__ import annotations

import inspect

from jewelmind.domain.defaults import default_definition
from jewelmind.geometry_quality import harness as harness_module
from jewelmind.geometry_quality.compare import compare_snapshot
from jewelmind.geometry_quality.fingerprint import collect_fingerprint
from jewelmind.geometry_quality.harness import (
    accept_candidate_baseline,
    generate_candidate_baseline,
    verify_all_goldens,
    verify_golden,
)
from jewelmind.geometry_quality.models import ArtifactChange
from jewelmind.geometry_quality.registry import list_golden_ids, load_golden
from jewelmind.geometry_quality.snapshot import generate_snapshot

GOLDEN_ID = "SOL-001-default-solitaire"


class TestRealGeneration:
    """Every golden in the real suite verifies against its own accepted
    baseline using the real pipeline — never a mock."""

    def test_every_golden_in_the_manifest_passes(self):
        results = verify_all_goldens()
        assert len(results) >= 8
        for result in results:
            assert result.status in ("PASS", "PASS_WITH_KNOWN_LIMITATIONS"), result.message

    def test_verify_golden_uses_the_real_pipeline_not_a_mock(self):
        result = verify_golden(GOLDEN_ID)
        assert result.diff is not None
        assert result.diff.actualFingerprint.kernelVersion  # a real cadquery.__version__ string


class TestHumanReadableDiff:
    def test_a_clean_diff_reads_as_no_regression(self):
        golden = load_golden(GOLDEN_ID)
        diff = compare_snapshot(
            GOLDEN_ID,
            golden.geometrySnapshot,
            golden.geometrySnapshot,
            golden.versionFingerprint,
            golden.versionFingerprint,
        )
        assert diff.severity == "NONE"
        assert "no regression detected" in diff.human_readable()

    def test_a_real_verification_never_reports_a_false_regression(self):
        # A real cross-platform rerun can legitimately differ from the
        # recorded baseline at the ULP level (severity INFO, still within
        # tolerance) — see 505-comparison-tolerance-policy.md. This must
        # never read as a regression, but it is not guaranteed to be the
        # literal string "no regression detected" on every platform.
        result = verify_golden(GOLDEN_ID)
        assert result.status in ("PASS", "PASS_WITH_KNOWN_LIMITATIONS")
        assert result.diff.severity in ("NONE", "INFO")

    def test_failing_diff_names_the_metric_and_both_values(self):
        golden = load_golden(GOLDEN_ID)
        mutated = golden.geometrySnapshot.model_copy(deep=True)
        for c in mutated.components:
            if c.componentId == "band":
                c.volumeMm3 = c.volumeMm3 * 1.5
        diff = compare_snapshot(
            GOLDEN_ID, golden.geometrySnapshot, mutated, golden.versionFingerprint, golden.versionFingerprint
        )
        text = diff.human_readable()
        assert "band" in text and "volumeMm3" in text
        assert "Expected:" in text and "Actual:" in text and "Delta:" in text and "Tolerance:" in text


class TestIntentionalFailureDetection:
    """A deliberately modified COPY of a real snapshot must be flagged —
    the real accepted baseline on disk is never touched (brief section
    36)."""

    def test_altered_component_count_is_flagged_as_a_regression(self):
        golden = load_golden(GOLDEN_ID)
        mutated = golden.geometrySnapshot.model_copy(deep=True)
        mutated.assembly.componentCount = 2
        diff = compare_snapshot(
            GOLDEN_ID, golden.geometrySnapshot, mutated, golden.versionFingerprint, golden.versionFingerprint
        )
        assert diff.severity == "REGRESSION"
        assert diff.requiresBaselineReview is True
        assert any(c.path == "assembly.componentCount" for c in diff.exactChanges)

    def test_volume_altered_beyond_tolerance_is_flagged(self):
        golden = load_golden(GOLDEN_ID)
        mutated = golden.geometrySnapshot.model_copy(deep=True)
        for c in mutated.components:
            if c.componentId == "band":
                c.volumeMm3 = c.volumeMm3 * 2
        diff = compare_snapshot(
            GOLDEN_ID, golden.geometrySnapshot, mutated, golden.versionFingerprint, golden.versionFingerprint
        )
        assert diff.severity == "REGRESSION"
        assert any(not n.withinTolerance for n in diff.numericChanges)

    def test_the_real_accepted_baseline_file_is_unchanged_by_this_test(self):
        reloaded = load_golden(GOLDEN_ID)
        assert reloaded.geometrySnapshot.assembly.componentCount == 4


class TestRepeatability:
    """Generate the default solitaire's snapshot 3 times; document observed
    variability rather than assuming it (brief section 37)."""

    def test_three_repeated_generations_are_bit_identical_locally(self):
        runs = [generate_snapshot(default_definition())[0] for _ in range(3)]
        dumps = [r.model_dump() for r in runs]
        assert dumps[0] == dumps[1] == dumps[2], (
            "Observed local non-determinism: 0 differences expected on a fixed "
            "machine/kernel build (ATLAS-GOV-003). The only measured drift is "
            "cross-platform — see docs/bible/16-geometry-inspection/486-inspection-determinism.md."
        )


class TestArtifactSeverityEscalation:
    """A real artifact regression must never be masked by a prior
    INFO-level (within-tolerance) geometric diff — verify_golden() must
    still escalate to REGRESSION."""

    def test_artifact_regression_escalates_even_when_geometric_diff_is_info(self, monkeypatch):
        def fake_step_check(_model):
            return [ArtifactChange(artifactType="STEP", description="synthetic test regression")]

        def fake_stl_check(_model, _definition):
            return []

        # Force the geometric comparison to look INFO-level (a real,
        # within-tolerance numeric drift) rather than NONE, so the
        # escalation logic is exercised on its non-trivial branch.
        original_compare = harness_module.compare_snapshot

        def fake_compare(*args, **kwargs):
            diff = original_compare(*args, **kwargs)
            return diff.model_copy(update={"severity": "INFO"})

        monkeypatch.setattr(harness_module, "step_roundtrip_check", fake_step_check)
        monkeypatch.setattr(harness_module, "stl_structure_check", fake_stl_check)
        monkeypatch.setattr(harness_module, "compare_snapshot", fake_compare)

        result = verify_golden(GOLDEN_ID, check_artifacts=True)
        assert result.diff.severity == "REGRESSION"
        assert result.status == "REGRESSION_DETECTED"


class TestNoAutoUpdate:
    """CI/agents must never overwrite a failing baseline automatically
    (QUALITY-GOV-003) — enforced structurally: verify_golden/
    verify_all_goldens/generate_candidate_baseline never call save_golden,
    only accept_candidate_baseline does, and it always requires an
    explicit human call."""

    def test_verify_golden_never_writes_to_the_registry(self):
        source = inspect.getsource(verify_golden)
        assert "save_golden" not in source
        assert "save_candidate" not in source

    def test_verify_all_goldens_never_writes_to_the_registry(self):
        source = inspect.getsource(verify_all_goldens)
        assert "save_golden" not in source

    def test_generate_candidate_baseline_never_writes_to_the_registry(self):
        source = inspect.getsource(generate_candidate_baseline)
        assert "save_golden" not in source

    def test_only_accept_candidate_baseline_calls_save_golden(self):
        source = inspect.getsource(accept_candidate_baseline)
        assert "save_golden" in source

    def test_a_regression_detected_by_verify_golden_does_not_change_the_file_on_disk(self):
        before = load_golden(GOLDEN_ID).geometrySnapshot.model_dump()
        # Simulate a coding agent running verify on every golden after a
        # regression-inducing code change was made elsewhere: this must
        # never rewrite the accepted baseline no matter how many times
        # it's called or what it finds.
        for _ in range(2):
            verify_golden(GOLDEN_ID)
            verify_all_goldens()
        after = load_golden(GOLDEN_ID).geometrySnapshot.model_dump()
        assert before == after


class TestVersionFingerprint:
    def test_fingerprint_uses_the_real_installed_kernel_version(self):
        _snapshot, model, _report = generate_snapshot(default_definition())
        fp = collect_fingerprint(model)
        import cadquery as cq

        assert fp.kernelVersion == cq.__version__
        assert fp.jdlSchemaVersion
        assert fp.forgeRuleSetVersion != ""

    def test_every_accepted_golden_has_a_complete_fingerprint(self):
        for golden_id in list_golden_ids():
            fp = load_golden(golden_id).versionFingerprint
            assert fp.kernelVersion and fp.jdlSchemaVersion and fp.atlasGeneratorVersion
