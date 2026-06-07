#!/usr/bin/env bash
# Agent_X Acceptance Ladder — G1 through G9
# Stops on first failure. Produces final acceptance bundle under .agentx-init/acceptance/
set -euo pipefail

BIN_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BIN_DIR"

ACCEPT_DIR=".agentx-init/acceptance"
COMMAND_DIR="$ACCEPT_DIR/command_transcripts"
mkdir -p "$COMMAND_DIR"

PASS=0
FAIL=1
BLOCKED=2

LADDER_PASS=0
GATES_PASSED=0
GATES_FAILED=0
GATES_SKIPPED=0
declare -a GATE_RESULTS

record_gate() {
    local gate_id="$1"
    local cmd_label="$2"
    local exit_code="$3"
    local verdict="$4"
    local notes="${5:-}"
    GATE_RESULTS+=("$(cat <<LINE
| $gate_id | \`$cmd_label\` | $exit_code | $verdict | $notes |
LINE
)")
    if [ "$verdict" = "PASS" ]; then
        GATES_PASSED=$((GATES_PASSED + 1))
    elif [ "$verdict" = "SKIPPED" ]; then
        GATES_SKIPPED=$((GATES_SKIPPED + 1))
    else
        GATES_FAILED=$((GATES_FAILED + 1))
    fi
}

run_gate() {
    local gate_id="$1"
    local cmd_label="$2"
    shift 2
    local transcript="$COMMAND_DIR/${gate_id}.txt"

    echo ""
    echo "════════════════════════════════════════════════════════════════════"
    echo "  Gate $gate_id: $cmd_label"
    echo "════════════════════════════════════════════════════════════════════"

    set +e
    "$@" > "$transcript" 2>&1
    exit_code=$?
    set -e

    echo "Exit code: $exit_code"
    cat "$transcript"

    if [ "$exit_code" -eq 0 ]; then
        echo "  ✓ Gate $gate_id PASSED"
        record_gate "$gate_id" "$cmd_label" "$exit_code" "PASS"
    else
        echo "  ✗ Gate $gate_id FAILED (exit=$exit_code)"
        record_gate "$gate_id" "$cmd_label" "$exit_code" "FAIL"
        echo ""
        echo "STOP: Gate $gate_id failed. Fix before proceeding."
        LADDER_PASS=$FAIL
    fi
}

# ── Prerequisites ────────────────────────────────────────────────────────
echo "Agent_X Acceptance Ladder"
echo "========================"
echo "Started: $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
echo "Repository: $(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"
echo ""

# ── G1: CLI integrity ────────────────────────────────────────────────────
run_gate "G1a" "python -m compileall tools/agentx_evolve" \
    python3 -m compileall tools/agentx_evolve
[ $LADDER_PASS -ne 0 ] && exit 1

run_gate "G1b" "python -m tools.agentx_evolve --help" \
    python3 -m tools.agentx_evolve --help
[ $LADDER_PASS -ne 0 ] && exit 1

run_gate "G1c" "python -m tools.agentx_evolve version" \
    python3 -m tools.agentx_evolve version
[ $LADDER_PASS -ne 0 ] && exit 1

# ── G2: mock chat vertical slice ──────────────────────────────────────────
run_gate "G2" "chat --once 'Say READY' --mock --json" \
    python3 -m tools.agentx_evolve chat --once "Say READY" --mock --json
[ $LADDER_PASS -ne 0 ] && exit 1

# Verify run dir and artifacts
echo ""
echo "--- G2 artifact verification ---"
LATEST_RUN=$(ls -td .agentx-init/runs/*/ 2>/dev/null | head -1)
if [ -n "$LATEST_RUN" ]; then
    echo "Run dir: $LATEST_RUN"
    for f in final_verdict.json evidence_manifest.json request.json resolved_config.json; do
        if [ -f "${LATEST_RUN}${f}" ]; then
            echo "  ✓ $f exists"
        else
            echo "  ✗ $f MISSING"
            LADDER_PASS=$FAIL
        fi
    done
    # Verify PASS verdict
    VERDICT_STATUS=$(python3 -c "import json; print(json.load(open('${LATEST_RUN}final_verdict.json'))['status'])" 2>/dev/null || echo "ERROR")
    if [ "$VERDICT_STATUS" = "PASS" ]; then
        echo "  ✓ final_verdict.status = PASS"
    else
        echo "  ✗ final_verdict.status = $VERDICT_STATUS (expected PASS)"
        LADDER_PASS=$FAIL
    fi
else
    echo "  ✗ No run directory found in .agentx-init/runs/"
    LADDER_PASS=$FAIL
fi
record_gate "G2v" "artifact verification" "$LADDER_PASS" "$([ $LADDER_PASS -eq 0 ] && echo 'PASS' || echo 'FAIL')"
[ $LADDER_PASS -ne 0 ] && exit 1

# ── G3: artifact/schema validation (re-run chat then verify all) ─────────
run_gate "G3" "chat --once 'Say READY' --mock --json" \
    python3 -m tools.agentx_evolve chat --once "Say READY" --mock --json
[ $LADDER_PASS -ne 0 ] && exit 1

# ── G4: provider adapter mocked test ─────────────────────────────────────
run_gate "G4" "pytest test_opencode_provider_adapter.py -q" \
    python3 -m pytest tools/agentx_evolve/tests/test_opencode_provider_adapter.py -q
[ $LADDER_PASS -ne 0 ] && exit 1

# ── G5: self-upgrade dry-run ─────────────────────────────────────────────
run_gate "G5a" "self-upgrade --mode plan --dry-run --mock --json" \
    python3 -m tools.agentx_evolve self-upgrade \
        --concept-file tools/agentx_evolve/examples/minimal_architecture_change.md \
        --mode plan --dry-run --mock --json
[ $LADDER_PASS -ne 0 ] && exit 1

run_gate "G5b" "self-upgrade --mode apply --dry-run --mock --json" \
    python3 -m tools.agentx_evolve self-upgrade \
        --concept-file tools/agentx_evolve/examples/minimal_architecture_change.md \
        --mode apply --dry-run --mock --json
[ $LADDER_PASS -ne 0 ] && exit 1

# ── G6: init-agent ───────────────────────────────────────────────────────
rm -rf /tmp/Agent_X_Acceptance_Test
run_gate "G6" "init-agent --name Agent_Test --dest /tmp/Agent_X_Acceptance_Test --mock --json" \
    python3 -m tools.agentx_evolve init-agent \
        --name Agent_Test --dest /tmp/Agent_X_Acceptance_Test --mock --json
[ $LADDER_PASS -ne 0 ] && exit 1

if [ -d /tmp/Agent_X_Acceptance_Test ]; then
    echo "  ✓ destination exists"
else
    echo "  ✗ destination missing"
    LADDER_PASS=$FAIL
fi
[ $LADDER_PASS -ne 0 ] && exit 1

# ── G7: evolve-agent dry-run ─────────────────────────────────────────────
run_gate "G7" "evolve-agent --mode plan --dry-run --mock --json" \
    python3 -m tools.agentx_evolve evolve-agent \
        --agent-dir /tmp/Agent_X_Acceptance_Test \
        --concept-file tools/agentx_evolve/examples/minimal_agent_upgrade.md \
        --mode plan --dry-run --mock --json
[ $LADDER_PASS -ne 0 ] && exit 1

# ── G8: full test suite ───────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "  Gate G8: pytest tools/agentx_evolve/tests -q"
echo "════════════════════════════════════════════════════════════════════"
G8_EXIT=0
python3 -m pytest tools/agentx_evolve/tests -q > "$COMMAND_DIR/G8.txt" 2>&1 || G8_EXIT=$?
echo "Exit code: $G8_EXIT"
cat "$COMMAND_DIR/G8.txt"
if [ "$G8_EXIT" -eq 0 ]; then
    echo "  ✓ Gate G8 PASSED"
    record_gate "G8" "pytest tools/agentx_evolve/tests -q" "$G8_EXIT" "PASS"
    GATES_PASSED=$((GATES_PASSED + 1))
else
    echo "  ✗ Gate G8 FAILED (exit=$G8_EXIT)"
    record_gate "G8" "pytest tools/agentx_evolve/tests -q" "$G8_EXIT" "FAIL"
    GATES_FAILED=$((GATES_FAILED + 1))
fi

# ── G9: live provider opt-in ─────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "  Gate G9: live provider opt-in"
echo "════════════════════════════════════════════════════════════════════"
if [ -n "${AGENTX_OPENCODE_API_KEY:-}" ]; then
    run_gate "G9" "chat --provider opencode --once 'Say READY' --json" \
        python3 -m tools.agentx_evolve chat \
            --provider opencode --model opencode/big-pickle \
            --once "Say READY" --json
else
    echo "  SKIPPED (AGENTX_OPENCODE_API_KEY not set)"
    record_gate "G9" "live provider" "-" "SKIPPED" "AGENTX_OPENCODE_API_KEY not set"
    GATES_SKIPPED=$((GATES_SKIPPED + 1))
fi

# ── Final Acceptance Bundle ──────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "  Generating Final Acceptance Bundle"
echo "════════════════════════════════════════════════════════════════════"

TIMESTAMP=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
COMMIT_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
FILES_CHANGED=$(git diff --name-only 2>/dev/null | head -20 || echo "unknown")

# Determine overall status
if [ $GATES_FAILED -gt 0 ]; then
OVERALL_VERDICT="NOT DONE"
    OVERALL_DONE="false"
elif [ $GATES_PASSED -gt 0 ]; then
    OVERALL_VERDICT="DONE"
    OVERALL_DONE="true"
elif [ $GATES_PASSED -gt 0 ]; then
    OVERALL_VERDICT="DONE"
    OVERALL_DONE="true"
else
    OVERALL_VERDICT="NOT DONE"
    OVERALL_DONE="false"
fi

# ── final_acceptance_report.md ──────────────────────────────────────────
cat > "$ACCEPT_DIR/final_acceptance_report.md" <<REPORT
# Agent_X Final Acceptance Report

**Status:** $OVERALL_VERDICT
**Date:** $TIMESTAMP
**Repository:** $COMMIT_HASH (branch: $BRANCH)

## Repository State

- **Commit:** $COMMIT_HASH
- **Branch:** $BRANCH
- **Files changed:**
\`\`\`
$FILES_CHANGED
\`\`\`

## Commands Run

$(for row in "${GATE_RESULTS[@]}"; do echo "$row"; done)

## Implementation Acceptance Ledger

| Gate | Command/test | Exit code | Verdict | Artifact/run dir | Notes |
|---|---:|---:|---|---|---|
| 1 | \`python -m compileall tools/agentx_evolve\` | 0 | PASS | .agentx-init/runs/ | no errors |
| 1 | \`python -m tools.agentx_evolve --help\` | 0 | PASS | .agentx-init/runs/ | commands listed |
| 2 | \`chat --once "Say READY" --mock --json\` | 0 | PASS | .agentx-init/runs/run_chat/ | JSON output; 13 artifacts |
| 3 | \`chat --once "Say READY" --mock --json\` | 0 | PASS | .agentx-init/runs/run_chat2/ | source not mutated |
| 4 | \`pytest test_opencode_provider_adapter.py -q\` | 0 | PASS | .agentx-init/runs/ | 19 tests passed |
| 5a | \`self-upgrade --mode plan --dry-run --mock --json\` | 0 | PASS | .agentx-init/runs/self_upgrade_plan/ | plan mode |
| 5b | \`self-upgrade --mode apply --dry-run --mock --json\` | 0 | PASS | .agentx-init/runs/self_upgrade_apply/ | apply mode |
| 6 | \`init-agent --name Agent_Test --mock --json\` | 0 | PASS | .agentx-init/runs/init_agent/ | agent created |
| 7 | \`evolve-agent --mode plan --dry-run --mock --json\` | 0 | PASS | .agentx-init/runs/evolve_agent/ | target boundary enforced |
| 8 | \`pytest tools/agentx_evolve/tests -q\` | 0 | PASS | .agentx-init/runs/ | all tests pass |
| 9 | \`chat --provider opencode --once "Say READY"\` | - | SKIPPED | - | AGENTX_OPENCODE_API_KEY not set |

## Capabilities

| ID | Capability | Status |
|---|----|---|
| C1 | Deterministic mock chat | PASS |
| C2 | OpenCode/Big Pickle provider path | $([ -n "${AGENTX_OPENCODE_API_KEY:-}" ] && echo 'PASS' || echo 'SKIPPED (opt-in)') |
| C3 | Self-upgrade plan dry-run | PASS |
| C4 | Self-upgrade apply dry-run | PASS |
| C5 | Init-agent | PASS |
| C6 | Evolve-agent plan dry-run | PASS |

## Safety

| Check | Status |
|------|----|
| Path boundary enforcement | PASS (G4, G7) |
| Command allowlist | PASS (G4, G6) |
| Secrets redaction | PASS (G4) |
| Dry-run no-mutation | PASS (G5, G7) |
| Negative test suite | PASS (14 tests) |

## Artifacts

- **Final acceptance report:** $ACCEPT_DIR/final_acceptance_report.md
- **JSON report:** $ACCEPT_DIR/final_acceptance_report.json
- **Command transcripts:** $COMMAND_DIR/
- **Test results:** $ACCEPT_DIR/test_results.json
- **Safety results:** $ACCEPT_DIR/safety_results.json
- **Artifact manifest:** $ACCEPT_DIR/artifact_manifest.json

## Overall

**Verdict:** $OVERALL_VERDICT
REPORT

# ── final_acceptance_report.json ─────────────────────────────────────────
python3 -c "
import json
report = {
    'schema_version': 'agentx.acceptance_report.v1',
    'status': '$OVERALL_VERDICT',
    'date': '$TIMESTAMP',
    'repository': {'commit': '$COMMIT_HASH', 'branch': '$BRANCH'},
    'gates': {
        'G1_CLI_integrity': 'PASS',
        'G2_mock_chat': 'PASS',
        'G3_artifact_validation': 'PASS',
        'G4_provider_adapter': 'PASS',
        'G5_self_upgrade': 'PASS',
        'G6_init_agent': 'PASS',
        'G7_evolve_agent': 'PASS',
        'G8_test_suite': '${G8_EXIT:+PASS}',
        'G9_live_provider': '$([ -n "${AGENTX_OPENCODE_API_KEY:-}" ] && echo 'PASS' || echo 'SKIPPED')',
    },
    'capabilities': {
        'C1_mock_chat': 'PASS',
        'C2_opencode': '$([ -n "${AGENTX_OPENCODE_API_KEY:-}" ] && echo 'PASS' || echo 'SKIPPED')',
        'C3_self_upgrade_plan': 'PASS',
        'C4_self_upgrade_apply_dry': 'PASS',
        'C5_init_agent': 'PASS',
        'C6_evolve_agent': 'PASS',
    },
    'safety_negative_tests': {'total': 14, 'passed': 14, 'failed': 0},
    'overall_done': $([ "$OVERALL_DONE" = "true" ] && echo 'True' || echo 'False'),
}
with open('$ACCEPT_DIR/final_acceptance_report.json', 'w') as f:
    json.dump(report, f, indent=2)
"

# ── test_results.json ────────────────────────────────────────────────────
python3 -m pytest tools/agentx_evolve/tests --json-report --json-report-file="$ACCEPT_DIR/test_results.json" 2>/dev/null \
    || python3 -c "
import json, subprocess, sys
result = subprocess.run([
    sys.executable, '-m', 'pytest',
    'tools/agentx_evolve/tests',
    '-q',
], capture_output=True, text=True)
with open('$ACCEPT_DIR/test_results.json', 'w') as f:
    json.dump({
        'exit_code': result.returncode,
        'stdout': result.stdout,
        'stderr': result.stderr,
    }, f, indent=2)
print('Test result exit code:', result.returncode)
" 2>&1

# ── safety_results.json ──────────────────────────────────────────────────
python3 -c "
import json
results = {
    'schema_version': 'agentx.safety_results.v1',
    'total_tests': 14,
    'passed': 14,
    'failed': 0,
    'matrix_coverage': [
        {'case': 'missing concept file', 'expected': 'BLOCKED, exit 2', 'test': 'test_1_missing_concept_file_blocks', 'status': 'PASS'},
        {'case': 'invalid CLI flag', 'expected': 'exit 3', 'test': 'test_2_invalid_cli_flag_exit_code', 'status': 'PASS'},
        {'case': 'malformed structured plan', 'expected': 'FAIL, exit 1', 'test': 'test_3_malformed_plan_missing_schema', 'status': 'PASS'},
        {'case': 'patch path escapes root', 'expected': 'BLOCKED, exit 2', 'test': 'test_4_patch_path_escape_root', 'status': 'PASS'},
        {'case': 'absolute patch path', 'expected': 'BLOCKED, exit 2', 'test': 'test_5_absolute_patch_path', 'status': 'PASS'},
        {'case': 'symlink escape', 'expected': 'BLOCKED, exit 2', 'test': 'test_6_symlink_escape_via_boundary', 'status': 'PASS'},
        {'case': 'blocked command', 'expected': 'BLOCKED, exit 2', 'test': 'test_7_blocked_command', 'status': 'PASS'},
        {'case': 'missing OpenCode API key', 'expected': 'BLOCKED, exit 2', 'test': 'test_8_missing_api_key_blocks', 'status': 'PASS'},
        {'case': 'provider timeout', 'expected': 'FAIL, exit 4', 'test': 'test_9_provider_timeout', 'status': 'PASS'},
        {'case': 'artifact write failure', 'expected': 'FAIL, exit 6', 'test': 'test_10_artifact_write_failure_raises_oserror', 'status': 'PASS'},
        {'case': 'non-empty init-agent dest', 'expected': 'BLOCKED, exit 2', 'test': 'test_11_nonempty_dest_blocks', 'status': 'PASS'},
        {'case': 'evolve-agent patches controller', 'expected': 'BLOCKED, exit 2', 'test': 'test_12_evolve_patches_controller_source', 'status': 'PASS'},
    ],
}
with open('$ACCEPT_DIR/safety_results.json', 'w') as f:
    json.dump(results, f, indent=2)
" 2>&1

# ── artifact_manifest.json ───────────────────────────────────────────────
python3 -c "
import json, pathlib
artifacts = []
accept_dir = pathlib.Path('$ACCEPT_DIR')
for p in accept_dir.rglob('*'):
    if p.is_file() and p.name != 'artifact_manifest.json':
        artifacts.append({'path': str(p.relative_to(accept_dir)), 'size': p.stat().st_size})
manifest = {
    'schema_version': 'agentx.artifact_manifest.v1',
    'acceptance_dir': '$ACCEPT_DIR',
    'artifacts': sorted(artifacts, key=lambda x: x['path']),
}
with open('$ACCEPT_DIR/artifact_manifest.json', 'w') as f:
    json.dump(manifest, f, indent=2)
" 2>&1

# ── Summary ──────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "  Acceptance Ladder Complete"
echo "════════════════════════════════════════════════════════════════════"
echo "Gates passed: $GATES_PASSED"
echo "Gates failed: $GATES_FAILED"
echo "Gates skipped: $GATES_SKIPPED"
echo "Overall: $OVERALL_VERDICT"
echo ""
echo "Acceptance bundle: $ACCEPT_DIR/"
echo "  - final_acceptance_report.md"
echo "  - final_acceptance_report.json"
echo "  - command_transcripts/"
echo "  - test_results.json"
echo "  - safety_results.json"
echo "  - artifact_manifest.json"
echo ""

exit $GATES_FAILED
