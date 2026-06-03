import json
from pathlib import Path
from typing import Any
from .policy_models import PolicyAudit, PolicyDecision, PolicyViolation, new_id, utc_now_iso, to_dict
from .initiator_policy_compat import InitiatorPolicyCompat


def append_policy_decision(
    decision: PolicyDecision,
    repo_root: Path,
    compat: InitiatorPolicyCompat | None = None,
) -> dict:
    try:
        path = repo_root / ".agentx-init" / "policies" / "policy_decisions.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        entry = decision.to_dict()
        with open(path, "a") as f:
            f.write(json.dumps(entry) + "\n")
        return {"success": True, "path": str(path)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def append_policy_violation(
    violation: PolicyViolation,
    repo_root: Path,
    compat: InitiatorPolicyCompat | None = None,
) -> dict:
    try:
        path = repo_root / ".agentx-init" / "policies" / "policy_violations.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        entry = violation.to_dict()
        with open(path, "a") as f:
            f.write(json.dumps(entry) + "\n")
        return {"success": True, "path": str(path)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def write_latest_policy_decision(
    decision: PolicyDecision,
    repo_root: Path,
    compat: InitiatorPolicyCompat | None = None,
) -> dict:
    try:
        path = repo_root / ".agentx-init" / "policies" / "latest_policy_decision.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        entry = decision.to_dict()
        with open(tmp, "w") as f:
            json.dump(entry, f, indent=2)
            f.flush()
        tmp.replace(path)
        return {"success": True, "path": str(path)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def build_policy_audit_event(
    decision: PolicyDecision,
    success: bool = True,
) -> PolicyAudit:
    return PolicyAudit(
        audit_id=new_id("audit"),
        timestamp=utc_now_iso(),
        event_type="policy_evaluation",
        decision_id=decision.decision_id,
        caller_role=decision.caller_role,
        tool_name=decision.tool_name,
        requested_effect=decision.requested_effect,
        decision=decision.decision,
        reason=decision.reason,
        success=success,
    )


def write_policy_decision(
    decision: PolicyDecision,
    repo_root: Path,
) -> dict:
    return write_latest_policy_decision(decision, repo_root)



