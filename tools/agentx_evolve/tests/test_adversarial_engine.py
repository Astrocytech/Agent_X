from __future__ import annotations

from agentx_evolve.adversarial.adversarial_engine import (
    MvpAdversarialEngine,
    MvpAttackCase,
    MvpAttackResult,
)
from agentx_evolve.adversarial.default_attack_suite import DEFAULT_ATTACKS


def _dummy_blocked() -> dict:
    return {"blocked": True, "result": "DENIED"}


def _dummy_unblocked() -> dict:
    return {"blocked": False, "result": "ALLOWED"}


class TestAdversarialEngine:
    def setup_method(self):
        self.engine = MvpAdversarialEngine()

    def test_attack_case_creation(self):
        attack = MvpAttackCase(
            attack_id="test_01",
            name="Test Attack",
            description="A test attack case",
            expected_result="DENIED",
            attack_fn=_dummy_blocked,
        )
        assert attack.attack_id == "test_01"
        assert attack.expected_result == "DENIED"

    def test_engine_runs_all_attacks(self):
        self.engine.register_attack(
            MvpAttackCase(attack_id="a1", name="A1", expected_result="DENIED", attack_fn=_dummy_blocked)
        )
        self.engine.register_attack(
            MvpAttackCase(attack_id="a2", name="A2", expected_result="BLOCKED", attack_fn=_dummy_blocked)
        )
        results = self.engine.run_all()
        assert len(results) == 2
        assert all(isinstance(r, MvpAttackResult) for r in results)

    def test_engine_reports_summary(self):
        self.engine.register_attack(
            MvpAttackCase(attack_id="a1", name="A1", expected_result="DENIED", attack_fn=_dummy_blocked)
        )
        self.engine.register_attack(
            MvpAttackCase(attack_id="a2", name="A2", expected_result="BLOCKED", attack_fn=_dummy_unblocked)
        )
        s = self.engine.summary()
        assert s["total"] == 2
        assert s["passed"] == 1
        assert s["failed"] == 1

    def test_default_attacks_exist(self):
        assert len(DEFAULT_ATTACKS) == 4
        ids = [a.attack_id for a in DEFAULT_ATTACKS]
        assert "execute_without_validation" in ids
        assert "promote_without_review" in ids
        assert "fake_evidence" in ids
        assert "self_promote" in ids

    def test_self_promote_attack_blocked(self):
        engine = MvpAdversarialEngine(DEFAULT_ATTACKS)
        result = engine.run_attack("self_promote")
        assert result is not None
        assert result.blocked is True
        assert result.actual_result == "DENIED"
        assert result.passed is True
