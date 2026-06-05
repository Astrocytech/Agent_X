from __future__ import annotations

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask,
    LLMWorkerModelRequest,
    PatchProposal,
    ValidationHandoff,
    utc_now_iso,
    new_id,
)
from agentx_evolve.workers.llm_implementation_worker.worker_config import (
    WORKER_BLOCKED,
    WORKER_FAILED,
)


def check_worker_task_permission(
    task: LLMWorkerTask,
    policy_context: dict,
) -> dict:
    decision_id = new_id("pd")
    timestamp = utc_now_iso()

    allowed_callers = policy_context.get("allowed_callers", [])
    if allowed_callers and task.caller_role not in allowed_callers:
        return {
            "decision_id": decision_id,
            "timestamp": timestamp,
            "decision": "BLOCK",
            "reason": f"caller_role '{task.caller_role}' not in allowed callers",
            "warnings": [],
            "errors": ["caller not authorized"],
        }

    blocked_modes = policy_context.get("blocked_modes", [])
    if task.worker_mode in blocked_modes:
        return {
            "decision_id": decision_id,
            "timestamp": timestamp,
            "decision": "BLOCK",
            "reason": f"worker_mode '{task.worker_mode}' is blocked",
            "warnings": [],
            "errors": ["mode blocked by policy"],
        }

    allowed_components = policy_context.get("allowed_components", [])
    if allowed_components and task.target_component_id not in allowed_components:
        return {
            "decision_id": decision_id,
            "timestamp": timestamp,
            "decision": "BLOCK",
            "reason": f"component '{task.target_component_id}' not allowed",
            "warnings": [],
            "errors": ["component not authorized"],
        }

    return {
        "decision_id": decision_id,
        "timestamp": timestamp,
        "decision": "ALLOW",
        "reason": "permission granted",
        "warnings": [],
        "errors": [],
    }


def check_model_call_permission(
    model_request: LLMWorkerModelRequest,
    policy_context: dict,
) -> dict:
    decision_id = new_id("pd")
    timestamp = utc_now_iso()

    allowed_model_profiles = policy_context.get("allowed_model_profiles", [])
    if allowed_model_profiles and model_request.model_profile_id not in allowed_model_profiles:
        return {
            "decision_id": decision_id,
            "timestamp": timestamp,
            "decision": "BLOCK",
            "reason": f"model_profile '{model_request.model_profile_id}' not allowed",
            "warnings": [],
            "errors": ["model profile not authorized"],
        }

    allowed_capabilities = policy_context.get("allowed_capabilities", [])
    if allowed_capabilities and model_request.requested_capability not in allowed_capabilities:
        return {
            "decision_id": decision_id,
            "timestamp": timestamp,
            "decision": "BLOCK",
            "reason": f"capability '{model_request.requested_capability}' not allowed",
            "warnings": [],
            "errors": ["capability not authorized"],
        }

    if policy_context.get("block_model_calls", False):
        return {
            "decision_id": decision_id,
            "timestamp": timestamp,
            "decision": "BLOCK",
            "reason": "model calls blocked by policy",
            "warnings": [],
            "errors": ["model calls disabled"],
        }

    return {
        "decision_id": decision_id,
        "timestamp": timestamp,
        "decision": "ALLOW",
        "reason": "model call permitted",
        "warnings": [],
        "errors": [],
    }


def check_patch_proposal_permission(
    patch_proposal: PatchProposal,
    policy_context: dict,
) -> dict:
    decision_id = new_id("pd")
    timestamp = utc_now_iso()

    if policy_context.get("block_patch_proposals", False):
        return {
            "decision_id": decision_id,
            "timestamp": timestamp,
            "decision": "BLOCK",
            "reason": "patch proposals blocked by policy",
            "warnings": [],
            "errors": ["patch proposals disabled"],
        }

    allowed_targets = policy_context.get("allowed_patch_targets", [])
    if allowed_targets:
        for f in patch_proposal.target_files:
            if not any(f.startswith(a) for a in allowed_targets):
                return {
                    "decision_id": decision_id,
                    "timestamp": timestamp,
                    "decision": "BLOCK",
                    "reason": f"target file '{f}' not in allowed targets",
                    "warnings": [],
                    "errors": ["file not authorized"],
                }

    if patch_proposal.requires_governance and not policy_context.get(
        "governance_available", False
    ):
        return {
            "decision_id": decision_id,
            "timestamp": timestamp,
            "decision": "NEEDS_GOVERNANCE",
            "reason": "governance required but not available",
            "warnings": ["governance unavailable"],
            "errors": [],
        }

    return {
        "decision_id": decision_id,
        "timestamp": timestamp,
        "decision": "ALLOW",
        "reason": "patch proposal permitted",
        "warnings": [],
        "errors": [],
    }


def check_validation_handoff_permission(
    handoff: ValidationHandoff,
    policy_context: dict,
) -> dict:
    decision_id = new_id("pd")
    timestamp = utc_now_iso()

    if policy_context.get("block_validation_handoff", False):
        return {
            "decision_id": decision_id,
            "timestamp": timestamp,
            "decision": "BLOCK",
            "reason": "validation handoff blocked by policy",
            "warnings": [],
            "errors": ["validation handoff disabled"],
        }

    allowed_commands = policy_context.get("allowed_validation_commands", [])
    for cmd in handoff.validation_commands:
        if allowed_commands and cmd not in allowed_commands:
            return {
                "decision_id": decision_id,
                "timestamp": timestamp,
                "decision": "BLOCK",
                "reason": f"validation command '{cmd}' not allowlisted",
                "warnings": [],
                "errors": ["command not authorized"],
            }

    return {
        "decision_id": decision_id,
        "timestamp": timestamp,
        "decision": "ALLOW",
        "reason": "validation handoff permitted",
        "warnings": [],
        "errors": [],
    }
