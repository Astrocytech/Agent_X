# TODO: Make This Chat L0 / L1 / L2 Compliant

**This chat** = this opencode agent session, with tools bash/read/write/edit/glob/grep/websearch/webfetch/question.
**Goal**: Every session respects L0 kernel governance, follows L1 FIC workflow, stays within L2 proposal-only boundaries.

---

## Current Violations

| Layer | Violation | What this chat did |
|-------|-----------|--------------------|
| L0 | No governance gate | Tools called directly, never through `KernelService.run_turn()` → governance → gateway |
| L0 | No evidence ledger | No `record_evidence()` call for any action |
| L0 | No profile enforcement | No `AgentProfileSchema` was loaded to constrain tool access |
| L0 | Direct shell (`bash`) | L0 forbids shell — tool gateway blocks `shell.run` for all seed profiles |
| L0 | Direct filesystem write | L0 forbids — `filesystem.write` is in `generalist` forbidden list |
| L0 | Direct network (`webfetch`/`websearch`) | L0 forbids — `network.request` is in `generalist` forbidden list |
| L1 | No governing FIC | No FIC contract defined scope, permitted files, or stop conditions |
| L1 | No completion evidence | No `L1/evidence/completion/` record written |
| L1 | No traceability update | `L1/docs/08_L1_TRACEABILITY_MATRIX.md` not updated |
| L1 | No workflow chain | Skipped goal→arch→pseudo→FIC→code→evidence→review |
| L2 | Executed tools in proposal context | L2 is proposal-only — zero tools allowed |

---

## Phase 0: Make This Session Compliant Now (Zero Infra)

These are manual discipline rules. Apply them to this chat immediately. No code needed.

| # | Rule | Why |
|---|------|-----|
| 0.1 | User picks a governing FIC. For this session: `L1/docs/00_L1_SYSTEM_GOAL.md` is the governing document (no code FIC exists yet). Permitted files: `docs/03_runtime_integration/AGENT_GOVERNANCE_ALIGNMENT_TODO.md` only. | L1: no implementation without a governing contract |
| 0.2 | Agent reads the governing doc before any tool call. Done. | L1: specification before execution |
| 0.3 | Agent edits only files in permitted scope. If user asks for edits outside scope, agent says BLOCKED. | L1: bounded implementation |
| 0.4 | Agent does NOT call `bash()` except to run `python3 -c` verification commands specified in a FIC. | L0: no direct shell |
| 0.5 | Agent does NOT call `websearch()`/`webfetch()` unless a FIC authorizes network. | L0: no direct network |
| 0.6 | Agent writes a completion record to `L1/evidence/completion/` at session end. | L1 completion evidence required |
| 0.7 | Agent uses L1 outcome vocabulary: BLOCKED / NO_CHANGE / IMPLEMENTED / VALIDATED / REJECTED / DEFERRED. | L1 §12: lifecycle outcomes |

---

## Phase 1: Build L0 Governance Pipeline

### 1.1 — Create Agent Profile

**File**: `L0/CODE/profiles/builtin/coding_agent.yaml`

The `AgentProfileSchema` dataclass expects specific fields. Missing required fields: `purpose`, `stop_conditions`. Extra unknown fields like `permission_ceiling` or `required_contracts` will be caught by `validate_config()`.

```yaml
id: coding_agent
name: OpenCode Coding Agent
role: coding_agent
purpose: "Governed FIC implementation through L0 kernel gateway"
schema_version: 1

allowed_tools:
  - seed.emit_answer
  - read
  - glob
  - grep
  - write
  - edit
  - bash
  - websearch
  - webfetch
  - question

forbidden_tools:
  - shell.run
  - filesystem.write
  - network.request
  - evolution.promote
  - runtime.mutate

allowed_memory_scopes:
  working:
    - session
    - run

input_schema: fic_unit
output_schema: completion_record
risk_policy: conservative
approval_policy: approval_required_for_high_risk

stop_conditions:
  - missing_governing_fic
  - file_outside_permitted_scope
  - missing_required_context

prompt:
  system: |
    You are the governed Agent_X coding agent. You implement FIC units
    through the L0 kernel gateway. No direct shell, filesystem, or network.
    All tool calls route through governance. Stop with BLOCKED when
    context is missing.
```

**Verify**:
```bash
python3 -c "
from profiles.profile_loader import ProfileLoader
p = ProfileLoader('L0/CODE/profiles/builtin').load('coding_agent')
errs = ProfileLoader('').validate_profile(p)
print('errors:', errs if errs else 'none')
print('id:', p.id, 'tools:', p.allowed_tools)
"
```

