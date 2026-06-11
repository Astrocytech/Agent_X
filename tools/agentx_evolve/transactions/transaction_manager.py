from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MvpTransaction:
    transaction_id: str = ""
    run_id: str = ""
    action_id: str = ""
    status: str = "open"
    staged_changes: list[dict] = field(default_factory=list)
    evidence: list[dict] = field(default_factory=list)
    created_at: str = ""
    committed_at: str = ""
    aborted_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "run_id": self.run_id,
            "action_id": self.action_id,
            "status": self.status,
            "staged_changes": list(self.staged_changes),
            "evidence": list(self.evidence),
            "created_at": self.created_at,
            "committed_at": self.committed_at,
            "aborted_at": self.aborted_at,
        }


class MvpTransactionManager:
    def __init__(self) -> None:
        self._active: MvpTransaction | None = None
        self._history: list[MvpTransaction] = []

    @property
    def active(self) -> MvpTransaction | None:
        return self._active

    def begin(self, txn_id: str, run_id: str, action_id: str, created_at: str) -> MvpTransaction:
        if self._active is not None:
            raise RuntimeError(f"Transaction {self._active.transaction_id} already active")
        txn = MvpTransaction(
            transaction_id=txn_id,
            run_id=run_id,
            action_id=action_id,
            status="open",
            created_at=created_at,
        )
        self._active = txn
        return txn

    def stage(self, change: dict) -> None:
        if self._active is None:
            raise RuntimeError("No active transaction")
        self._active.staged_changes.append(change)

    def commit(self, committed_at: str) -> MvpTransaction:
        if self._active is None:
            raise RuntimeError("No active transaction to commit")
        if self._active.status != "open":
            raise RuntimeError(f"Cannot commit transaction with status: {self._active.status}")
        self._active.status = "committed"
        self._active.committed_at = committed_at
        self._active.evidence.append({
            "event": "commit",
            "timestamp": committed_at,
            "staged_count": len(self._active.staged_changes),
        })
        txn = self._active
        self._history.append(txn)
        self._active = None
        return txn

    def abort(self, aborted_at: str, reason: str = "") -> MvpTransaction:
        if self._active is None:
            raise RuntimeError("No active transaction to abort")
        self._active.status = "aborted"
        self._active.aborted_at = aborted_at
        self._active.evidence.append({
            "event": "abort",
            "timestamp": aborted_at,
            "reason": reason,
        })
        txn = self._active
        self._history.append(txn)
        self._active = None
        return txn

    def history_for_run(self, run_id: str) -> list[MvpTransaction]:
        return [t for t in self._history if t.run_id == run_id]
