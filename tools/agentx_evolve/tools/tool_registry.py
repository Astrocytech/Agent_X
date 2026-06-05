from __future__ import annotations

from agentx_evolve.tools.tool_models import (
    ToolDefinition,
    ToolRegistry,
    TRUST_TIER_0_READ_ONLY,
    TRUST_TIER_1_LOCAL_STATE_WRITE,
    TRUST_TIER_2_APPROVED_SOURCE_WRITE,
    TRUST_TIER_3_VALIDATION_EXECUTION,
    TRUST_TIER_4_GIT_WRITE,
    TRUST_TIER_5_NETWORK_OR_EXTERNAL,
    TRUST_TIER_6_BLOCKED,
    ROLE_ORCHESTRATOR,
    ROLE_IMPLEMENTATION_WORKER,
    ROLE_VALIDATION_REPAIR_WORKER,
    ROLE_REVIEWER_ASSISTANT,
    ROLE_PROMOTION_CHECKER,
    ROLE_HUMAN_OPERATOR,
    ROLE_MCP_CLIENT,
    EFFECT_READ,
    EFFECT_WRITE,
    EFFECT_EXECUTE,
    EFFECT_VALIDATE,
    EFFECT_REPORT,
    EFFECT_PLAN,
    EFFECT_PROPOSE,
    EFFECT_ROLLBACK,
    utc_now_iso,
    new_id,
)


def _def(
    tool_name: str,
    description: str,
    owner_component: str,
    trust_tier: str = TRUST_TIER_0_READ_ONLY,
    input_schema_id: str = "tool_call.schema.json",
    output_schema_id: str = "tool_result.schema.json",
    allowed_roles: list[str] | None = None,
    requested_effects: list[str] | None = None,
    requires_sandbox_check: bool = False,
    requires_capability_policy: bool = False,
    requires_governance: bool = False,
    requires_human_approval: bool = False,
    requires_dry_run: bool = False,
    writes_source: bool = False,
    writes_runtime_state: bool = False,
    runs_subprocess: bool = False,
    uses_network: bool = False,
    allowlisted: bool = True,
    enabled: bool = True,
) -> ToolDefinition:
    return ToolDefinition(
        tool_name=tool_name,
        description=description,
        owner_component=owner_component,
        trust_tier=trust_tier,
        input_schema_id=input_schema_id,
        output_schema_id=output_schema_id,
        allowed_roles=allowed_roles or [],
        requested_effects=requested_effects or [EFFECT_READ],
        requires_sandbox_check=requires_sandbox_check,
        requires_capability_policy=requires_capability_policy,
        requires_governance=requires_governance,
        requires_human_approval=requires_human_approval,
        requires_dry_run=requires_dry_run,
        writes_source=writes_source,
        writes_runtime_state=writes_runtime_state,
        runs_subprocess=runs_subprocess,
        uses_network=uses_network,
        allowlisted=allowlisted,
        enabled=enabled,
    )


_INTERNAL_ROLES = [
    ROLE_ORCHESTRATOR,
    ROLE_IMPLEMENTATION_WORKER,
    ROLE_VALIDATION_REPAIR_WORKER,
    ROLE_REVIEWER_ASSISTANT,
    ROLE_PROMOTION_CHECKER,
    ROLE_HUMAN_OPERATOR,
]

_ALL_INTERNAL = _INTERNAL_ROLES + [ROLE_MCP_CLIENT]

_INITIATOR_TOOLS = [
    _def("agentx_scan", "Run Initiator scan", "Initiator",
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_READ, EFFECT_REPORT]),
    _def("agentx_status", "Show Initiator status", "Initiator",
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_READ, EFFECT_REPORT]),
    _def("agentx_plan", "Run Initiator plan", "Initiator",
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_PLAN, EFFECT_REPORT]),
    _def("agentx_propose", "Run Initiator propose", "Initiator",
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_PROPOSE, EFFECT_REPORT]),
    _def("agentx_validate", "Run Initiator validate", "Initiator",
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_VALIDATE, EFFECT_REPORT]),
    _def("agentx_report", "Run Initiator report", "Initiator",
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_REPORT]),
    _def("agentx_graph_build", "Build knowledge graph", "Initiator",
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_WRITE, EFFECT_EXECUTE]),
    _def("agentx_graph_status", "Show graph status", "Initiator",
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_READ, EFFECT_REPORT]),
    _def("agentx_graph_query", "Query knowledge graph", "Initiator",
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_READ, EFFECT_REPORT]),
]

_SECURITY_TOOLS = [
    _def("read_file_guarded", "Read file through sandbox", "SecuritySandbox",
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_READ],
         requires_sandbox_check=True),
    _def("list_files_guarded", "List files through sandbox", "SecuritySandbox",
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_READ],
         requires_sandbox_check=True),
    _def("search_files_guarded", "Search files through sandbox", "SecuritySandbox",
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_READ],
         requires_sandbox_check=True),
    _def("write_file_guarded", "Write file through sandbox (runtime only by default)", "SecuritySandbox",
         trust_tier=TRUST_TIER_1_LOCAL_STATE_WRITE,
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_WRITE],
         requires_sandbox_check=True, requires_capability_policy=True,
         writes_runtime_state=True),
    _def("edit_file_guarded", "Edit file through sandbox (blocked unless policy allows)", "SecuritySandbox",
         trust_tier=TRUST_TIER_2_APPROVED_SOURCE_WRITE,
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_WRITE],
         requires_sandbox_check=True, requires_capability_policy=True,
         writes_source=True),
    _def("patch_precheck_guarded", "Precheck patch target through sandbox", "SecuritySandbox",
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_READ, EFFECT_VALIDATE],
         requires_sandbox_check=True),
    _def("run_allowlisted_command", "Run allowlisted command through sandbox", "SecuritySandbox",
         trust_tier=TRUST_TIER_3_VALIDATION_EXECUTION,
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_EXECUTE],
         requires_sandbox_check=True, requires_capability_policy=True,
         runs_subprocess=True),
]