### 1.2 — Create General Agent Profile (Unrestricted)

**File**: `L0/CODE/profiles/builtin/general_opencode.yaml`

This profile allows **all** opencode tools with no FIC workflow. Used when the `general` agent is active. The `governed` agent uses the `coding_agent.yaml` profile from 1.1.

```yaml
id: general_opencode
name: General OpenCode Agent
role: general_opencode
purpose: "Unrestricted opencode session through L0 governance gateway"
schema_version: 1

allowed_tools:
  - seed.emit_answer
  - read
  - write
  - edit
  - glob
  - grep
  - bash
  - websearch
  - webfetch
  - question

forbidden_tools:
  - shell.run
  - filesystem.write
  - network.request
  - evolution.promote
  - runtime.mutate

allowed_memory_scopes:
  working:
    - session
    - run

risk_policy: permissive
approval_policy: auto_approve

stop_conditions:
  - goal_achieved
  - max_steps_reached

prompt:
  system: |
    You are the general-purpose Agent_X agent with unrestricted tool access.
    All tool calls route through the L0 governance gateway for evidence logging.
    No FIC workflow is required. Operate normally.
```

**Verify**:
```bash
python3 -c "
from profiles.profile_loader import ProfileLoader
p = ProfileLoader('L0/CODE/profiles/builtin').load('general_opencode')
errs = ProfileLoader('').validate_profile(p)
print('errors:', errs if errs else 'none')
print('id:', p.id, 'tools:', p.allowed_tools)
"
```

### 1.3 — Certify opencode tools as L0 ToolContracts

**File**: `L0/CODE/tool_gateway/opencode_tool_registry.py`

The real `ToolContract` uses `ToolRiskLevel` enum, `SideEffectClass` enum, has required fields `side_effect_class`, `risk_level`, `permission_scope`, `rollback_behavior`, `evidence_required`. The `register()` method on `ToolRegistry` takes `(contract: ToolContract, handler: Callable)`.

```python
"""Certify opencode agent tools as governed ToolContracts."""

from tool_gateway.tool_contracts import ToolContract, ToolRiskLevel, SideEffectClass
from tool_gateway.tool_registry import ToolRegistry


def _handler_not_implemented(**kwargs):
    raise NotImplementedError("Handler runs in opencode process, not in L0 kernel")


def register_opencode_contracts(registry: ToolRegistry) -> None:
    tools = [
        ToolContract(
            name="read",
            description="Read file contents from local filesystem",
            risk_level=ToolRiskLevel.NONE,
            side_effect_class=SideEffectClass.READ_ONLY.value,
            permission_scope="project",
            rollback_behavior="",
            evidence_required=[],
            input_schema={
                "type": "object",
                "properties": {
                    "filePath": {"type": "string"},
                    "offset": {"type": "integer"},
                    "limit": {"type": "integer"},
                },
                "required": ["filePath"],
            },
        ),
        ToolContract(
            name="write",
            description="Write content to a file (overwrites)",
            risk_level=ToolRiskLevel.HIGH,
            side_effect_class=SideEffectClass.LOCAL_FILE_WRITE.value,
            permission_scope="fic_permitted_files",
            rollback_behavior="git_revert",
            evidence_required=["file_path", "content_hash", "diff"],
            input_schema={
                "type": "object",
                "properties": {
                    "filePath": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["filePath", "content"],
            },
        ),
        ToolContract(
            name="edit",
            description="Replace text in an existing file",
            risk_level=ToolRiskLevel.HIGH,
            side_effect_class=SideEffectClass.CODE_PATCH.value,
            permission_scope="fic_permitted_files",
            rollback_behavior="git_revert",
            evidence_required=["file_path", "old_string_hash", "new_string_hash"],
            input_schema={
                "type": "object",
                "properties": {
                    "filePath": {"type": "string"},
                    "oldString": {"type": "string"},
                    "newString": {"type": "string"},
                },
                "required": ["filePath", "oldString", "newString"],
            },
        ),
        ToolContract(
            name="glob",
            description="Find files matching a glob pattern",
            risk_level=ToolRiskLevel.NONE,
            side_effect_class=SideEffectClass.READ_ONLY.value,
            permission_scope="project",
            rollback_behavior="",
            evidence_required=[],
        ),
        ToolContract(
            name="grep",
            description="Search file contents with regex",
            risk_level=ToolRiskLevel.NONE,
            side_effect_class=SideEffectClass.READ_ONLY.value,
            permission_scope="project",
            rollback_behavior="",
            evidence_required=[],
        ),
        ToolContract(
            name="bash",
            description="Execute a shell command",
            risk_level=ToolRiskLevel.CRITICAL,
            side_effect_class=SideEffectClass.SHELL_COMMAND.value,
            permission_scope="fic_approved_commands",
            rollback_behavior="git_revert",
            evidence_required=["command", "exit_code", "stdout_hash"],
            input_schema={
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                    "description": {"type": "string"},
                    "timeout": {"type": "integer"},
                },
                "required": ["command", "description"],
            },
        ),
        ToolContract(
            name="websearch",
            description="Search the web",
            risk_level=ToolRiskLevel.MEDIUM,
            side_effect_class=SideEffectClass.NETWORK_CALL.value,
            permission_scope="fic_authorized_network",
            rollback_behavior="manual_revert",
            evidence_required=["query", "num_results", "timestamp"],
        ),
        ToolContract(
            name="webfetch",
            description="Fetch URL content",
            risk_level=ToolRiskLevel.MEDIUM,
            side_effect_class=SideEffectClass.NETWORK_CALL.value,
            permission_scope="fic_authorized_network",
            rollback_behavior="manual_revert",
            evidence_required=["url", "timestamp"],
        ),
        ToolContract(
            name="question",
            description="Ask the user a question",
            risk_level=ToolRiskLevel.NONE,
            side_effect_class=SideEffectClass.READ_ONLY.value,
            permission_scope="session",
            rollback_behavior="",
            evidence_required=[],
        ),
        ToolContract(
            name="seed.emit_answer",
            description="Emit a governed answer from the seed kernel",
            risk_level=ToolRiskLevel.NONE,
            side_effect_class=SideEffectClass.READ_ONLY.value,
            permission_scope="kernel",
            rollback_behavior="",
            evidence_required=[],
            input_schema={
                "type": "object",
                "properties": {
                    "answer": {"type": "string"},
                },
                "required": ["answer"],
            },
        ),
    ]
    for t in tools:
        # Handlers run in the opencode process, not in the L0 kernel.
        # We register a stub so the contract passes schema checks.
        registry.register(t, _handler_not_implemented)
```

