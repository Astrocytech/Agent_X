from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


class AcceptanceCheck:
    def __init__(self):
        self._results: dict[str, bool] = {}

    def run_all(self) -> dict[str, bool]:
        self._results = {
            "fresh_clone_install": False,
            "initiator_commands": False,
            "patch_execution": False,
            "rollback": False,
            "source_guard": False,
            "llm_worker_output": False,
            "orchestrator_session": False,
            "human_review": False,
            "promotion_gate": False,
            "audit_memory_graph": False,
            "no_l0_mutation": False,
            "no_uncontrolled_shell": False,
            "no_network_default": False,
            "small_model_profile": False,
        }
        return dict(self._results)

    def set_result(self, check: str, passed: bool) -> None:
        self._results[check] = passed

    def get_result(self, check: str) -> bool:
        return self._results.get(check, False)

    def all_passed(self) -> bool:
        if not self._results:
            return False
        return all(self._results.values())

    def summary(self) -> dict:
        total = len(self._results)
        passed = sum(1 for v in self._results.values() if v)
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "all_passed": self.all_passed(),
            "results": dict(self._results),
        }
