from __future__ import annotations

from typing import Any

CORE_INVARIANTS = [
    "no_action_without_validation",
    "no_irreversible_without_rollback",
    "no_promotion_without_evidence",
    "no_self_promotion",
    "no_executor_changes_validator",
    "no_policy_change_same_run",
    "no_l0_modification_default",
    "no_runtime_as_source_promotion",
    "no_failed_test_ignored",
    "no_evidence_overwrite_silent",
    "no_false_file_claim",
]


class MvpInvariantEngine:
    def __init__(self) -> None:
        self._results: list[dict[str, Any]] = []

    def check(self, invariant_name: str, action: Any, context: dict[str, Any]) -> dict[str, Any]:
        result = {"name": invariant_name, "passed": True, "reason": ""}

        if invariant_name == "no_action_without_validation":
            if action and hasattr(action, "status") and action.status == "EXECUTED":
                if context.get("validated") is not True:
                    result["passed"] = False
                    result["reason"] = "Action executed without validation"

        elif invariant_name == "no_self_promotion":
            agent_id = context.get("agent_id", "")
            target_agent = context.get("target_agent", "")
            if agent_id and target_agent and agent_id == target_agent:
                action_type = context.get("action_type", "")
                if action_type in ("review", "promote"):
                    result["passed"] = False
                    result["reason"] = f"Agent {agent_id} attempted self-{action_type}"
                    result["self_promotion_violation"] = True

        elif invariant_name == "no_promotion_without_evidence":
            if context.get("requires_evidence") and not context.get("evidence_refs"):
                result["passed"] = False
                result["reason"] = "Promotion requires evidence references"

        elif invariant_name == "no_false_file_claim":
            claimed_files = context.get("claimed_files", [])
            for f in claimed_files:
                if not isinstance(f, dict) or not f.get("path"):
                    result["passed"] = False
                    result["reason"] = f"Invalid file claim: {f}"

        elif invariant_name == "no_irreversible_without_rollback":
            if action and hasattr(action, "status") and action.status == "EXECUTED":
                if context.get("irreversible") and not context.get("rollback_snapshot_id"):
                    result["passed"] = False
                    result["reason"] = "Irreversible action without rollback snapshot"

        elif invariant_name == "no_executor_changes_validator":
            changed_files = context.get("changed_files", [])
            for f in changed_files:
                if "validator" in f.get("path", "").lower():
                    if f.get("change_type") != "noop":
                        result["passed"] = False
                        result["reason"] = f"Non-noop change to validator file: {f.get('path')}"

        elif invariant_name == "no_policy_change_same_run":
            if context.get("policy_changed") and context.get("same_run"):
                result["passed"] = False
                result["reason"] = "Policy changed within same run"

        elif invariant_name == "no_l0_modification_default":
            claimed = context.get("claimed_files", [])
            for f in claimed:
                if isinstance(f, dict) and f.get("path", "").startswith("l0/"):
                    if not context.get("l0_override"):
                        result["passed"] = False
                        result["reason"] = f"L0 modification without override: {f.get('path')}"

        elif invariant_name == "no_runtime_as_source_promotion":
            if context.get("promotion_mode") == "runtime_to_source":
                result["passed"] = False
                result["reason"] = "Runtime files promoted as source"

        elif invariant_name == "no_failed_test_ignored":
            if context.get("has_failed_tests") and context.get("tests_ignored"):
                result["passed"] = False
                result["reason"] = "Failed tests are being ignored"

        elif invariant_name == "no_evidence_overwrite_silent":
            if context.get("overwrite_attempt") and not context.get("overwrite_approved"):
                result["passed"] = False
                result["reason"] = "Silent evidence overwrite detected"

        self._results.append(result)
        return result

    def check_all(self, action: Any, context: dict[str, Any]) -> list[dict[str, Any]]:
        results = []
        for inv in CORE_INVARIANTS:
            r = self.check(inv, action, context)
            results.append(r)
        return results

    def check_by_names(self, names: list[str], action: Any,
                       context: dict[str, Any]) -> list[dict[str, Any]]:
        results = []
        for name in names:
            if name in CORE_INVARIANTS:
                r = self.check(name, action, context)
                results.append(r)
        return results

    def clear(self) -> None:
        self._results.clear()

    def latest_results(self) -> list[dict[str, Any]]:
        return list(self._results)