**Verify**:
```bash
python3 -c "
from tool_gateway.tool_registry import ToolRegistry
from tool_gateway.opencode_tool_registry import register_opencode_contracts
r = ToolRegistry()
register_opencode_contracts(r)
print('OK', len(r.list_tools()), 'tools registered')
for t in r.list_tools():
    print(f'  {t.name}: risk={t.risk_level.value} side_effect={t.side_effect_class}')
"
```

### 1.4 — Implement governance decide()

**File**: `L0/CODE/governance/governance_factory.py`

The `ToolGateway.invoke()` calls `self.governance_bus.decide(gov_request)` and checks `decision.allowed`. The `GovernanceRequest` has fields: `action_category`, `action_name`, `profile_id`, `client_id`, `run_id`, `task_id`, `target`, `risk_level`, `effective_policy_id`, `payload`, `metadata`, `action`. `PermissionClass` uses integer position ordering (not `.value`). Use `permission_allows()` for ceiling checks.

```python
"""Governance factory — creates a governance bus from active profile."""

from pathlib import Path
from core_kernel.contracts.governance_contracts import (
    GovernanceRequest,
    GovernanceDecision,
)
from profiles.profile_loader import ProfileLoader
from profiles.agent_profile_schema import AgentProfileSchema
from governance.permission_classes import (
    PermissionClass,
    get_permission_ceiling,
    permission_allows,
)


class ProfileGovernanceBus:
    """Governance bus that checks tool requests against the active profile."""

    def __init__(self, profile: AgentProfileSchema):
        self.profile = profile
        self.ceiling = get_permission_ceiling(profile.id)

    def decide(self, request: GovernanceRequest) -> GovernanceDecision:
        tool_name = request.action_name

        # Check forbidden tools
        if tool_name in self.profile.forbidden_tools:
            return GovernanceDecision(
                allowed=False,
                reason=f"forbidden_platform_tool: {tool_name} is forbidden for profile {self.profile.id}",
            )

        # Check allowed tools (if profile has an allowlist)
        if self.profile.allowed_tools and tool_name not in self.profile.allowed_tools:
            return GovernanceDecision(
                allowed=False,
                reason=f"tool_not_allowed_by_profile: {tool_name} not in {self.profile.id} allowed_tools",
            )

        # Map risk level string to minimum PermissionClass ceiling required.
        # permission_allows(ceiling, required) passes only when ceiling >= required
        # by enum position (P0 < P1 < ... < P9).
        risk_map = {
            "none": PermissionClass.P0_READ_ONLY,
            "low": PermissionClass.P2_WRITE_GENERATED,
            "medium": PermissionClass.P4_MODIFY_NON_PROTECTED_CODE,
            "high": PermissionClass.P5_MODIFY_PROTECTED_CODE,
            "critical": PermissionClass.P7_PUBLIC_API_CHANGE,
        }
        required = risk_map.get(request.risk_level, PermissionClass.P0_READ_ONLY)
        if not permission_allows(self.ceiling, required):
            return GovernanceDecision(
                allowed=False,
                reason=f"risk_policy_denied: risk {request.risk_level} exceeds ceiling {self.ceiling.value}",
            )

        return GovernanceDecision(
            allowed=True,
            reason="",
        )


def create_governance_bus(profile_path: str) -> ProfileGovernanceBus:
    p = Path(profile_path)
    loader = ProfileLoader(str(p.parent))
    profile = loader.load(p.stem)
    return ProfileGovernanceBus(profile)
```

