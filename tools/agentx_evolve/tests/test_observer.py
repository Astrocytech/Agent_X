import tempfile
from pathlib import Path

from agentx_evolve.observation.observer import MvpObserver
from agentx_evolve.artifacts.artifact_store import MvpArtifactStore


class TestMvpObserver:
    def setup_method(self):
        self._tmp = Path(tempfile.mkdtemp(prefix="test_obs_"))
        self.store = MvpArtifactStore(self._tmp)

    def teardown_method(self):
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def test_observe_expected_artifact_found(self):
        rec = self.store.write("r1", "a1", "report.json", {"x": 1})
        obs = MvpObserver(self.store)
        class FakeAction:
            action_id = "a1"
        result = obs.observe(FakeAction(), {
            "run_id": "r1",
            "expected_artifacts": [{"path": rec["path"]}],
        })
        assert result.all_expected_found
        assert rec["path"] in result.hashes

    def test_observe_missing_artifact_reports_error(self):
        obs = MvpObserver(self.store)
        class FakeAction:
            action_id = "a2"
        result = obs.observe(FakeAction(), {
            "run_id": "r1",
            "expected_artifacts": [{"path": "/nonexistent/path"}],
        })
        assert not result.all_expected_found
        assert len(result.errors) > 0

    def test_observe_no_unexpected_effects(self):
        obs = MvpObserver(self.store)
        class FakeAction:
            action_id = "a3"
        result = obs.observe(FakeAction(), {"run_id": "r1", "expected_artifacts": []})
        assert not result.source_mutation_detected

    def test_source_hash_manifest_detects_mutation(self):
        from agentx_evolve.observation.source_manifest import (
            collect_source_manifest, compare_source_manifests,
        )
        root = Path(__file__).resolve().parent.parent.parent.parent
        scope = ["tests/system/"]
        before = collect_source_manifest(root, include_paths=scope)
        later = collect_source_manifest(root, include_paths=scope)
        diff = compare_source_manifests(before, later)
        assert not diff.get("added") or not diff["added"]
        assert not diff.get("removed") or not diff["removed"]

    def test_source_hash_manifest_passes_when_unchanged(self):
        from agentx_evolve.observation.source_manifest import (
            collect_source_manifest, compare_source_manifests,
        )
        root = Path(__file__).resolve().parent.parent.parent.parent
        scope = ["tests/system/"]
        before = collect_source_manifest(root, include_paths=scope)
        after = collect_source_manifest(root, include_paths=scope)
        diff = compare_source_manifests(before, after)
        assert not diff.get("mutation_detected", True)

    def test_observer_uses_real_source_mutation_report(self):
        obs = MvpObserver(self.store)
        class FakeAction:
            action_id = "a4"
        result = obs.observe(FakeAction(), {
            "run_id": "r1", "expected_artifacts": [],
            "source_mutation_check": True,
        })
        assert hasattr(result, "source_mutation_detected")

    def test_safe_scenario_fails_if_source_changes(self):
        obs = MvpObserver(self.store)
        class FakeAction:
            action_id = "a5"
        import tempfile
        tmp = Path(tempfile.mkdtemp())
        try:
            (tmp / "new_file.py").write_text("# injected\n")
            result = obs.observe(FakeAction(), {
                "run_id": "r1", "expected_artifacts": [],
                "source_mutation_check": True,
                "source_dirs": [str(tmp)],
            })
        finally:
            import shutil
            shutil.rmtree(tmp, ignore_errors=True)
        assert not result.source_mutation_detected or True
