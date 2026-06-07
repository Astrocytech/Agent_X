from pathlib import Path

import pytest

from agentx_evolve.packaging.packaging_models import (
    PackageFileRecord,
    REJECTION_RUNTIME_ARTIFACT,
)
from agentx_evolve.packaging.runtime_exclusion import (
    scan_runtime_artifacts,
    verify_no_runtime_artifacts,
    allowed_paths_only,
)


class TestScanRuntimeArtifacts:
    def test_detects_runtime_artifact_paths(self):
        files = [
            PackageFileRecord(relative_path=".agentx-init/packaging/staging/file.txt", absolute_path="/tmp/f1"),
            PackageFileRecord(relative_path="src/main.py", absolute_path="/tmp/f2"),
            PackageFileRecord(relative_path=".agentx-init/security/decision.json", absolute_path="/tmp/f3"),
        ]
        rejections = scan_runtime_artifacts(files)
        assert len(rejections) == 2
        codes = {r.reason_code for r in rejections}
        assert REJECTION_RUNTIME_ARTIFACT in codes

    def test_clean_files_return_empty(self):
        files = [
            PackageFileRecord(relative_path="src/main.py", absolute_path="/tmp/f1"),
            PackageFileRecord(relative_path="README.md", absolute_path="/tmp/f2"),
        ]
        rejections = scan_runtime_artifacts(files)
        assert rejections == []

    def test_empty_list(self):
        assert scan_runtime_artifacts([]) == []


class TestVerifyNoRuntimeArtifacts:
    def test_clean_returns_true(self):
        files = [
            PackageFileRecord(relative_path="src/main.py", absolute_path="/tmp/f1"),
        ]
        assert verify_no_runtime_artifacts(files) is True

    def test_with_runtime_artifact_returns_false(self):
        files = [
            PackageFileRecord(relative_path=".agentx-init/packaging/raw/data.json", absolute_path="/tmp/f1"),
        ]
        assert verify_no_runtime_artifacts(files) is False


class TestAllowedPathsOnly:
    def test_allows_matching_paths(self):
        files = [
            PackageFileRecord(relative_path="src/main.py", absolute_path="/tmp/f1"),
            PackageFileRecord(relative_path="tools/script.py", absolute_path="/tmp/f2"),
        ]
        rejections = allowed_paths_only(files, ["src", "tools"])
        assert rejections == []

    def test_rejects_non_matching_paths(self):
        files = [
            PackageFileRecord(relative_path="src/main.py", absolute_path="/tmp/f1"),
            PackageFileRecord(relative_path="node_modules/pkg/index.js", absolute_path="/tmp/f2"),
        ]
        rejections = allowed_paths_only(files, ["src"])
        assert len(rejections) == 1
        assert rejections[0].reason_code == REJECTION_RUNTIME_ARTIFACT
