# Acceptance Summary — Agent_X Post-Umbrella Phase

## Score: 9/10 (One Critical Gap Remains)

### What Passes (9/10)
| Area | Status | Evidence |
|------|--------|----------|
| evolve_agent.py apply branch | **FIXED** | Now calls `git apply` in apply mode, `applied_patch.diff` written with real content |
| Default mode | **FIXED** | Changed from `plan` to `apply` |
| applied_patch.diff in manifest | **FIXED** | Added to evidence manifest as optional required artifact |
| L0 authorization | **FIXED** | High-risk proposal L0-AUTH-001 + approval created |
| Release tests (quick) | **PASS** | 88/88 pass |
| Release tests (core) | **PASS** | 96/96 pass (security, policy, injection, artifact, orchestrator, tool, sabotage, negative) |
| Structured plan parsing | **PASS** | PlanParser validates JSON schemas correctly, but provider must return valid JSON |
| Provenance records | **UPDATED** | Both agents' records document fixes and remaining limitations |

### Critical Gap (1/10): OpenCode Server Executes Actions Server-Side

The `complete_structured` method on the OpenCode provider sends a message to the OpenCode server. The server interprets the request as a **task to execute**, not a **structured plan to generate**. It:

1. Reads the system prompt and user concept
2. Executes the change (writes files, runs commands, etc.)
3. Returns a human-readable response like "Done. Added docstring..."
4. The provider then fails to parse this as a structured JSON plan

**Impact**: The evolve-agent pipeline cannot produce structured plans from the OpenCode server because the server acts as an autonomous agent, not a plan-only generator. The pipeline exits FAIL before reaching the apply step.

### Verification Commands
```bash
python3 -m pytest tests/quick/ -q           # 88 passed
python3 -m pytest tests/release/test_security_policy_boundary.py tests/release/test_policy_bypass_resistance.py tests/release/test_prompt_injection_negative.py -q  # 20 passed
python3 -m pytest tests/release/test_negative_*.py tests/release/test_no_l0_dependency_violation.py tests/release/test_runtime_artifact_boundary.py -q  # 48 passed
python3 -m pytest tests/release/test_orchestrator_review_promotion_flow.py tests/release/test_tool_mcp_policy_flow.py -q  # 10 passed
python3 -m pytest tests/release/test_patch_execution_flow.py tests/release/test_sabotage_checks.py -q  # 18 passed
```

### Next Step to Reach 10/10
Restructure `OpenCodeProvider.complete_structured()` to run in a **planning-only mode** where the server is instructed to return only a structured plan JSON without executing any file changes. This requires either:
- Adding a planning-only endpoint/mode to the OpenCode server, OR
- Using the mock provider for deterministic plans and reserving the OpenCode server for execution-only mode
