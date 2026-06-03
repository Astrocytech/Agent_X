from pathlib import Path

from agentx_evolve.final_acceptance.acceptance_runner import (
    write_completion_record, write_latest_result,
)
from agentx_evolve.final_acceptance.acceptance_models import (
    FinalAcceptanceCompletionRecord, VERDICT_ACCEPTED,
)


class TestWriteCompletionRecord:
    def test_writes_record(self, tmp_path: Path):
        record = FinalAcceptanceCompletionRecord(
            status="VALIDATED",
            created_at="2024-01-01T00:00:00Z",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=1.0,
        )
        path = write_completion_record(record, tmp_path)
        assert path.exists()
        assert path.name == "final_acceptance_completion_record.json"
        assert ".agentx-init" in str(path)

    def test_writes_latest_result(self, tmp_path: Path):
        record = FinalAcceptanceCompletionRecord(
            status="VALIDATED",
            created_at="2024-01-01T00:00:00Z",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=1.0,
        )
        path = write_latest_result(record, tmp_path)
        assert path.exists()
        assert path.name == "latest_final_acceptance_result.json"

    def test_record_with_all_fields(self, tmp_path: Path):
        record = FinalAcceptanceCompletionRecord(
            status="VALIDATED",
            reviewed_commit="abc123",
            reviewed_branch="main",
            created_at="2024-01-01T00:00:00Z",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=0.85,
            commands_run=[{"command_name": "pytest", "status": "PASS"}],
            artifacts_created=["report.json"],
            review_environment={"python": "3.11"},
        )
        path = write_completion_record(record, tmp_path)
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "abc123" in content
        assert "pytest" in content
        assert "0.85" in content

    def test_record_empty_commands_and_artifacts(self, tmp_path: Path):
        record = FinalAcceptanceCompletionRecord(
            status="VALIDATED", created_at="t",
            final_verdict=VERDICT_ACCEPTED, implementation_rating=1.0,
        )
        path = write_completion_record(record, tmp_path)
        content = path.read_text(encoding="utf-8")
        assert '"commands_run"' in content
        assert '"artifacts_created"' in content
