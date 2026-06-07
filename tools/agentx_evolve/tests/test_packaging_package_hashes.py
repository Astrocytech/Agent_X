import pytest
from pathlib import Path
from agentx_evolve.packaging.package_hashes import hash_file, hash_directory, verify_hash


class TestHashFile:
    def test_hash_file(self, tmp_path: Path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        digest = hash_file(f)
        assert isinstance(digest, str)
        assert len(digest) == 64

    def test_verify_hash(self, tmp_path: Path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        digest = hash_file(f)
        assert verify_hash(f, digest) is True
        assert verify_hash(f, "0" * 64) is False


class TestHashDirectory:
    def test_hash_directory(self, tmp_path: Path):
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.txt").write_text("b")
        result = hash_directory(tmp_path)
        assert "a.txt" in result
        assert "b.txt" in result

    def test_hash_directory_not_a_dir(self, tmp_path: Path):
        f = tmp_path / "file.txt"
        f.write_text("x")
        with pytest.raises(NotADirectoryError):
            hash_directory(f)
