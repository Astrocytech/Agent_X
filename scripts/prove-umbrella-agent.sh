#!/usr/bin/env bash
set -euo pipefail
# prove-umbrella-agent.sh — Full umbrella agent real self-evolution milestone proof.
# Delegates to sub-scripts for each phase. See Makefile prove-umbrella-agent target.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPORT_DIR="$REPO_ROOT/reports/umbrella_agent"

log() { echo "[$(date +%H:%M:%S)] $*"; }

log "=== Umbrella Agent Real Self-Evolution Milestone Proof ==="
log "Repo root: $REPO_ROOT"
log "Report dir: $REPORT_DIR"
echo ""

# Stage A: Pipeline infrastructure proof
log "--- Stage A: Pipeline Infrastructure ---"

log "Phase A1: Baseline snapshots (pass_0..pass_3)"
test -f "$REPORT_DIR/pass_0_repository_reality_snapshot.json" && log "  pass_0: OK" || { log "  pass_0: MISSING"; exit 1; }
test -f "$REPORT_DIR/pass_1_requirement_traceability_matrix.json" && log "  pass_1: OK" || { log "  pass_1: MISSING"; exit 1; }
test -f "$REPORT_DIR/pass_2_umbrella_agent_contract.md" && log "  pass_2: OK" || { log "  pass_2: MISSING"; exit 1; }
test -f "$REPORT_DIR/pass_3_recommendation_rules.md" && log "  pass_3: OK" || { log "  pass_3: MISSING"; exit 1; }
test -f "$REPORT_DIR/source_hash_manifest_before.json" && log "  hash_manifest: OK" || { log "  hash_manifest: MISSING"; exit 1; }
test -f "$REPORT_DIR/file_origin_classification.json" && log "  origin_classification: OK" || { log "  origin_classification: MISSING"; exit 1; }

log "Phase A2: Schema files"
test -f "$REPO_ROOT/schemas/umbrella_agent_input.schema.json" && log "  input schema: OK" || { log "  input schema: MISSING"; exit 1; }
test -f "$REPO_ROOT/schemas/umbrella_weather_fixture.schema.json" && log "  weather fixture schema: OK" || { log "  weather fixture schema: MISSING"; exit 1; }
test -f "$REPO_ROOT/schemas/umbrella_agent_output.schema.json" && log "  output schema: OK" || { log "  output schema: MISSING"; exit 1; }

log "Phase A3: Policy registry (weather.fixture.read)"
PYTHONPATH="$REPO_ROOT/tools/agentx_evolve:$REPO_ROOT/tools" python3 << 'PYEOF' 2>&1 | tail -1
from agentx_evolve.policy.capability_registry import CapabilityRegistryImpl
r = CapabilityRegistryImpl()
r.register_default_tools()
names = [t.tool_name for t in r.list_tools()]
assert 'weather_fixture_read' in names
caps = {}
for t in r.list_tools():
    for c in t.capabilities:
        caps[c.name] = c
assert 'weather.fixture.read' in caps
print('  weather.fixture.read: OK')
PYEOF

log "Phase A4: Canary patch tests"
PYTHONPATH="$REPO_ROOT/tools/agentx_evolve:$REPO_ROOT/tools" bash "$REPO_ROOT/scripts/canary-patch-test.sh" 2>&1 | tail -5

log "Phase A5: Evidence helpers"
test -f "$REPO_ROOT/tools/agentx_evolve/evidence/evidence_writer.py" && log "  evidence_writer: OK" || { log "  evidence_writer: MISSING"; exit 1; }
test -f "$REPO_ROOT/tools/agentx_evolve/evidence/event_logger.py" && log "  event_logger: OK" || { log "  event_logger: MISSING"; exit 1; }
test -f "$REPO_ROOT/tools/agentx_evolve/evidence/manifest_builder.py" && log "  manifest_builder: OK" || { log "  manifest_builder: MISSING"; exit 1; }

log "Phase A6: Prove script + Makefile target"
test -f "$REPO_ROOT/scripts/prove-umbrella-agent.sh" && log "  prove-umbrella-agent.sh: OK" || { log "  prove-umbrella-agent.sh: MISSING"; exit 1; }
grep -q "prove-umbrella-agent" "$REPO_ROOT/Makefile" && log "  Makefile target: OK" || { log "  Makefile target: MISSING"; exit 1; }

log ""
log "--- Stage A: Infrastructure verified ---"
log "Proceed to Stage B by running the umbrella agent pipeline."
log "See reports/umbrella_agent/ for evidence artifacts."
echo ""
echo "=== prove-umbrella-agent: STAGE A PASS ==="
