from __future__ import annotations

from pathlib import Path

from .policy_models import (
    ALL_ROLES,
    CapabilityEntry,
    CapabilityPolicy,
    DECISION_ALLOW,
    DECISION_BLOCK,
    EFFECT_AUDIT_WRITE,
    EFFECT_EDIT_SOURCE,
    EFFECT_EXECUTE_COMMAND,
    EFFECT_GRAPH_WRITE,
    EFFECT_MEMORY_WRITE,
    EFFECT_PATCH_APPLY,
    EFFECT_PATCH_PRECHECK,
    EFFECT_PROMOTE,
    EFFECT_READ,
    EFFECT_READ_GIT,
    EFFECT_REQUEST_APPROVAL,
    EFFECT_ROLLBACK,
    EFFECT_USE_MODEL,
    EFFECT_USE_NETWORK,
    EFFECT_WRITE_GIT,
    EFFECT_WRITE_RUNTIME,
    EFFECT_WRITE_SOURCE,
    ModelPolicy,
    ModelProfile,
    NON_OVERRIDABLE_BLOCKS,
    ROLE_HUMAN_OPERATOR,
    ROLE_IMPLEMENTATION_WORKER,
    ROLE_MODEL_ADAPTER,
    ROLE_ORCHESTRATOR,
    ROLE_PATCH_EXECUTOR,
    ROLE_PROMOTION_CHECKER,
    ROLE_REVIEWER_ASSISTANT,
    ROLE_TOOL_ADAPTER,
    ROLE_VALIDATION_REPAIR_WORKER,
    RolePermissionMatrix,
    ToolEntry,
    ToolPolicy,
    TRUST_TIER_0_READ_ONLY,
    TRUST_TIER_1_LOCAL_STATE_WRITE,
    TRUST_TIER_2_APPROVED_SOURCE_WRITE,
    TRUST_TIER_3_VALIDATION_EXECUTION,
    TRUST_TIER_4_GIT_WRITE,
    TRUST_TIER_5_NETWORK_OR_EXTERNAL,
    TRUST_TIER_6_BLOCKED,
    new_id,
    utc_now_iso,
)


def load_default_capability_policy(repo_root: Path | None = None) -> CapabilityPolicy:
    now = utc_now_iso()
    return CapabilityPolicy(
        policy_id=new_id("cap-pol"),
        timestamp=now,
        roles=list(ALL_ROLES),
        tools=[
            "agentx_scan",
            "agentx_status",
            "agentx_plan",
            "agentx_report",
            "agentx_graph_query",
            "check_path_boundary",
            "safe_read_file",
            "safe_write_file",
            "safe_exact_edit",
            "safe_patch_precheck",
            "check_subprocess_allowed",
            "check_network_allowed",
            "redact_secrets",
            "patch_apply",
            "patch_rollback",
            "patch_session_status",
            "git_status",
            "git_diff",
            "git_diff_name_only",
            "git_diff_stat",
        ],
        default_decision=DECISION_BLOCK,
        capabilities=[
            CapabilityEntry(
                capability_id=new_id("cap"),
                role=ROLE_ORCHESTRATOR,
                tool_name="agentx_scan",
                allowed_effects=[EFFECT_READ],
            ),
            CapabilityEntry(
                capability_id=new_id("cap"),
                role=ROLE_ORCHESTRATOR,
                tool_name="agentx_status",
                allowed_effects=[EFFECT_READ],
            ),
            CapabilityEntry(
                capability_id=new_id("cap"),
                role=ROLE_ORCHESTRATOR,
                tool_name="agentx_plan",
                allowed_effects=[EFFECT_READ],
            ),
            CapabilityEntry(
                capability_id=new_id("cap"),
                role=ROLE_ORCHESTRATOR,
                tool_name="agentx_report",
                allowed_effects=[EFFECT_READ],
            ),
            CapabilityEntry(
                capability_id=new_id("cap"),
                role=ROLE_ORCHESTRATOR,
                tool_name="agentx_graph_query",
                allowed_effects=[EFFECT_READ],
            ),
            CapabilityEntry(
                capability_id=new_id("cap"),
                role=ROLE_ORCHESTRATOR,
                tool_name="check_path_boundary",
                allowed_effects=[EFFECT_PATCH_PRECHECK],
                requires_sandbox=True,
            ),
            CapabilityEntry(
                capability_id=new_id("cap"),
                role=ROLE_TOOL_ADAPTER,
                tool_name="check_subprocess_allowed",
                allowed_effects=[EFFECT_EXECUTE_COMMAND],
                requires_sandbox=True,
            ),
            CapabilityEntry(
                capability_id=new_id("cap"),
                role=ROLE_PATCH_EXECUTOR,
                tool_name="safe_patch_precheck",
                allowed_effects=[EFFECT_PATCH_PRECHECK],
                requires_sandbox=True,
            ),
            CapabilityEntry(
                capability_id=new_id("cap"),
                role=ROLE_PATCH_EXECUTOR,
                tool_name="patch_apply",
                allowed_effects=[EFFECT_PATCH_APPLY],
                requires_governance=True,
            ),
            CapabilityEntry(
                capability_id=new_id("cap"),
                role=ROLE_MODEL_ADAPTER,
                tool_name="small_local_coder",
                allowed_effects=[EFFECT_USE_MODEL],
            ),
        ],
    )


