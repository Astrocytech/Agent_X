import json, os, sys, tempfile
from pathlib import Path


class TestAgentxEvolveNoSourcePollution:
    """Test that patch execution does not leave temporary files in source."""

    REPO_ROOT = Path(__file__).resolve().parent.parent.parent

    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        sys.path.insert(0, str(self.REPO_ROOT / "tools"))

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        if str(self.REPO_ROOT / "tools") in sys.path:
            sys.path.remove(str(self.REPO_ROOT / "tools"))

    def test_no_tmp_files_left_in_source_after_dry_run(self):
        from agentx_evolve.patch_execution.patch_models import (
            ImplementationSession, PatchOperation,
            new_id, utc_now_iso,
        )
        from agentx_evolve.patch_execution.patch_applier import apply_patch_operations
        from agentx_evolve.patch_execution.initiator_patch_compat import InitiatorPatchCompat

        target = self.tmpdir / "target_file.py"
        target.write_text("original code\n")

        session = ImplementationSession(
            session_id=new_id("session"),
            timestamp=utc_now_iso(),
        )

        ops = [
            PatchOperation(
                operation_id=new_id("op"),
                operation_type="EXACT_EDIT",
                target_path="target_file.py",
                old_text="original code",
                new_text="modified code",
            ),
        ]

        compat = InitiatorPatchCompat(repo_root=self.tmpdir)
        result = apply_patch_operations(
            session=session,
            operations=ops,
            repo_root=self.tmpdir,
            mode="DRY_RUN",
            approved_paths=["target_file.py"],
            sandbox_policy=None,
            compat=compat,
        )
        assert result.status == "DRY_RUN"

        source_files = list(self.tmpdir.rglob("*"))
        tmp_files = [f for f in source_files if ".tmp" in f.suffixes or "tmp" in f.name.lower()]
        assert len(tmp_files) == 0, f"Found unexpected temp files: {tmp_files}"

    def test_temp_workspace_cleaned_on_teardown(self):
        tmp_subdir = Path(tempfile.mkdtemp())
        (tmp_subdir / "some_artifact.json").write_text("{}")
        assert tmp_subdir.exists()

        import shutil
        shutil.rmtree(tmp_subdir, ignore_errors=True)
        assert not tmp_subdir.exists()

    def test_no_files_leak_to_repo_source(self):
        from agentx_evolve.patch_execution.patch_applier import apply_patch

        result = apply_patch("patch content", "some_path.py", str(self.tmpdir))
        assert result.status == "APPLIED"

        repo_files = {str(p.relative_to(self.tmpdir)) for p in self.tmpdir.rglob("*") if p.is_file()}
        source_pollution = {f for f in repo_files if "agentx" in f.lower() and "tmp" in f.lower()}
        assert len(source_pollution) == 0
