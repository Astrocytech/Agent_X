import pytest
from agentx_evolve.context.context_artifact_writer import write_review_report, write_completion_record


class TestContextEvidence:
    def test_write_review_report(self, tmp_path):
        result = write_review_report(review_data={"status": "pass"}, repo_root=tmp_path)
        assert result is not None

    def test_write_completion_record(self, tmp_path):
        result = write_completion_record(record_data={"status": "done"}, repo_root=tmp_path)
        assert result is not None