def load_default_tool_policy(repo_root: Path | None = None) -> ToolPolicy:
    now = utc_now_iso()
    return ToolPolicy(
        policy_id=new_id("tool-pol"),
        timestamp=now,
        tools=[
            # read-only agentx tools
            ToolEntry(
                tool_name="agentx_scan",
                trust_tier=TRUST_TIER_0_READ_ONLY,
                allowlisted=True,
                blocked=False,
                requested_effects=[EFFECT_READ],
            ),
            ToolEntry(
                tool_name="agentx_status",
                trust_tier=TRUST_TIER_0_READ_ONLY,
                allowlisted=True,
                blocked=False,
                requested_effects=[EFFECT_READ],
            ),
            ToolEntry(
                tool_name="agentx_plan",
                trust_tier=TRUST_TIER_0_READ_ONLY,
                allowlisted=True,
                blocked=False,
                requested_effects=[EFFECT_READ],
            ),
            ToolEntry(
                tool_name="agentx_report",
                trust_tier=TRUST_TIER_0_READ_ONLY,
                allowlisted=True,
                blocked=False,
                requested_effects=[EFFECT_READ],
            ),
            ToolEntry(
                tool_name="agentx_graph_query",
                trust_tier=TRUST_TIER_0_READ_ONLY,
                allowlisted=True,
                blocked=False,
                requested_effects=[EFFECT_READ],
            ),
            # sandbox tools
            ToolEntry(
                tool_name="check_path_boundary",
                trust_tier=TRUST_TIER_1_LOCAL_STATE_WRITE,
                allowlisted=True,
                blocked=False,
                requested_effects=[EFFECT_PATCH_PRECHECK, EFFECT_READ],
            ),
            ToolEntry(
                tool_name="safe_read_file",
                trust_tier=TRUST_TIER_0_READ_ONLY,
                allowlisted=True,
                blocked=False,
                requested_effects=[EFFECT_READ],
            ),
            ToolEntry(
                tool_name="safe_write_file",
                trust_tier=TRUST_TIER_2_APPROVED_SOURCE_WRITE,
                requires_governance=True,
                requires_sandbox=True,
                writes_source=True,
                blocked=False,
            ),
            ToolEntry(
                tool_name="safe_exact_edit",
                trust_tier=TRUST_TIER_2_APPROVED_SOURCE_WRITE,
                requires_governance=True,
                requires_sandbox=True,
                writes_source=True,
                blocked=False,
            ),
            ToolEntry(
                tool_name="safe_patch_precheck",
                trust_tier=TRUST_TIER_1_LOCAL_STATE_WRITE,
                requires_sandbox=True,
                blocked=False,
            ),
            ToolEntry(
                tool_name="check_subprocess_allowed",
                trust_tier=TRUST_TIER_1_LOCAL_STATE_WRITE,
                allowlisted=True,
                blocked=False,
                requested_effects=[EFFECT_PATCH_PRECHECK, EFFECT_READ],
            ),
            ToolEntry(
                tool_name="check_network_allowed",
                trust_tier=TRUST_TIER_1_LOCAL_STATE_WRITE,
                allowlisted=True,
                blocked=False,
                requested_effects=[EFFECT_PATCH_PRECHECK, EFFECT_READ],
            ),
            ToolEntry(
                tool_name="redact_secrets",
                trust_tier=TRUST_TIER_1_LOCAL_STATE_WRITE,
                allowlisted=True,
                blocked=False,
                requested_effects=[EFFECT_PATCH_PRECHECK, EFFECT_READ],
            ),
            # patch tools
            ToolEntry(
                tool_name="patch_apply",
                trust_tier=TRUST_TIER_3_VALIDATION_EXECUTION,
                requires_governance=True,
                requires_sandbox=True,
                blocked=True,
            ),
            ToolEntry(
                tool_name="patch_rollback",
                trust_tier=TRUST_TIER_3_VALIDATION_EXECUTION,
                requires_governance=True,
                blocked=True,
            ),
            ToolEntry(
                tool_name="patch_session_status",
                trust_tier=TRUST_TIER_0_READ_ONLY,
                allowlisted=True,
                blocked=False,
                requested_effects=[EFFECT_READ],
            ),
            # git read-only tools
            ToolEntry(
                tool_name="git_status",
                trust_tier=TRUST_TIER_0_READ_ONLY,
                allowlisted=True,
                blocked=False,
                requested_effects=[EFFECT_READ_GIT],
            ),
            ToolEntry(
                tool_name="git_diff",
                trust_tier=TRUST_TIER_0_READ_ONLY,
                allowlisted=True,
                blocked=False,
                requested_effects=[EFFECT_READ_GIT],
            ),
            ToolEntry(
                tool_name="git_diff_name_only",
                trust_tier=TRUST_TIER_0_READ_ONLY,
                allowlisted=True,
                blocked=False,
                requested_effects=[EFFECT_READ_GIT],
            ),
            ToolEntry(
                tool_name="git_diff_stat",
                trust_tier=TRUST_TIER_0_READ_ONLY,
                allowlisted=True,
                blocked=False,
                requested_effects=[EFFECT_READ_GIT],
            ),
        ],
    )