**Also update** `L0/CODE/governance/permission_classes.py`:
Add entries for both new profiles. `general_opencode` needs the highest ceiling (P9) since it permits unrestricted bash/web access. `coding_agent` needs P7 to allow shell commands under FIC governance.

```python
_PROFILE_CEILINGS: dict[str, PermissionClass] = {
    "answer_seed": PermissionClass.P0_READ_ONLY,
    "research_seed": PermissionClass.P0_READ_ONLY,
    "coder_seed": PermissionClass.P3_PROPOSE_PATCH,
    "evaluator_seed": PermissionClass.P0_READ_ONLY,
    "evolution_proposer_seed": PermissionClass.P3_PROPOSE_PATCH,
    "coordinator_seed": PermissionClass.P1_WRITE_SCRATCH,
    "generalist": PermissionClass.P3_PROPOSE_PATCH,
    "general_opencode": PermissionClass.P9_EXTERNAL_SIDE_EFFECT,  # <-- add: unrestricted
    "coding_agent": PermissionClass.P7_PUBLIC_API_CHANGE,         # <-- add: governed FIC
}
```

**Verify**:
```bash
python3 -c "
from profiles.profile_loader import ProfileLoader
from governance.governance_factory import ProfileGovernanceBus
from governance.permission_classes import get_permission_ceiling
from core_kernel.contracts.governance_contracts import GovernanceRequest
p = ProfileLoader('L0/CODE/profiles/builtin').load('coding_agent')
print('ceiling:', get_permission_ceiling(p.id).value)
bus = ProfileGovernanceBus(p)
req = GovernanceRequest(action_name='seed.emit_answer', risk_level='low')
dec = bus.decide(req)
print('seed.emit_answer:', 'allowed' if dec.allowed else 'denied')
req2 = GovernanceRequest(action_name='shell.run', risk_level='critical')
dec2 = bus.decide(req2)
print('shell.run:', 'allowed' if dec2.allowed else 'denied:', dec2.reason)
"
# Expected: ceiling = P7_PUBLIC_API_CHANGE, seed.emit_answer allowed, shell.run denied
```

### 1.7 — Implement layer resolver

**File**: `L0/CODE/bridge/layer_resolver.py`

```python
"""Detect the current governance layer and return the correct profile."""

import os

LAYER_PROFILES = {
    "L2": "L2/profiles/l2_proposal_agent.yaml",
    "L1": "L0/CODE/profiles/builtin/coding_agent.yaml",
    "L0": "L0/CODE/profiles/builtin/generalist.yaml",
}

def detect_layer() -> str:
    env = os.environ.get("AGENT_X_LAYER", "").upper()
    if env in LAYER_PROFILES:
        return env
    cwd = os.getcwd()
    if "/L2/" in cwd:
        return "L2"
    if "/L0/" in cwd and "/L1/" not in cwd:
        return "L0"
    return "L1"

def resolve_profile_path() -> str:
    return LAYER_PROFILES[detect_layer()]
```

### 1.5 — Build the governance bridge

**File**: `L0/CODE/bridge/opencode_tool_bridge.py`

Depends on 1.7 (layer_resolver) and 1.1+1.2 (both profiles). The bridge selects a profile in two phases:
1. **Layer override** — if `AGENT_X_LAYER=L2` or `L0`, that layer's profile takes priority (from the `LAYER_PROFILES` dict).
2. **Agent-based fallback** — for L1 (default), the profile comes from `agent_name`.

