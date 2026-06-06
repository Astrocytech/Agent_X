from __future__ import annotations
import json
import os
import shutil
from pathlib import Path
from agentx_evolve.patch_execution._v1.patch_models import (
    RollbackSnapshot, new_id, sha256_file, utc_now_iso, to_dict,
)
from agentx_evolve.security.security_models import (
    STATUS_SUCCESS, STATUS_FAILED,
)


class RollbackManager:
    def __init__(self, repo_root: Path):
        self._repo_root = repo_root.resolve()
        self._snapshots_dir = (
            self._repo_root / ".agentx-init" / "implementation" / "rollback_snapshots"
        )

    def snapshot_file(self, file_path: str, session_id: str) -> RollbackSnapshot:
        full_path = (self._repo_root / file_path).resolve()
        snapshot_id = new_id("snap")
        snapshot_dir = self._snapshots_dir / session_id
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        snapshot_path = snapshot_dir / f"{snapshot_id}_{file_path.replace('/', '__')}.bak"

        before_hash = ""
        if full_path.exists():
            before_hash = sha256_file(full_path)
            shutil.copy2(str(full_path), str(snapshot_path))
        else:
            snapshot_path.write_text("")

        return RollbackSnapshot(
            snapshot_id=snapshot_id,
            timestamp=utc_now_iso(),
            session_id=session_id,
            file_path=file_path,
            before_hash=before_hash,
            snapshot_path=str(snapshot_path),
        )

    def snapshot_files(
        self, file_paths: list[str], session_id: str,
    ) -> list[RollbackSnapshot]:
        return [self.snapshot_file(p, session_id) for p in file_paths]

    def restore_snapshot(self, snapshot: RollbackSnapshot) -> dict:
        snap_path = Path(snapshot.snapshot_path)
        target_path = (self._repo_root / snapshot.file_path).resolve()

        if not snap_path.exists():
            return {
                "status": "FAILED",
                "error": f"Snapshot file not found: {snapshot.snapshot_path}",
            }

        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if snap_path.stat().st_size == 0:
                if target_path.exists():
                    target_path.unlink()
            else:
                shutil.copy2(str(snap_path), str(target_path))
            snapshot.restored = True
            return {"status": STATUS_SUCCESS, "restored_path": str(target_path)}
        except OSError as e:
            return {"status": STATUS_FAILED, "error": str(e)}

    def restore_all(self, snapshots: list[RollbackSnapshot]) -> list[dict]:
        return [self.restore_snapshot(s) for s in snapshots]

    def cleanup_session(self, session_id: str) -> dict:
        session_snap_dir = self._snapshots_dir / session_id
        if session_snap_dir.exists():
            shutil.rmtree(str(session_snap_dir))
            return {"status": STATUS_SUCCESS, "removed": str(session_snap_dir)}
        return {"status": STATUS_SUCCESS, "removed": None}
