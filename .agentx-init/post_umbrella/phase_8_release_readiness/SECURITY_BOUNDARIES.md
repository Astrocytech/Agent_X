# Security Boundaries

## Protected paths (L0/)
- Core kernel, governance, tool gateway are read-only
- All agent evolution is bounded to examples/ directory

## Policy enforcement
- Every agent has a profile with allowed_tools and forbidden_tools
- seed.emit_answer is the only output tool
- shell.run, filesystem.write, network.request are forbidden

## Safe failure
- All agents return safe_failure=true when data is missing/malformed
- No agent can escalate privileges
- No agent can modify L0/ code
