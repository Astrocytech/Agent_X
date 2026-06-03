import pytest
import json
from pathlib import Path
from agentx_evolve.context.context_models import TaskPack, ContextPack, ContextItem
from agentx_evolve.context.context_artifact_writer import (
    write_context_pack_artifacts,
    write_latest_context_pack,
    write_context_pack_evidence,
    append_context_pack_history,
)


class TestContextArtifactWriterNegative:
    def test_empty_task_pack_writes(self, tmp_path):
        tp = TaskPack(
            task_pack_id="tp-empty",
            created_at="2026-01-01T00:00:00Z",
            task_input=None,
            context_pack=None,
        )
        result = write_context_pack_artifacts(tp, tmp_path)
        assert result["artifact_root"] is not None

    def test_non_existent_repo_root_creates(self, tmp_path):
        nested = tmp_path / "a" / "b" / "c"
        tp = TaskPack(
            task_pack_id="tp-nested",
            created_at="2026-01-01T00:00:00Z",
            context_pack=ContextPack(
                context_pack_id="cp-nested",
                task_input_id="ti-nested",
                max_context_tokens=100,
            ),
        )
        result = write_context_pack_artifacts(tp, nested)
        assert Path(result["artifact_root"]).exists()

    def test_malformed_evidence_record(self, tmp_path):
        class Bad: pass
        result = write_context_pack_evidence({"bad": Bad()}, tmp_path)
        assert Path(result["evidence_path"]).exists()

    def test_atomic_write_does_not_corrupt(self, tmp_path):
        tp = TaskPack(
            task_pack_id="tp-atomic",
            created_at="2026-01-01T00:00:00Z",
            context_pack=ContextPack(
                context_pack_id="cp-atomic",
                task_input_id="ti-atomic",
                max_context_tokens=100,
            ),
        )
        write_context_pack_artifacts(tp, tmp_path)
        result = write_context_pack_artifacts(tp, tmp_path)
        cp_path = Path(result["context_pack_path"])
        content = json.loads(cp_path.read_text())
        assert content["context_pack_id"] == "cp-atomic"

    def test_latest_write_creates_file(self, tmp_path):
        tp = TaskPack(
            task_pack_id="tp-latest",
            created_at="2026-01-01T00:00:00Z",
            context_pack=ContextPack(
                context_pack_id="cp-latest",
                task_input_id="ti-latest",
                max_context_tokens=100,
            ),
        )
        result = write_latest_context_pack(tp, tmp_path)
        assert Path(result["context_pack_path"]).exists()

    def test_append_history_no_corruption(self, tmp_path):
        tp = TaskPack(
            task_pack_id="tp-hist1",
            created_at="2026-01-01T00:00:00Z",
            context_pack=ContextPack(
                context_pack_id="cp-hist1",
                task_input_id="ti-hist1",
                max_context_tokens=100,
            ),
        )
        append_context_pack_history(tp, tmp_path)
        append_context_pack_history(tp, tmp_path)
        lines = (tmp_path / ".agentx-init" / "context_packs" / "context_pack_history.jsonl").read_text().strip().splitlines()
        assert len(lines) == 2
