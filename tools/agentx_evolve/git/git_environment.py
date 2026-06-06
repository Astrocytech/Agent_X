import tempfile
import shutil
from pathlib import Path


def build_git_environment(repo_root: str | Path) -> dict[str, str]:
    tmpdir = build_isolated_home()
    return {
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_ASKPASS": "",
        "SSH_ASKPASS": "",
        "GIT_PAGER": "cat",
        "PAGER": "cat",
        "GIT_EXTERNAL_DIFF": "",
        "GIT_CONFIG_NOSYSTEM": "1",
        "HOME": str(tmpdir),
        "XDG_CONFIG_HOME": str(tmpdir / "config"),
        "LC_ALL": "C",
    }


def build_isolated_home() -> Path:
    return Path(tempfile.mkdtemp(prefix="agentx_git_home_"))


def cleanup_isolated_home(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)
