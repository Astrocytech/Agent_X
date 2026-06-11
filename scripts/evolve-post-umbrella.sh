#!/usr/bin/env bash
set -euo pipefail
# evolve-post-umbrella.sh — Run governed evolve-agent on post-umbrella example agents
# Generates real provenance (proposal → plan → governance → evidence) through the
# governed patch pipeline instead of relying on static artifact generation.
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="L0/CODE:L1:L2:tools/agentx_initiator:tools/agentx_evolve:tools:examples:${REPO_ROOT}"
EVOLVE="python3 -m agentx_evolve evolve-agent"
log() { echo "[$(date +%H:%M:%S)] $*"; }
ok=0
fail=0

cd "$REPO_ROOT"

evolve_agent() {
  local agent_dir="$1" concept="$2" label="$3"
  log "  --- evolve ($label): $agent_dir ---"
  if $EVOLVE --mock --dry-run --mode plan \
    --agent-dir "$agent_dir" \
    --concept-file "$concept" \
    --json 2>/dev/null; then
    log "  evolve ($label): PASS"
    ok=$((ok + 1))
  else
    log "  evolve ($label): FAIL"
    fail=$((fail + 1))
  fi
}

log "=== Evolve Post-Umbrella Agents ==="

evolve_agent \
  "examples/clothing_advice_agent" \
  "examples/concepts/clothing_docstring.md" \
  "clothing_advice"

evolve_agent \
  "examples/daily_planning_agent" \
  "examples/concepts/daily_priority_validator.md" \
  "daily_planning"

log "=== Evolve: ${ok} passed, ${fail} failed ==="
exit $fail
