import warnings
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class FileLock:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._lock_path = self.path.with_suffix(self.path.suffix + ".lock")
        self._locked = False

    @contextmanager
    def acquire(self, blocking: bool = True, timeout: float = -1) -> Iterator[bool]:
        if self._locked:
            yield True
            return
        self._lock_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._lock_path.touch(exist_ok=False)
            self._locked = True
            yield True
        except FileExistsError:
            yield False
        finally:
            if self._locked:
                self._lock_path.unlink(missing_ok=True)
                self._locked = False

    def release(self) -> None:
        if self._locked:
            self._lock_path.unlink(missing_ok=True)
            self._locked = False

    def locked(self) -> bool:
        return self._locked or self._lock_path.exists()


warnings.warn(
    "agentx_evolve.monitoring.file_lock is deprecated; "
    "use agentx_evolve.monitoring.monitoring_utils instead",
    DeprecationWarning, stacklevel=2,
)

__all__ = ["FileLock"]