| Layer | Profile | Effect |
|-------|---------|--------|
| L2 | `l2_proposal_agent.yaml` | Zero tools allowed |
| L0 | `generalist.yaml` | Only `seed.emit_answer` |
| L1 (general agent) | `general_opencode.yaml` | Unrestricted |
| L1 (governed agent) | `coding_agent.yaml` | FIC workflow |

The bridge is a **governance check + evidence logger** only. It does NOT execute tools — the TypeScript wrapper handles execution.

```python
#!/usr/bin/env python3
"""Governance check + evidence logging for opencode tool calls.

Profile selection: layer (L0/L2) > agent_name (general/governed).
Input:  {"tool_name": "...", "agent_name": "general|governed", ...}
Output: {"governance_allowed": bool, "reason": "", "trace_id": "..."}
"""
import json, sys, hashlib, uuid
from pathlib import Path
from datetime import datetime, timezone

from profiles.profile_loader import ProfileLoader
from core_kernel.evidence.evidence_ledger import record_evidence
from layer_resolver import detect_layer

AGENT_PROFILES = {
    "governed": "L0/CODE/profiles/builtin/coding_agent.yaml",
    "general": "L0/CODE/profiles/builtin/general_opencode.yaml",
}


def resolve_profile(agent_name: str) -> str:
    # Layer detection overrides: L2 blocks all tools, L0 restricts to seed.emit_answer
    layer = detect_layer()
    if layer == "L2":
        return "L2/profiles/l2_proposal_agent.yaml"
    if layer == "L0":
        return "L0/CODE/profiles/builtin/generalist.yaml"
    # L1 — select profile based on agent identity
    return AGENT_PROFILES.get(agent_name, AGENT_PROFILES["general"])


def main():
    req = json.loads(sys.stdin.read())
    tool_name = req.get("tool_name", "")
    arguments = req.get("arguments", {})
    agent_name = req.get("agent_name", "general")
    session_id = req.get("session_id", str(uuid.uuid4())[:8])

    # 1. Select and load profile (layer detection + agent name)
    profile_path = resolve_profile(agent_name)
    p = Path(profile_path)
    loader = ProfileLoader(str(p.parent))
    profile = loader.load(p.stem)

    # 2. Governance check — allowed_tools / forbidden_tools
    allowed = True
    reason = ""
    if tool_name in profile.forbidden_tools:
        allowed = False
        reason = f"tool '{tool_name}' is in profile.forbidden_tools"
    elif profile.allowed_tools and tool_name not in profile.allowed_tools:
        allowed = False
        reason = f"tool '{tool_name}' not in profile.allowed_tools"

    trace_id = hashlib.sha256(
        (tool_name + str(datetime.now(timezone.utc))).encode()
    ).hexdigest()[:12]

    # 3. Record evidence
    record_evidence({
        "tool_name": tool_name,
        "trace_id": trace_id,
        "profile_id": profile.id,
        "agent_name": agent_name,
        "session_id": session_id,
        "allowed": allowed,
        "reason": reason,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    # 4. Return governance decision
    sys.stdout.write(json.dumps({
        "governance_allowed": allowed,
        "reason": reason,
        "trace_id": trace_id,
        "profile_id": profile.id,
    }))


if __name__ == "__main__":
    main()
```

**Verify**:
```bash
# Test 1: general agent allows seed.emit_answer
echo '{"tool_name":"seed.emit_answer","arguments":{"answer":"test"}}' | python3 L0/CODE/bridge/opencode_tool_bridge.py
# Returns {"governance_allowed": true, "profile_id": "general_opencode", ...}

# Test 2: shell.run forbidden by general agent profile
echo '{"tool_name":"shell.run","arguments":{}}' | python3 L0/CODE/bridge/opencode_tool_bridge.py
# Returns {"governance_allowed": false, "reason": "tool 'shell.run' is in profile.forbidden_tools", "profile_id": "general_opencode", ...}

# Test 3: governed agent auto-selects coding_agent.yaml (different profile_id!)
echo '{"tool_name":"seed.emit_answer","arguments":{"answer":"test"},"agent_name":"governed"}' | python3 L0/CODE/bridge/opencode_tool_bridge.py
# Returns {"governance_allowed": true, "profile_id": "coding_agent", ...}
```

### 1.8 — Create L2 proposal profile

**File**: `L2/profiles/l2_proposal_agent.yaml`

