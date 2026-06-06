from pathlib import Path
from agentx_evolve.git.git_environment import (
    build_git_environment, build_isolated_home, cleanup_isolated_home,
)


class TestBuildGitEnvironment:
    def test_returns_dict(self):
        env = build_git_environment("/tmp")
        assert isinstance(env, dict)

    def test_suppresses_prompt(self):
        env = build_git_environment("/tmp")
        assert env["GIT_TERMINAL_PROMPT"] == "0"
        assert env["GIT_ASKPASS"] == ""
        assert env["SSH_ASKPASS"] == ""

    def test_sets_pager_to_cat(self):
        env = build_git_environment("/tmp")
        assert env["GIT_PAGER"] == "cat"
        assert env["PAGER"] == "cat"

    def test_disables_system_config(self):
        env = build_git_environment("/tmp")
        assert env["GIT_CONFIG_NOSYSTEM"] == "1"

    def test_sets_isolated_home(self):
        env = build_git_environment("/tmp")
        assert env["HOME"].startswith("/tmp/agentx_git_home_")

    def test_sets_locale(self):
        env = build_git_environment("/tmp")
        assert env["LC_ALL"] == "C"

    def test_sets_xdg_config_home(self):
        env = build_git_environment("/tmp")
        assert "/config" in env["XDG_CONFIG_HOME"]

    def test_disables_external_diff(self):
        env = build_git_environment("/tmp")
        assert env["GIT_EXTERNAL_DIFF"] == ""


class TestBuildIsolatedHome:
    def test_creates_directory(self):
        path = build_isolated_home()
        assert path.exists()
        assert path.is_dir()
        cleanup_isolated_home(path)

    def test_returns_path(self):
        path = build_isolated_home()
        assert isinstance(path, Path)
        cleanup_isolated_home(path)

    def test_prefix_used(self):
        path = build_isolated_home()
        assert "agentx_git_home_" in path.name
        cleanup_isolated_home(path)


class TestCleanupIsolatedHome:
    def test_removes_directory(self):
        path = build_isolated_home()
        assert path.exists()
        cleanup_isolated_home(path)
        assert not path.exists()

    def test_does_not_raise_on_nonexistent(self):
        cleanup_isolated_home(Path("/nonexistent/path"))
        # should not raise

    def test_does_not_raise_on_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        cleanup_isolated_home(f)
        # should not raise