_PATCH_STUBS = [
    _def("patch_session_status", "Check patch session status (BLOCKED until patch layer)", "GovernedPatchExecution",
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_READ, EFFECT_VALIDATE]),
    _def("patch_apply_guarded", "Apply patch (BLOCKED until patch layer authorizes)", "GovernedPatchExecution",
         trust_tier=TRUST_TIER_6_BLOCKED, enabled=False,
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_WRITE, EFFECT_EXECUTE],
         requires_sandbox_check=True, requires_capability_policy=True,
         writes_source=True),
    _def("rollback_session", "Rollback session (BLOCKED until patch layer authorizes)", "GovernedPatchExecution",
         trust_tier=TRUST_TIER_6_BLOCKED, enabled=False,
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_ROLLBACK],
         requires_sandbox_check=True, requires_capability_policy=True,
         writes_source=True),
]

_GIT_READ_TOOLS = [
    _def("git_status", "Show git status (read-only)", "GitTools",
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_READ],
         runs_subprocess=True),
    _def("git_diff", "Show git diff (read-only)", "GitTools",
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_READ],
         runs_subprocess=True),
    _def("git_diff_name_only", "Show git diff names only (read-only)", "GitTools",
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_READ],
         runs_subprocess=True),
    _def("git_diff_stat", "Show git diff stat (read-only)", "GitTools",
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_READ],
         runs_subprocess=True),
]

_GIT_WRITE_TOOLS = [
    _def("git_create_branch", "Create git branch (BLOCKED in v1)", "GitTools",
         trust_tier=TRUST_TIER_4_GIT_WRITE, enabled=False,
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_WRITE, EFFECT_EXECUTE],
         runs_subprocess=True, requires_capability_policy=True),
    _def("git_stage_approved", "Stage approved changes (BLOCKED in v1)", "GitTools",
         trust_tier=TRUST_TIER_4_GIT_WRITE, enabled=False,
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_WRITE, EFFECT_EXECUTE],
         runs_subprocess=True, requires_capability_policy=True),
    _def("git_commit_approved", "Commit approved changes (BLOCKED in v1)", "GitTools",
         trust_tier=TRUST_TIER_4_GIT_WRITE, enabled=False,
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_WRITE, EFFECT_EXECUTE],
         runs_subprocess=True, requires_capability_policy=True),
    _def("git_push", "Push to remote (BLOCKED in v1)", "GitTools",
         trust_tier=TRUST_TIER_5_NETWORK_OR_EXTERNAL, enabled=False,
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_WRITE, EFFECT_EXECUTE],
         runs_subprocess=True, uses_network=True, requires_capability_policy=True),
]

_HUMAN_STUBS = [
    _def("ask_human", "Request human review (BLOCKED stub)", "HumanReview",
         trust_tier=TRUST_TIER_6_BLOCKED, enabled=False,
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_READ],
         requires_human_approval=True),
]

_INVALID_HANDLER = [
    _def("invalid_tool_handler", "Handle invalid/unknown tool calls", "ToolMCPAdapter",
         allowed_roles=_ALL_INTERNAL, requested_effects=[EFFECT_READ]),
]

_ALL_TOOL_DEFS = (
    _INITIATOR_TOOLS
    + _SECURITY_TOOLS
    + _PATCH_STUBS
    + _GIT_READ_TOOLS
    + _GIT_WRITE_TOOLS
    + _HUMAN_STUBS
    + _INVALID_HANDLER
)


def load_default_tool_registry() -> ToolRegistry:
    reg_id = new_id("reg_")
    return ToolRegistry(
        registry_id=reg_id,
        created_at=utc_now_iso(),
        tools=list(_ALL_TOOL_DEFS),
    )


def register_tool(registry: ToolRegistry, tool_definition: ToolDefinition) -> ToolRegistry:
    for t in registry.tools:
        if t.tool_name == tool_definition.tool_name:
            raise ValueError(f"Duplicate tool name: {tool_definition.tool_name}")
    registry.tools.append(tool_definition)
    return registry


def get_tool_definition(registry: ToolRegistry, tool_name: str) -> ToolDefinition | None:
    for t in registry.tools:
        if t.tool_name == tool_name:
            return t
    return None


def list_enabled_tools(registry: ToolRegistry) -> list[ToolDefinition]:
    return [t for t in registry.tools if t.enabled]


def list_mcp_exposable_tools(registry: ToolRegistry) -> list[ToolDefinition]:
    return [
        t
        for t in registry.tools
        if t.enabled
        and not t.writes_source
        and not t.runs_subprocess
        and not t.uses_network
        and t.trust_tier in (TRUST_TIER_0_READ_ONLY, TRUST_TIER_1_LOCAL_STATE_WRITE)
        and EFFECT_WRITE not in t.requested_effects
        and EFFECT_EXECUTE not in t.requested_effects
    ]
