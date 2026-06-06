import json
import pytest
from pathlib import Path

from tools.agentx_evolve.final_acceptance.evidence_collector import (
    collect_evidence_item, collect_layer_evidence,
    validate_evidence_item_schema_if_json, write_evidence_manifest,
)
from tools.agentx_evolve.final_acceptance.acceptance_models import (
    FinalAcceptanceLayer, FinalAcceptanceLayerRegistry,
    MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
)


class TestCollectEvidenceItem:
    def test_file_exists_and_readable(self, tmp_path: Path):
        layer = FinalAcceptanceLayer(layer_id="L1")
        f = tmp_path / "test.txt"
        f.write_text("hello")
        item = collect_evidence_item(
            tmp_path, layer, str(f.relative_to(tmp_path)), "test", True,
        )
        assert item.exists is True
        assert item.readable is True
        assert item.sha256 is not None
        assert len(item.sha256) == 64

    def test_file_not_exists(self, tmp_path: Path):
        layer = FinalAcceptanceLayer(layer_id="L1")
        item = collect_evidence_item(
            tmp_path, layer, "nonexistent.txt", "test", True,
        )
        assert item.exists is False
        assert item.readable is False
        assert item.sha256 is None

    def test_not_required(self, tmp_path: Path):
        layer = FinalAcceptanceLayer(layer_id="L1")
        item = collect_evidence_item(
            tmp_path, layer, "missing.txt", "test", False,
        )
        assert item.required is False

    def test_artifact_timestamp(self, tmp_path: Path):
        layer = FinalAcceptanceLayer(layer_id="L1")
        f = tmp_path / "timed.txt"
        f.write_text("data")
        item = collect_evidence_item(
            tmp_path, layer, str(f.relative_to(tmp_path)), "test", True,
        )
        assert item.artifact_timestamp is not None
        assert "T" in item.artifact_timestamp

    def test_json_artifact_extracts_commit(self, tmp_path: Path):
        layer = FinalAcceptanceLayer(layer_id="L1")
        f = tmp_path / "completion.json"
        f.write_text(json.dumps({"reviewed_commit": "abc123"}), encoding="utf-8")
        item = collect_evidence_item(
            tmp_path, layer, str(f.relative_to(tmp_path)), "completion_record", True,
        )
        assert item.reviewed_commit_in_artifact == "abc123"

    def test_json_artifact_extracts_validated_commit(self, tmp_path: Path):
        layer = FinalAcceptanceLayer(layer_id="L1")
        f = tmp_path / "report.json"
        f.write_text(json.dumps({"validated_commit": "def456"}), encoding="utf-8")
        item = collect_evidence_item(
            tmp_path, layer, str(f.relative_to(tmp_path)), "review_report", True,
        )
        assert item.reviewed_commit_in_artifact == "def456"

    def test_corrupt_json(self, tmp_path: Path):
        layer = FinalAcceptanceLayer(layer_id="L1")
        f = tmp_path / "bad.json"
        f.write_text("{invalid", encoding="utf-8")
        item = collect_evidence_item(
            tmp_path, layer, str(f.relative_to(tmp_path)), "completion_record", True,
        )
        assert item.schema_valid is False
        assert "Cannot parse JSON" in (item.schema_validation_error or "")

    def test_empty_file(self, tmp_path: Path):
        layer = FinalAcceptanceLayer(layer_id="L1")
        f = tmp_path / "empty.txt"
        f.write_text("")
        item = collect_evidence_item(
            tmp_path, layer, str(f.relative_to(tmp_path)), "test", True,
        )
        assert item.exists
        assert item.readable

    def test_binary_file(self, tmp_path: Path):
        layer = FinalAcceptanceLayer(layer_id="L1")
        f = tmp_path / "data.bin"
        f.write_bytes(b"\x00\x01\x02\xff")
        item = collect_evidence_item(
            tmp_path, layer, str(f.relative_to(tmp_path)), "package", False,
        )
        assert item.exists
        assert item.readable


