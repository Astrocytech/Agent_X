import re
from pathlib import Path

import pytest

from agentx_evolve.packaging.artifact_hasher import (
    hash_artifact, write_hash_manifest, verify_artifact_hash, hash_bytes,
)


class TestHashArtifact:
    def test_hash_artifact(self, tmp_path: Path):
        f = tmp_path / "test.txt"
        f.write_text("hello world")
        rec = hash_artifact(f)
        assert len(rec.sha256) == 64
        assert re.match(r"^[a-f0-9]{64}$", rec.sha256)
        assert rec.artifact_path == str(f)
        assert rec.size_bytes == len("hello world")
        assert rec.artifact_kind == "txt"
        assert rec.hash_algorithm == "sha256"

    def test_hash_artifact_tar_kind(self, tmp_path: Path):
        f = tmp_path / "pkg.tar.gz"
        f.write_text("fake tar")
        rec = hash_artifact(f)
        assert rec.artifact_kind == "tar.gz"


class TestHashManifest:
    def test_hash_manifest(self, tmp_path: Path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("content a")
        f2.write_text("content b")
        out = tmp_path / "hash_manifest.json"
        manifest = write_hash_manifest([f1, f2], out)
        assert manifest.hash_manifest_id.startswith("hash_")
        assert len(manifest.artifacts) == 2
        assert manifest.hash_algorithm == "sha256"
        assert out.exists()


class TestVerifyArtifactHash:
    def test_verify_artifact_hash_correct(self, tmp_path: Path):
        f = tmp_path / "data.bin"
        f.write_text("test data")
        rec = hash_artifact(f)
        assert verify_artifact_hash(f, rec.sha256) is True

    def test_verify_artifact_hash_incorrect(self, tmp_path: Path):
        f = tmp_path / "data.bin"
        f.write_text("test data")
        assert verify_artifact_hash(f, "a" * 64) is False


class TestHashBytes:
    def test_hash_bytes(self):
        result = hash_bytes(b"hello")
        assert len(result) == 64
        assert re.match(r"^[a-f0-9]{64}$", result)

    def test_deterministic(self):
        assert hash_bytes(b"test") == hash_bytes(b"test")
