import pytest
import tempfile
from pathlib import Path

from agentx_evolve.docs_sync.doc_controller import (
    run_documentation_sync, run_scan_only, run_plan_only,
)
from agentx_evolve.docs_sync.doc_models import (
    DOC_SYNC_MODE_SCAN_ONLY, DOC_SYNC_MODE_SCAN_PLAN,
    CENTRAL_STATUS_SCANNED, CENTRAL_STATUS_PLAN_CREATED,
)


class TestController:
    def test_controller_scan_only(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "docs").mkdir()
            (root / "docs" / "readme.md").write_text("# Readme")
            result = run_scan_only(root)
            assert result["status"] == CENTRAL_STATUS_SCANNED
            assert result["mode"] == DOC_SYNC_MODE_SCAN_ONLY
            assert result["scan_report_path"] is not None

    def test_controller_scan_plan(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "docs").mkdir()
            (root / "docs" / "readme.md").write_text("# Readme")
            result = run_plan_only(root)
            assert result["status"] == CENTRAL_STATUS_PLAN_CREATED
            assert result["sync_plan_path"] is not None

    def test_controller_scan_plan_writes_expected_artifacts(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "docs").mkdir()
            (root / "docs" / "readme.md").write_text("# Readme")
            run_plan_only(root)
            assert (root / ".agentx-init/docs_sync/documentation_scan_result.json").exists()
            assert (root / ".agentx-init/docs_sync/documentation_sync_plan.json").exists()

    def test_controller_with_include_paths(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            sub = root / "subdir"
            sub.mkdir()
            (sub / "doc.md").write_text("# doc")
            result = run_documentation_sync(
                root,
                mode=DOC_SYNC_MODE_SCAN_ONLY,
                include_paths=["subdir"],
            )
            assert result["status"] == CENTRAL_STATUS_SCANNED

    def test_controller_empty_repo(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = run_scan_only(root)
            assert result["status"] == CENTRAL_STATUS_SCANNED
