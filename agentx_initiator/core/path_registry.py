from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def state_dir() -> Path:
    return repo_root() / ".agentx-init"


def config_file() -> Path:
    return state_dir() / "config" / "config.json"


def memory_file(name: str) -> Path:
    return state_dir() / "memory" / name


def report_file(name: str) -> Path:
    return state_dir() / "reports" / name


def snapshot_file(name: str) -> Path:
    return state_dir() / "snapshots" / name


def ensure_state_dirs():
    for d in [
        state_dir() / "config",
        state_dir() / "memory",
        state_dir() / "reports",
        state_dir() / "snapshots",
        state_dir() / "graph",
    ]:
        d.mkdir(parents=True, exist_ok=True)
