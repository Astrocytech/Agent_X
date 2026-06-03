import os
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.promotion.gate_recorder import (
    write_gate_decision, append_gate_decision_history,
    append_blocked_promotion, acquire_promotion_lock,
    release_promotion_lock, LockUnavailableError,
)
from agentx_evolve.promotion.promotion_models import (
    PromotionGateDecision,
)


class TestWriteGateDecisionCreatesFile:
    def test_write_gate_decision_creates_file(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            decision = PromotionGateDecision(
                decision_id="gd-test-001",
                gate_decision_hash="a" * 64,
                idempotency_key="ik-001",
                component_id="comp-1",
                candidate_id="rc-001",
                source_commit="abc123",
            )
            path = write_gate_decision(decision, repo_root)
            assert path.exists()
            data = json.loads(path.read_text())
            assert data["decision_id"] == "gd-test-001"


class TestAppendGateDecisionHistory:
    def test_append_gate_decision_history_appends_to_jsonl(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            decision = PromotionGateDecision(
                decision_id="gd-hist-001",
                gate_decision_hash="a" * 64,
                idempotency_key="ik-001",
                component_id="comp-1",
                candidate_id="rc-001",
                source_commit="abc123",
            )
            path = append_gate_decision_history(decision, repo_root)
            assert path.exists()
            lines = path.read_text().strip().split("\n")
            assert len(lines) == 1
            data = json.loads(lines[0])
            assert data["decision_id"] == "gd-hist-001"


class TestAppendBlockedPromotion:
    def test_append_blocked_promotion_writes_to_jsonl(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            decision = PromotionGateDecision(
                decision_id="gd-blocked-001",
                gate_decision_hash="a" * 64,
                idempotency_key="ik-001",
                component_id="comp-1",
                candidate_id="rc-001",
                source_commit="abc123",
                status="BLOCKED",
                decision="BLOCK",
            )
            path = append_blocked_promotion(decision, repo_root)
            assert path.exists()
            lines = path.read_text().strip().split("\n")
            assert len(lines) == 1


class TestAcquireAndReleaseLock:
    def test_acquire_and_release_lock(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            acquire_promotion_lock(repo_root, timeout_seconds=1)
            release_promotion_lock(repo_root)
            lock_file = repo_root / ".agentx-init" / "promotion" / ".promotion_gate.lock"
            assert not lock_file.exists()


class TestLockUnavailableRaises:
    def test_lock_unavailable_raises(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            acquire_promotion_lock(repo_root, timeout_seconds=1)
            import pytest
            with pytest.raises(LockUnavailableError):
                acquire_promotion_lock(repo_root, timeout_seconds=0)
            release_promotion_lock(repo_root)