class TestCollectLayerEvidence:
    def test_returns_manifest(self, tmp_path: Path):
        reg = FinalAcceptanceLayerRegistry(
            acceptance_mode=MODE_SOURCE_ONLY_ACCEPTANCE,
            layers=[FinalAcceptanceLayer(layer_id="L1")],
        )
        manifest = collect_layer_evidence(tmp_path, reg)
        assert manifest.acceptance_mode == MODE_SOURCE_ONLY_ACCEPTANCE
        assert isinstance(manifest.items, list)

    def test_with_full_registry(self, tmp_path: Path):
        reg = FinalAcceptanceLayerRegistry(
            created_at="t",
            acceptance_mode=MODE_IMPLEMENTATION_ACCEPTANCE,
            layers=[
                FinalAcceptanceLayer(
                    layer_id="L1",
                    expected_completion_record_path="some/path.json",
                ),
            ],
        )
        manifest = collect_layer_evidence(tmp_path, reg)
        assert len(manifest.items) > 0

    def test_bootstrap_self_flag(self, tmp_path: Path):
        reg = FinalAcceptanceLayerRegistry(
            created_at="t",
            acceptance_mode=MODE_IMPLEMENTATION_ACCEPTANCE,
            bootstrap_self=True,
            layers=[
                FinalAcceptanceLayer(
                    layer_id="FINAL_SYSTEM_ACCEPTANCE",
                    expected_completion_record_path="comp.json",
                ),
            ],
        )
        manifest = collect_layer_evidence(tmp_path, reg, bootstrap_self=True)
        assert manifest is not None

    def test_empty_layers(self, tmp_path: Path):
        reg = FinalAcceptanceLayerRegistry(created_at="t", layers=[])
        manifest = collect_layer_evidence(tmp_path, reg)
        assert len(manifest.items) == 0

    def test_manifest_has_reviewed_commit(self, tmp_path: Path):
        reg = FinalAcceptanceLayerRegistry(
            reviewed_commit="abc", created_at="t", layers=[],
        )
        manifest = collect_layer_evidence(tmp_path, reg)
        assert manifest.reviewed_commit == "abc"


class TestValidateEvidenceItemSchemaIfJson:
    def test_returns_same_item(self, tmp_path: Path):
        layer = FinalAcceptanceLayer(layer_id="L1")
        item = collect_evidence_item(tmp_path, layer, "missing.txt", "test", False)
        result = validate_evidence_item_schema_if_json(tmp_path, item)
        assert result.layer_id == "L1"

    def test_preserves_item_state(self, tmp_path: Path):
        layer = FinalAcceptanceLayer(layer_id="L2")
        f = tmp_path / "data.txt"
        f.write_text("test")
        item = collect_evidence_item(tmp_path, layer, str(f.relative_to(tmp_path)), "test", True)
        result = validate_evidence_item_schema_if_json(tmp_path, item)
        assert result.exists == item.exists
        assert result.sha256 == item.sha256


class TestWriteEvidenceManifest:
    def test_writes_file(self, tmp_path: Path):
        reg = FinalAcceptanceLayerRegistry(created_at="t", layers=[])
        from tools.agentx_evolve.final_acceptance.evidence_collector import FinalAcceptanceEvidenceManifest
        manifest = FinalAcceptanceEvidenceManifest(
            created_at="t", acceptance_mode=MODE_SOURCE_ONLY_ACCEPTANCE,
        )
        path = write_evidence_manifest(manifest, tmp_path)
        assert path.exists()
        assert path.name == "final_acceptance_evidence_manifest.json"

    def test_content(self, tmp_path: Path):
        from tools.agentx_evolve.final_acceptance.evidence_collector import FinalAcceptanceEvidenceManifest
        manifest = FinalAcceptanceEvidenceManifest(
            reviewed_commit="abc", created_at="t",
            acceptance_mode=MODE_IMPLEMENTATION_ACCEPTANCE,
        )
        path = write_evidence_manifest(manifest, tmp_path)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["schema_id"] == "final_acceptance_evidence_manifest.schema.json"
        assert data["reviewed_commit"] == "abc"

    def test_includes_items(self, tmp_path: Path):
        from tools.agentx_evolve.final_acceptance.evidence_collector import (
            FinalAcceptanceEvidenceManifest, FinalAcceptanceEvidenceItem,
        )
        item = FinalAcceptanceEvidenceItem(
            layer_id="L1", artifact_path="/a", artifact_type="t", exists=True,
        )
        manifest = FinalAcceptanceEvidenceManifest(
            created_at="t", items=[item],
        )
        path = write_evidence_manifest(manifest, tmp_path)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert len(data["items"]) == 1
        assert data["items"][0]["layer_id"] == "L1"
