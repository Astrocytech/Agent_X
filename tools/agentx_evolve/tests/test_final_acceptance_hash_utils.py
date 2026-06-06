import json
import pytest
from pathlib import Path

from agentx_evolve.final_acceptance.hash_utils import (
    sha256_file, sha256_text, hash_artifacts,
    write_artifact_hashes, validate_acyclic_hash_manifest,
)
from agentx_evolve.final_acceptance.acceptance_models import (
    FinalAcceptanceArtifactHash,
)


class TestSHA256File:
    def test_text_file(self, tmp_path: Path):
        f = tmp_path / "hello.txt"
        f.write_text("hello world")
        h = sha256_file(f)
        assert len(h) == 64
        assert h == sha256_text("hello world")

    def test_binary_file(self, tmp_path: Path):
        f = tmp_path / "data.bin"
        f.write_bytes(b"\x00\x01\x02\xff")
        h = sha256_file(f)
        assert len(h) == 64

    def test_empty_file(self, tmp_path: Path):
        f = tmp_path / "empty.txt"
        f.write_text("")
        h = sha256_file(f)
        assert h == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    def test_large_file(self, tmp_path: Path):
        f = tmp_path / "large.bin"
        f.write_bytes(b"x" * 100000)
        h = sha256_file(f)
        assert len(h) == 64


class TestSHA256Text:
    def test_hello(self):
        h = sha256_text("hello")
        assert h == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"

    def test_empty(self):
        h = sha256_text("")
        assert h == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    def test_unicode(self):
        h = sha256_text("\u00e9\u00e0\u00fc")
        assert len(h) == 64

    def test_newlines(self):
        h1 = sha256_text("line1\nline2")
        h2 = sha256_text("line1\r\nline2")
        assert h1 != h2


class TestHashArtifacts:
    def test_empty_paths(self):
        hashes = hash_artifacts([])
        assert hashes == []

    def test_single_file(self, tmp_path: Path):
        f = tmp_path / "a.txt"
        f.write_text("data")
        hashes = hash_artifacts([f])
        assert len(hashes) == 1
        assert hashes[0].artifact_path == str(f)
        assert len(hashes[0].sha256) == 64

    def test_multiple_files(self, tmp_path: Path):
        a = tmp_path / "a.txt"; a.write_text("aaa")
        b = tmp_path / "b.txt"; b.write_text("bbb")
        hashes = hash_artifacts([a, b])
        assert len(hashes) == 2

    def test_excludes_self_hash(self, tmp_path: Path):
        f = tmp_path / "data.txt"; f.write_text("data")
        self_hash = tmp_path / "hash.json"; self_hash.write_text("{}")
        hashes = hash_artifacts([f, self_hash], exclude_self_hash_file=self_hash)
        assert len(hashes) == 1
        assert hashes[0].artifact_path == str(f)

    def test_duplicate_paths_deduped(self, tmp_path: Path):
        f = tmp_path / "a.txt"; f.write_text("data")
        hashes = hash_artifacts([f, f, str(f)])
        assert len(hashes) == 1

    def test_nonexistent_file_skipped(self, tmp_path: Path):
        hashes = hash_artifacts([tmp_path / "nonexistent.txt"])
        assert hashes == []

    def test_mixed_existing_and_missing(self, tmp_path: Path):
        a = tmp_path / "a.txt"; a.write_text("aaa")
        hashes = hash_artifacts([a, tmp_path / "missing.txt", tmp_path / "also_missing"])
        assert len(hashes) == 1

    def test_string_paths(self, tmp_path: Path):
        f = tmp_path / "a.txt"; f.write_text("data")
        hashes = hash_artifacts([str(f)])
        assert len(hashes) == 1


class TestWriteArtifactHashes:
    def test_writes_file(self, tmp_path: Path):
        hashes = [FinalAcceptanceArtifactHash(artifact_path="/a", sha256="abc")]
        path = write_artifact_hashes(hashes, tmp_path)
        assert path.exists()
        assert path.name == "final_acceptance_artifact_hashes.json"

    def test_content_structure(self, tmp_path: Path):
        hashes = [
            FinalAcceptanceArtifactHash(artifact_path="/a", sha256="abc"),
            FinalAcceptanceArtifactHash(artifact_path="/b", sha256="def"),
        ]
        path = write_artifact_hashes(hashes, tmp_path)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["schema_version"] == "1.0"
        assert data["self_hash_mode"] == "EXCLUDED_FROM_SELF_HASH"
        assert len(data["hashed_artifacts"]) == 2
        assert data["hashed_artifacts"][0]["artifact_path"] == "/a"
        assert len(data["unhashed_artifacts"]) == 1

    def test_custom_self_hash_mode(self, tmp_path: Path):
        hashes = [FinalAcceptanceArtifactHash(artifact_path="/a", sha256="abc")]
        path = write_artifact_hashes(hashes, tmp_path, self_hash_mode="CUSTOM_MODE")
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["self_hash_mode"] == "CUSTOM_MODE"


class TestValidateAcyclicHashManifest:
    def test_nonexistent_returns_error(self, tmp_path: Path):
        errors = validate_acyclic_hash_manifest(tmp_path)
        assert "Hash manifest does not exist" in errors

    def test_valid_manifest(self, tmp_path: Path):
        runtime = tmp_path / ".agentx-init" / "final_acceptance"
        runtime.mkdir(parents=True)
        manifest = {
            "schema_version": "1.0",
            "self_hash_mode": "EXCLUDED_FROM_SELF_HASH",
            "hashed_artifacts": [],
            "unhashed_artifacts": [],
        }
        (runtime / "final_acceptance_artifact_hashes.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        errors = validate_acyclic_hash_manifest(tmp_path)
        assert errors == []

    def test_wrong_self_hash_mode(self, tmp_path: Path):
        runtime = tmp_path / ".agentx-init" / "final_acceptance"
        runtime.mkdir(parents=True)
        manifest = {
            "schema_version": "1.0",
            "self_hash_mode": "INCLUDED",
            "hashed_artifacts": [],
            "unhashed_artifacts": [],
        }
        (runtime / "final_acceptance_artifact_hashes.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        errors = validate_acyclic_hash_manifest(tmp_path)
        assert any("EXCLUDED_FROM_SELF_HASH" in e for e in errors)

    def test_invalid_json_manifest(self, tmp_path: Path):
        runtime = tmp_path / ".agentx-init" / "final_acceptance"
        runtime.mkdir(parents=True)
        (runtime / "final_acceptance_artifact_hashes.json").write_text(
            "not json", encoding="utf-8"
        )
        errors = validate_acyclic_hash_manifest(tmp_path)
        assert any("Cannot read" in e for e in errors)

    def test_report_with_embedded_hash_flagged(self, tmp_path: Path):
        runtime = tmp_path / ".agentx-init" / "final_acceptance"
        runtime.mkdir(parents=True)
        report = {
            "artifact_hashes_sha256": "abc123",
        }
        report_path = runtime / "final_acceptance_report.json"
        report_path.write_text(json.dumps(report), encoding="utf-8")
        manifest = {
            "schema_version": "1.0",
            "self_hash_mode": "EXCLUDED_FROM_SELF_HASH",
            "hashed_artifacts": [
                {"artifact_path": str(report_path.resolve()), "sha256": "xyz"}
            ],
            "unhashed_artifacts": [],
        }
        (runtime / "final_acceptance_artifact_hashes.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        errors = validate_acyclic_hash_manifest(tmp_path)
        assert any("embeds artifact_hashes_sha256" in e for e in errors)
