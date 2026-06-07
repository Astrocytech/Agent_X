import pytest
from agentx_evolve.worker.patch_proposal_builder import build_patch_proposal


class TestBuildPatchProposal:
    def test_build(self):
        result = build_patch_proposal({"analysis_id": "a-001", "changes": ["file1.py"]})
        assert result["based_on_analysis"] == "a-001"
        assert result["changes"] == ["file1.py"]
        assert result["status"] == "proposed"