```yaml
id: l2_proposal_agent
name: L2 Proposal Agent
role: specification_author
purpose: "Propose profiles, blueprints, and specs at L2. Zero tool execution."
schema_version: 1

allowed_tools: []

forbidden_tools:
  - seed.emit_answer
  - read
  - glob
  - grep
  - write
  - edit
  - bash
  - websearch
  - webfetch
  - question

stop_conditions:
  - implementation_requested_in_l2_context

risk_policy: conservative
approval_policy: approval_required_for_all

prompt:
  system: |
    You are an L2 specification agent. You may only produce text proposals.
    Tool execution is denied. Route implementation requests to L1 via handoff.
```

---

## Phase 2: Configuration

### 2.1 — Create AGENTS_GENERAL.md (Unrestricted Agent)

**File**: `AGENTS_GENERAL.md` (project root)

Used when the `general` agent is active. Minimal rules — the agent uses `l0_gateway` for all tool calls but has no FIC workflow.

```markdown
# Agent_X — General Agent Instructions

## Tool Access
Built-in tools (bash, write, read, edit, glob, grep, webfetch, websearch)
are DISABLED in opencode.json. Use the `l0_gateway` custom tool for ALL operations.
The builtin `question` tool remains available for interactive user prompts.

Call `l0_gateway` with `tool_name` (the tool you want) and `arguments` (the args):

    l0_gateway(tool_name="bash", arguments={command: "ls"})
    l0_gateway(tool_name="read", arguments={filePath: "src/main.py"})
    l0_gateway(tool_name="write", arguments={filePath: "x.txt", content: "hello"})
    l0_gateway(tool_name="edit", arguments={filePath: "x.py", oldString: "foo", newString: "bar"})
    l0_gateway(tool_name="glob", arguments={pattern: "**/*.py"})
    l0_gateway(tool_name="grep", arguments={pattern: "def main", path: "src/"})
    l0_gateway(tool_name="websearch", arguments={query: "python tutorial"})
    l0_gateway(tool_name="webfetch", arguments={url: "https://example.com"})

## FIC Governance Mode
**Not active in general mode.** If the user requests governed FIC-style work,
switch to the `governed` agent by telling them to restart with the governed agent.

## L0 / L2 Layer Enforcement
When `AGENT_X_LAYER=L0` or `AGENT_X_LAYER=L2` is set, the bridge automatically
selects the correct profile. No manual action needed.
```

### 2.2 — Create AGENTS_GOVERNED.md (FIC-Compliant Agent)

**File**: `AGENTS_GOVERNED.md` (project root)

Used when the `governed` agent is active. Enforces L1 FIC workflow, L2 proposal-only rules.

```markdown
# Agent_X — Governed Agent (FIC-Compliant)

## Tool Access
Built-in tools (bash, write, read, edit, glob, grep, webfetch, websearch)
are DISABLED. Use `l0_gateway` for all operations. The builtin `question`
tool remains available. The bridge automatically loads the strict
`coding_agent.yaml` profile.

## L1 Mode (default) — FIC-Governed Implementation

### Mandatory workflow
1. User MUST specify a governing FIC contract path at session start.
2. Read the FIC before any tool call. Identify: permitted files, required outcome, evidence expectations.
3. Implement only what the FIC authorizes. Edit only files in the FIC's permitted scope.
4. Do not modify L0 files unless the FIC explicitly authorizes it.
5. If required context is missing: stop with BLOCKED. Do not guess or proceed.
6. No speculative features, no unrelated refactors, no extra abstractions.

### After implementation
7. Collect completion evidence (diffs, test output, proof results).
8. Write completion record to `L1/evidence/completion/{fic_id}_{timestamp}.yaml`.
9. Update traceability matrix at `L1/docs/08_L1_TRACEABILITY_MATRIX.md`.

### Outcome vocabulary
- BLOCKED     → missing context/authority — cannot proceed
- NO_CHANGE   → existing code already satisfies FIC
- IMPLEMENTED → code written, validation pending
- VALIDATED   → all required checks pass
- REJECTED    → failed review or governance check
- DEFERRED    → intentionally postponed

## L2 Mode — Proposal Only, Zero Execution
When `AGENT_X_LAYER=L2` or cwd contains `/L2/`:
- Do NOT call any tool that reads, writes, or executes on the filesystem.
- You may produce markdown, YAML, or text proposals only.
- If the user asks for code or file changes, respond:
  "This is an L2 session. I can propose a spec. Implementation requires an L1 FIC handoff."
- Route implementation requests via L2_BuildL1HandoffProposal.eqc.md

## L0 Mode — Seed Kernel Only
When `AGENT_X_LAYER=L0`:
- Only `seed.emit_answer` is permitted.
- No file tool execution allowed.
```

