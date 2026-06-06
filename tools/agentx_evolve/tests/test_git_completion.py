import tempfile
from pathlib import Path
from agentx_evolve.git.git_evidence import write_git_completion_record, write_git_evidence_manifest


def test_completion_record_writes_to_temp_path():
    with tempfile.TemporaryDirectory() as tmp:
        record = write_git_completion_record(tmp, status="VALIDATED")
        assert record.status == "VALIDATED"
        assert record.repo_root == tmp
        assert record.record_id.startswith("gcr-")
        assert record.hash


def test_completion_record_has_hash():
    with tempfile.TemporaryDirectory() as tmp:
        record = write_git_completion_record(tmp)
        assert len(record.hash) == 64


def test_completion_record_defaults():
    with tempfile.TemporaryDirectory() as tmp:
        record = write_git_completion_record(tmp)
        assert record.status == "VALIDATED"


def test_evidence_manifest_tracks_files():
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / ".agentx-init" / "git" / "artifacts").mkdir(parents=True, exist_ok=True)
        art = Path(tmp) / ".agentx-init" / "git" / "artifacts" / "test.json"
        art.write_text('{"key": "value"}')
        manifest = write_git_evidence_manifest(tmp, validated_commit="abc123")
        assert manifest.validated_commit == "abc123"
        assert "test" in manifest.artifacts


def test_evidence_manifest_has_hash():
    with tempfile.TemporaryDirectory() as tmp:
        manifest = write_git_evidence_manifest(tmp)
        assert manifest.hash
