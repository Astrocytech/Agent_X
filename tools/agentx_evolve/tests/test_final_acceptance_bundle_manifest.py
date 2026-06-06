from pathlib import Path

from tools.agentx_evolve.final_acceptance.bundle_manifest import (
    compute_hash_of_hashes, build_final_acceptance_bundle, write_bundle_manifest,
)
from tools.agentx_evolve.final_acceptance.acceptance_models import (
    FinalAcceptanceArtifactHash,
)
from tools.agentx_evolve.final_acceptance.artifact_writer import runtime_root


class TestComputeHashOfHashes:
    def test_empty_list(self):
        result = compute_hash_of_hashes([])
        assert isinstance(result, str)
        assert len(result) == 64

    def test_single_hash(self):
        hashes = [FinalAcceptanceArtifactHash(artifact_path="/a", sha256="ff" * 32)]
        result = compute_hash_of_hashes(hashes)
        assert isinstance(result, str)
        assert len(result) == 64

    def test_multiple_hashes_sorted_by_path(self):
        hashes = [
            FinalAcceptanceArtifactHash(artifact_path="/b", sha256="aa" * 32),
            FinalAcceptanceArtifactHash(artifact_path="/a", sha256="bb" * 32),
        ]
        result = compute_hash_of_hashes(hashes)
        assert isinstance(result, str)

    def test_deterministic(self):
        hashes = [
            FinalAcceptanceArtifactHash(artifact_path="/a", sha256="cc" * 32),
        ]
        r1 = compute_hash_of_hashes(hashes)
        r2 = compute_hash_of_hashes(hashes)
        assert r1 == r2

    def test_different_inputs_different_hashes(self):
        h1 = [FinalAcceptanceArtifactHash(artifact_path="/a", sha256="aa" * 32)]
        h2 = [FinalAcceptanceArtifactHash(artifact_path="/a", sha256="bb" * 32)]
        assert compute_hash_of_hashes(h1) != compute_hash_of_hashes(h2)


class TestBuildFinalAcceptanceBundle:
    def test_minimal_bundle(self, tmp_path: Path):
        bundle = build_final_acceptance_bundle(
            repo_root=tmp_path,
            reviewed_commit=None,
            artifact_hashes=[],
        )
        assert bundle["schema_version"] == "1.0"
        assert bundle["bundle_status"] == "FINALIZED"
        assert bundle["reviewed_commit"] is None
        assert bundle["included_artifacts"] == []
        assert bundle["artifact_hashes"] == {}
        assert bundle["layer_evidence_hashes"] == {}
        assert bundle["command_output_hashes"] == {}

    def test_with_hashes(self, tmp_path: Path):
        hashes = [
            FinalAcceptanceArtifactHash(artifact_path="/a", sha256="aa"),
            FinalAcceptanceArtifactHash(artifact_path="/b", sha256="bb"),
        ]
        bundle = build_final_acceptance_bundle(
            repo_root=tmp_path,
            reviewed_commit="abc123",
            artifact_hashes=hashes,
        )
        assert bundle["reviewed_commit"] == "abc123"
        assert len(bundle["included_artifacts"]) == 2
        assert bundle["artifact_hashes"]["/a"] == "aa"
        assert bundle["artifact_hashes"]["/b"] == "bb"

    def test_with_layer_and_command_hashes(self, tmp_path: Path):
        bundle = build_final_acceptance_bundle(
            repo_root=tmp_path,
            reviewed_commit="abc",
            artifact_hashes=[],
            layer_evidence_hashes={"L1": "h1"},
            command_output_hashes={"cmd": "h2"},
        )
        assert bundle["layer_evidence_hashes"] == {"L1": "h1"}
        assert bundle["command_output_hashes"] == {"cmd": "h2"}

    def test_hash_of_hashes_present(self, tmp_path: Path):
        hashes = [FinalAcceptanceArtifactHash(artifact_path="/a", sha256="dd" * 32)]
        bundle = build_final_acceptance_bundle(tmp_path, "c", hashes)
        assert bundle["hash_of_hashes"] == compute_hash_of_hashes(hashes)

    def test_artifacts_sorted(self, tmp_path: Path):
        hashes = [
            FinalAcceptanceArtifactHash(artifact_path="/z", sha256="zz"),
            FinalAcceptanceArtifactHash(artifact_path="/a", sha256="aa"),
        ]
        bundle = build_final_acceptance_bundle(tmp_path, "c", hashes)
        assert bundle["included_artifacts"] == ["/a", "/z"]


class TestWriteBundleManifest:
    def test_writes_file(self, tmp_path: Path):
        bundle = build_final_acceptance_bundle(tmp_path, None, [])
        path = write_bundle_manifest(bundle, tmp_path)
        assert path.exists()
        assert path.name == "final_acceptance_bundle.json"
        assert runtime_root(tmp_path) in path.parents

    def test_written_content_is_valid(self, tmp_path: Path):
        bundle = build_final_acceptance_bundle(tmp_path, "abc", [])
        write_bundle_manifest(bundle, tmp_path)
        import json
        path = runtime_root(tmp_path) / "final_acceptance_bundle.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["bundle_status"] == "FINALIZED"