def load_default_model_policy(repo_root: Path | None = None) -> ModelPolicy:
    now = utc_now_iso()
    return ModelPolicy(
        policy_id=new_id("model-pol"),
        timestamp=now,
        model_profiles=[
            ModelProfile(
                model_profile_id="small_local_coder",
                provider_type="LOCAL",
                allowed_task_types=["code_analysis", "code_review", "documentation"],
                blocked_task_types=[],
                may_read_source_context=True,
                may_write_files=False,
                may_execute_tools=False,
                may_execute_commands=False,
                may_use_network=False,
                requires_redaction=True,
                requires_json_output=True,
                max_context_tokens=8192,
                requires_human_approval=False,
            ),
        ],
    )


def load_default_role_permission_matrix(repo_root: Path | None = None) -> RolePermissionMatrix:
    now = utc_now_iso()
    matrix = {}
    for role in ALL_ROLES:
        if role == ROLE_ORCHESTRATOR:
            matrix[role] = {
                EFFECT_READ: DECISION_ALLOW,
                EFFECT_WRITE_RUNTIME: DECISION_ALLOW,
                EFFECT_EXECUTE_COMMAND: DECISION_BLOCK,
            }
        else:
            matrix[role] = {"default": DECISION_BLOCK}
    return RolePermissionMatrix(
        matrix_id=new_id("role-mat"),
        timestamp=now,
        roles=list(ALL_ROLES),
        matrix=matrix,
        non_overridable_blocks=list(NON_OVERRIDABLE_BLOCKS),
    )



