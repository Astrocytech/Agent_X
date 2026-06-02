import pytest
from agentx_initiator.core.artifact_io import write_validated_latest


def test_write_validated_latest(tmp_path):
    dest = tmp_path / "latest.json"
    result = write_validated_latest(dest, {"key": "val"}, "repo_scan.schema.json")
    assert result.status == "FAILED"  # schema mismatch expected
    assert not dest.exists()


def test_write_validated_latest_bad_obj(tmp_path):
    dest = tmp_path / "latest.json"
    result = write_validated_latest(dest, {"not": "a scan"}, "repo_scan.schema.json")
    assert result.status == "FAILED"