### 2.3 — Create the custom tool definition

**File**: `.opencode/tools/l0_gateway.ts`

The bridge **auto-selects the profile** based on `context.agent`:
- `general` agent → `general_opencode.yaml` (unrestricted)
- `governed` agent → `coding_agent.yaml` (FIC workflow)

```typescript
import { tool } from "@opencode-ai/plugin"
import path from "path"

export default tool({
  description: "Governed entry point for all tool calls. Auto-selects profile from agent identity.",
  args: {
    tool_name: tool.schema.string().describe("Name of the tool to execute (read, write, bash, etc.)"),
    arguments: tool.schema.any().describe("Arguments to pass to the tool"),
  },
  async execute(args, context) {
    // 1. Check governance via Python bridge (sends agent_name for profile selection)
    const script = path.join(context.worktree, "L0/CODE/bridge/opencode_tool_bridge.py")
    const input = JSON.stringify({
      tool_name: args.tool_name,
      arguments: args.arguments || {},
      agent_name: context.agent || "general",
      session_id: context.sessionID,
    })
    const proc = Bun.spawn(["python3", script], {
      stdin: "pipe",
      stdout: "pipe",
      stderr: "pipe",
    })
    proc.stdin.write(input)
    proc.stdin.end()
    const stdout = await new Response(proc.stdout).text()
    const stderr = await new Response(proc.stderr).text()
    const exitCode = await proc.exited
    if (exitCode !== 0) {
      return `Bridge error (exit ${exitCode}): ${stderr}`
    }
    const governance = JSON.parse(stdout)
    if (!governance.governance_allowed) {
      return `BLOCKED by governance: ${governance.reason}`
    }

    // 2. Execute the actual tool (governance approved)
    switch (args.tool_name) {
      case "bash": {
        const result = await Bun.$`bash -c ${args.arguments.command}`.text()
        return result.trim()
      }
      case "read": {
        const file = Bun.file(args.arguments.filePath)
        const content = await file.text()
        const lines = content.split("\n")
        const offset = args.arguments.offset || 0
        const limit = args.arguments.limit || lines.length
        return lines.slice(offset, offset + limit).join("\n")
      }
      case "write": {
        await Bun.write(args.arguments.filePath, args.arguments.content)
        return `Written ${args.arguments.content.length} bytes`
      }
      case "edit": {
        const oldContent = await Bun.file(args.arguments.filePath).text()
        const newContent = oldContent.replace(
          args.arguments.oldString,
          args.arguments.newString
        )
        await Bun.write(args.arguments.filePath, newContent)
        return `Edit applied: replaced "${args.arguments.oldString.substring(0, 40)}..."`
      }
      case "glob": {
        const result = await Bun.$`python3 -c "import glob, sys; [print(x) for x in sorted(glob.glob(sys.argv[1], recursive=True))]" ${args.arguments.pattern}`.text()
        return result.trim()
      }
      case "grep": {
        const result = await Bun.$`rg ${args.arguments.pattern} ${args.arguments.path || "."}`.text()
        return result.trim()
      }
      case "websearch": {
        const resp = await fetch(
          `https://html.duckduckgo.com/html/?q=${encodeURIComponent(args.arguments.query)}`
        )
        return await resp.text()
      }
      case "webfetch": {
        const resp = await fetch(args.arguments.url)
        return await resp.text()
      }
      default:
        return `Unknown tool: ${args.tool_name}`
    }
  },
})
```

### 2.4 — Configure opencode

**File**: `opencode.json` (project root)

Disable all built-in tools and register two agents: `general` (default) and `governed`. Both agents use the same `l0_gateway` custom tool — the bridge selects the profile automatically based on `context.agent`.

**Important**: Only apply this after Phase 1 is complete. If the bridge doesn't exist, every tool call will fail.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "name": "Agent_X",
  "agent": {
    "general": {
      "description": "General-purpose unrestricted agent for everyday development",
      "mode": "primary",
      "prompt": "{file:./AGENTS_GENERAL.md}"
    },
    "governed": {
      "description": "FIC-governed agent for L0/L1/L2 compliant sessions",
      "mode": "primary",
      "prompt": "{file:./AGENTS_GOVERNED.md}"
    }
  },
  "tools": {
    "bash": false,
    "write": false,
    "read": false,
    "edit": false,
    "glob": false,
    "grep": false,
    "webfetch": false,
    "websearch": false
  },
  "permission": {
    "default": "allow"
  }
}
```

