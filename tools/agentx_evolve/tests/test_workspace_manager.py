import tempfile
from pathlib import Path

from agentx_evolve.workspace.workspace_manager import MvpWorkspaceManager


class TestMvpWorkspaceManager:
    def setup_method(self):
        self._tmp = tempfile.mkdtemp(prefix="test_ws_")
        self.ws = MvpWorkspaceManager(root=self._tmp)

    def teardown_method(self):
        self.ws.clean_all()

    def test_create_run_workspace(self):
        path = self.ws.create_run_workspace("run-1")
        assert path.exists()
        assert path.is_dir()

    def test_create_temp_workspace(self):
        path = self.ws.create_temp_workspace("run-1")
        assert path.exists()

    def test_block_path_traversal(self):
        try:
            self.ws.block_path_traversal("/etc/passwd")
            assert False, "Should have raised"
        except PermissionError:
            pass

    def test_block_source_pollution(self):
        self.ws.create_run_workspace("run-1")
        outside = Path(tempfile.mkdtemp())
        try:
            self.ws.block_source_pollution([str(outside)])
        except PermissionError:
            assert False, "Should not block outside paths"
        finally:
            import shutil
            shutil.rmtree(outside, ignore_errors=True)

    def test_block_evidence_overwrite(self):
        ws_path = self.ws.create_run_workspace("run-1")
        f = ws_path / "existing.txt"
        f.write_text("data")
        try:
            self.ws.block_evidence_overwrite(str(f))
            assert False, "Should have raised"
        except PermissionError:
            pass

    def test_clean_temp(self):
        self.ws.create_temp_workspace("run-1")
        self.ws.clean_temp()
        assert self.ws.temp_dir is None or not self.ws.temp_dir.exists()
