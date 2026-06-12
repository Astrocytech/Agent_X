from __future__ import annotations

import json
import sys
from pathlib import Path
from uuid import uuid4

from agentx_evolve.security.path_boundary_service import policy_for_phase, PHASE_CANARY
from agentx_evolve.security.safe_file_ops import safe_write_file
from agentx_evolve.security.initiator_compat import InitiatorCompat


def write_report(report_name: str, content: str, repo_root: Path) -> None:
    policy = policy_for_phase(PHASE_CANARY, repo_root)
    compat = InitiatorCompat(repo_root=repo_root)
    governance_id = f"canary-gov-{uuid4().hex[:12]}"
    session_id = f"canary-session-{uuid4().hex[:12]}"
    rollback_id = f"canary-rb-{uuid4().hex[:12]}"
    result = safe_write_file(
        path=f"reports/umbrella_agent/{report_name}",
        content=content,
        repo_root=repo_root,
        policy=policy,
        governance_decision_id=governance_id,
        implementation_session_id=session_id,
        rollback_snapshot_id=rollback_id,
        compat=compat,
    )
    if result.status != "SUCCESS":
        print(f"FAIL: write '{report_name}' blocked: {result.errors}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <report_name> <json_content>", file=sys.stderr)
        sys.exit(1)
    write_report(sys.argv[1], sys.argv[2], Path.cwd())
    print(f"Wrote reports/umbrella_agent/{sys.argv[1]}")
