import pytest
from agentx_evolve.promotion.promotion_models import PromotionEvidenceManifest, to_dict


class TestPromotionToolEvidence:
    def test_manifest_records_tool_evidence_refs(self):
        manifest = PromotionEvidenceManifest(
            manifest_id="m-001",
            tool_evidence_refs=["tool-ev-001", "tool-ev-002"],
        )
        assert len(manifest.tool_evidence_refs) == 2
        assert "tool-ev-001" in manifest.tool_evidence_refs

    def test_manifest_serializes_with_tool_evidence(self):
        manifest = PromotionEvidenceManifest(
            manifest_id="m-002",
            candidate_id="cand-001",
            tool_evidence_refs=["te-001"],
            patch_evidence_refs=["pe-001"],
        )
        d = to_dict(manifest)
        assert d["tool_evidence_refs"] == ["te-001"]
        assert d["patch_evidence_refs"] == ["pe-001"]

    def test_manifest_empty_tool_evidence_by_default(self):
        manifest = PromotionEvidenceManifest(manifest_id="m-003")
        assert manifest.tool_evidence_refs == []

    def test_manifest_with_multiple_tool_refs(self):
        refs = [f"tool-ev-{i}" for i in range(5)]
        manifest = PromotionEvidenceManifest(
            manifest_id="m-004",
            tool_evidence_refs=refs,
        )
        assert len(manifest.tool_evidence_refs) == 5
