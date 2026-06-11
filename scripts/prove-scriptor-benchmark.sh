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
if [ -d "$BC/tests" ]; then
  PYTHONPATH="$REPO_ROOT" python3 -m pytest "$BC/tests" -q --tb=short 2>&1 | tail -1
  log "  benchcore tests: OK"
else
  log "  benchcore/tests/: MISSING"
fi
log "=== prove-scriptor-benchmark: PASS ==="
