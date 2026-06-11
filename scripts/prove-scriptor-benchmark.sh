#!/usr/bin/env bash
set -euo pipefail
# prove-scriptor-benchmark.sh — Scriptor benchmark pack verification
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
log() { echo "[$(date +%H:%M:%S)] $*"; }
log "=== Scriptor Benchmark Pack Verification ==="

log "--- Canonical path ---"
if [ -d "$REPO_ROOT/benchmarks/benchcore" ]; then
  log "  benchmarks/benchcore/: OK"
else
  log "  benchmarks/benchcore/: MISSING — checking benchcore mapping..."
  if [ -d "$REPO_ROOT/benchmarks/benchcore" ]; then
    log "  benchmarks/benchcore/: EXISTS (mapped)"
  else
    log "  No benchmark directory found"; exit 1
  fi
fi

log "--- Source inventory ---"
BC="$REPO_ROOT/benchmarks/benchcore"
test -f "$BC/source_inventory.json" && log "  source_inventory.json: OK" || { log "  source_inventory.json: MISSING"; exit 1; }
test -f "$BC/source_hashes.json" && log "  source_hashes.json: OK" || { log "  source_hashes.json: MISSING"; exit 1; }

log "--- Core artifacts ---"
for f in \
  visual_inventory.json \
  per_pdf_semantic_coverage_report.json \
  generic_pattern_map.json \
  universal_agent_readiness_evidence_matrix.json \
  product_specific_boundary_report.json; do
  test -f "$BC/$f" && log "  $f: OK" || { log "  $f: MISSING"; exit 1; }
done

log "--- Sub-directories ---"
for d in ontology requirements evaluation feedback_loop dynamic_retrieval learning_policy \
  inverse_science_alignment grammar_validation data_quality protocol_architecture \
  human_review_ui operations_reproducibility; do
  test -d "$BC/$d" && log "  $d/: OK" || { log "  $d/: MISSING"; exit 1; }
done

log "--- Tests ---"
test -d "$BC/tests" && log "  benchcore/tests/: OK" || { log "  benchcore/tests/: MISSING"; exit 1; }
PYTHONPATH="$REPO_ROOT" python3 -m pytest "$BC/tests" -q --tb=short 2>&1 | tail -1
log "  benchcore tests: PASS"

log "--- JSON artifact validation ---"
for artifact in source_inventory.json source_hash_manifest.json universal_readiness_matrix.json; do
  python3 -c "import json; json.load(open('$BC/$artifact'))" && log "  $artifact: valid JSON" || { log "  $artifact: invalid JSON"; exit 1; }
done

log "--- Replay and acceptance reports ---"
test -f "$BC/replay_report.json" && python3 -c "import json; d=json.load(open('$BC/replay_report.json')); assert d.get('status')=='PASS'" && log "  replay_report.json: PASS" || { log "  replay_report.json: MISSING or not PASS"; exit 1; }
test -f "$BC/final_acceptance_report.json" && python3 -c "import json; d=json.load(open('$BC/final_acceptance_report.json')); assert d.get('status')=='PASS'" && log "  final_acceptance_report.json: PASS" || { log "  final_acceptance_report.json: MISSING or not PASS"; exit 1; }

log "--- Dedicated benchcore validators ---"
VALIDATOR_DIR="$REPO_ROOT/tools/agentx_evolve/validators"
python3 "$VALIDATOR_DIR/validate_benchcore_source_inventory.py" 2>&1 | tail -1 || { log "  source inventory: FAIL"; exit 1; }
python3 "$VALIDATOR_DIR/validate_benchcore_per_pdf_coverage.py" 2>&1 | tail -1 || { log "  per-pdf coverage: FAIL"; exit 1; }
python3 "$VALIDATOR_DIR/validate_benchcore_visual_inventory.py" 2>&1 | tail -1 || { log "  visual inventory: FAIL"; exit 1; }
python3 "$VALIDATOR_DIR/validate_benchcore_traceability.py" 2>&1 | tail -1 || { log "  traceability: FAIL"; exit 1; }
python3 "$VALIDATOR_DIR/validate_benchcore_claim_boundaries.py" 2>&1 | tail -1 || { log "  claim boundaries: FAIL"; exit 1; }

log "=== prove-scriptor-benchmark: PASS ==="
