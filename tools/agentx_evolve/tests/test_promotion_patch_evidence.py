import pytest
from agentx_evolve.promotion.promotion_models import PromotionEvidenceManifest, to_dict


class TestPromotionPatchEvidence:
    def test_manifest_records_patch_evidence_refs(self):
        manifest = PromotionEvidenceManifest(
            manifest_id="m-001",
            patch_evidence_refs=["patch-ev-001", "patch-ev-002"],
        )
        assert len(manifest.patch_evidence_refs) == 2
        assert "patch-ev-001" in manifest.patch_evidence_refs

    def test_manifest_serializes_correctly(self):
        manifest = PromotionEvidenceManifest(
            manifest_id="m-002",
            candidate_id="cand-001",
            source_commit="abc123",
            patch_evidence_refs=["patch-ev-001"],
        )
        d = to_dict(manifest)
        assert d["manifest_id"] == "m-002"
        assert d["candidate_id"] == "cand-001"
        assert d["source_commit"] == "abc123"
        assert d["patch_evidence_refs"] == ["patch-ev-001"]

    def test_manifest_empty_by_default(self):
        manifest = PromotionEvidenceManifest()
        assert manifest.patch_evidence_refs == []
        assert manifest.manifest_id == ""
        assert manifest.candidate_id == ""

    def test_manifest_with_multiple_evidence_types(self):
        manifest = PromotionEvidenceManifest(
            manifest_id="m-003",
            patch_evidence_refs=["pe-001", "pe-002"],
            tool_evidence_refs=["te-001"],
            git_evidence_refs=["ge-001"],
        )
        assert len(manifest.patch_evidence_refs) == 2
        assert len(manifest.tool_evidence_refs) == 1
        assert len(manifest.git_evidence_refs) == 1

    def test_manifest_hash_field(self):
        manifest = PromotionEvidenceManifest(
            manifest_id="m-004",
            manifest_hash="abc123hash",
        )
        assert manifest.manifest_hash == "abc123hash"
