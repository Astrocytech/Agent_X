from pathlib import Path

from agentx_evolve.final_acceptance.evidence_freshness import (
    build_evidence_freshness_report, write_evidence_freshness_report,
)
from agentx_evolve.final_acceptance.acceptance_models import (
    FinalAcceptanceEvidenceManifest, FinalAcceptanceEvidenceItem,
)
from agentx_evolve.final_acceptance.artifact_writer import runtime_root


class TestBuildEvidenceFreshnessReport:
    def test_no_reviewed_commit_returns_not_checked(self, tmp_path: Path):
        manifest = FinalAcceptanceEvidenceManifest(items=[])
        report = build_evidence_freshness_report(
            repo_root=tmp_path, evidence_manifest=manifest,
            reviewed_commit=None, acceptance_mode="TEST",
            required_layer_ids=[],
        )
        assert report["report_status"] == "NOT_CHECKED"
        assert report["reviewed_commit"] is None
        assert report["layers"] == []

    def test_empty_manifest_and_no_required(self, tmp_path: Path):
        manifest = FinalAcceptanceEvidenceManifest(items=[])
        report = build_evidence_freshness_report(
            repo_root=tmp_path, evidence_manifest=manifest,
            reviewed_commit="abc123", acceptance_mode="TEST",
            required_layer_ids=[],
        )
        assert report["report_status"] in ("PASS", "NOT_CHECKED")
        assert report["reviewed_commit"] == "abc123"

    def test_required_layer_missing_from_manifest(self, tmp_path: Path):
        manifest = FinalAcceptanceEvidenceManifest(items=[])
        report = build_evidence_freshness_report(
            repo_root=tmp_path, evidence_manifest=manifest,
            reviewed_commit="abc123", acceptance_mode="TEST",
            required_layer_ids=["L1"],
        )
        layers = report["layers"]
        assert any(l["layer_id"] == "L1" for l in layers)
        l1 = next(l for l in layers if l["layer_id"] == "L1")
        assert l1["freshness_status"] == "NOT_CHECKED"

    def test_exact_match_commit_is_fresh(self, tmp_path: Path):
        item = FinalAcceptanceEvidenceItem(
            layer_id="L1", reviewed_commit_in_artifact="abc123",
        )
        manifest = FinalAcceptanceEvidenceManifest(items=[item])
        report = build_evidence_freshness_report(
            repo_root=tmp_path, evidence_manifest=manifest,
            reviewed_commit="abc123", acceptance_mode="TEST",
            required_layer_ids=["L1"],
        )
        l1 = next(l for l in report["layers"] if l["layer_id"] == "L1")
        assert l1["freshness_status"] == "FRESH"
        assert l1["commit_relation"] == "exact_match"

    def test_no_layer_evidence_commit_is_stale(self, tmp_path: Path):
        item = FinalAcceptanceEvidenceItem(
            layer_id="L1", reviewed_commit_in_artifact=None,
        )
        manifest = FinalAcceptanceEvidenceManifest(items=[item])
        report = build_evidence_freshness_report(
            repo_root=tmp_path, evidence_manifest=manifest,
            reviewed_commit="abc123", acceptance_mode="TEST",
            required_layer_ids=["L1"],
        )
        l1 = next(l for l in report["layers"] if l["layer_id"] == "L1")
        assert l1["freshness_status"] == "STALE_REQUIRES_REVALIDATION"

    def test_duplicate_layer_ids_deduped(self, tmp_path: Path):
        items = [
            FinalAcceptanceEvidenceItem(layer_id="L1", reviewed_commit_in_artifact="abc"),
            FinalAcceptanceEvidenceItem(layer_id="L1", reviewed_commit_in_artifact="def"),
        ]
        manifest = FinalAcceptanceEvidenceManifest(items=items)
        report = build_evidence_freshness_report(
            repo_root=tmp_path, evidence_manifest=manifest,
            reviewed_commit="abc123", acceptance_mode="TEST",
            required_layer_ids=["L1"],
        )
        l1_layers = [l for l in report["layers"] if l["layer_id"] == "L1"]
        assert len(l1_layers) == 1

    def test_acceptance_mode_in_report(self, tmp_path: Path):
        manifest = FinalAcceptanceEvidenceManifest(items=[])
        report = build_evidence_freshness_report(
            repo_root=tmp_path, evidence_manifest=manifest,
            reviewed_commit="abc", acceptance_mode="PRODUCTION_ACCEPTANCE",
            required_layer_ids=[],
        )
        assert report["acceptance_mode"] == "PRODUCTION_ACCEPTANCE"


class TestWriteEvidenceFreshnessReport:
    def test_writes_report(self, tmp_path: Path):
        manifest = FinalAcceptanceEvidenceManifest(items=[])
        report = build_evidence_freshness_report(
            tmp_path, manifest, None, "TEST", [],
        )
        path = write_evidence_freshness_report(report, tmp_path)
        assert path.exists()
        assert path.name == "final_acceptance_evidence_freshness_report.json"

    def test_writes_to_runtime_root(self, tmp_path: Path):
        manifest = FinalAcceptanceEvidenceManifest(items=[])
        report = build_evidence_freshness_report(
            tmp_path, manifest, None, "TEST", [],
        )
        path = write_evidence_freshness_report(report, tmp_path)
        assert runtime_root(tmp_path) in path.parents