---

## Phase 3: Evidence Pipeline

### 3.1 — Implement FIC-L1-009 (evidence_collector)

**File**: `L1/CODE/evidence_collector.py`
**Action**: Implement per `L1/fic/units/FIC-L1-009-evidence-collector.md`. Must collect sha256 hashes of changed files, test output, proof output. Write structured records to `L1/evidence/{session_id}/`.

### 3.2 — Implement FIC-L1-010 (completion_record_writer)

**File**: `L1/CODE/completion_record_writer.py`
**Action**: Implement per `L1/fic/units/FIC-L1-010-completion-record-writer.md`. Must produce YAML at `L1/evidence/completion/{fic_id}_{timestamp}.yaml`:
```yaml
fic_id: "FIC-L1-XXX"
outcome: "IMPLEMENTED"
files_changed: ["path/to/file.py"]
evidence_hashes: {"file.py": "sha256:abc123"}
validation_status: "passed"
timestamp: "2026-06-08T12:00:00Z"
```

### 3.3 — Implement FIC-L1-011 (traceability_updater)

**File**: `L1/CODE/traceability_updater.py`
**Action**: Implement per `L1/fic/units/FIC-L1-011-traceability-updater.md`. Append row to `L1/docs/08_L1_TRACEABILITY_MATRIX.md`.

### 3.4 — Implement FIC-L1-007 (handoff_packet_builder)

**File**: `L1/CODE/handoff_packet_builder.py`
**Action**: Implement per `L1/fic/units/FIC-L1-007-handoff-packet-builder.md`. Produce `{fic_ref, permitted_files, expected_evidence, scope_rules}`.

---

## Acceptance Criteria

| Layer | Check | How to verify |
|-------|-------|---------------|
| L0 | Tools route through governance | Every tool call produces a `record_evidence()` entry in `.local/runtime/evidence/evidence_ledger.jsonl` |
| L0 | Forbidden tools blocked | Call to `l0_gateway(tool_name="shell.run")` returns `governance_allowed: false` |
| L0 | Profile loaded | `ProfileLoader(path).load('coding_agent')` succeeds, stop_conditions non-empty |
| Agent | General agent unrestricted | Running as `general` agent, `l0_gateway(tool_name="bash")` returns `governance_allowed: true` |
| Agent | Governed agent strict | Running as `governed` agent, the FIC workflow rules are enforced in AGENTS_GOVERNED.md |
| Agent | Profile auto-selects | Bridge returns different `profile_id` for `agent_name="general"` vs `agent_name="governed"` |
| L1 | FIC read at session start | Governed agent's first action is reading the FIC file |
| L1 | Completion record written | File exists at `L1/evidence/completion/` |
| L1 | Traceability updated | `L1/docs/08_L1_TRACEABILITY_MATRIX.md` has new row |
| L2 | Zero tools in L2 mode | `ProfileGovernanceBus.decide()` returns `allowed=False` for any tool call |
| L2 | Proposal-only output | Agent produces markdown, not file edits |

---

## Build Order

```
1.1 (coding_agent.yaml)         — standalone, 2 min
1.2 (general_opencode.yaml)     — standalone, 2 min
──────────────────────────────────────────
1.3 (tool contracts)            — standalone, 5 min
1.4 (governance bus)            — depends on 1.1 + 1.2, 10 min
1.7 (layer resolver)            — standalone, 2 min
──────────────────────────────────────────
1.5 (bridge)                    — depends on 1.7 (layer_resolver) + 1.1 + 1.2, 5 min
2.1 (AGENTS_GENERAL.md)         — standalone, 3 min
2.2 (AGENTS_GOVERNED.md)        — depends on 1.1 (FIC workflow reference), 5 min
2.3 (l0_gateway.ts)             — depends on 1.5, 5 min
2.4 (opencode.json)             — depends on 2.1 + 2.2 + 2.3, 2 min
──────────────────────────────────────────
3.1 (evidence_collector)        — depends on 1.5, implement FIC-L1-009
3.2 (completion_recorder)       — depends on 3.1, implement FIC-L1-010
3.3 (traceability_updater)      — depends on 3.2, implement FIC-L1-011
3.4 (handoff_builder)           — depends on 1.1, implement FIC-L1-007
1.8 (L2 profile)                — standalone, 2 min
```

**Start now**: Apply Phase 0 rules to this session. Then build in the order above.
