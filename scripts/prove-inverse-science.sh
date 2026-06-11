#!/usr/bin/env bash
set -euo pipefail
# prove-inverse-science.sh — Inverse science optional doctrine verification
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
log() { echo "[$(date +%H:%M:%S)] $*"; }
log "=== Inverse Science Verification ==="

# Doctrine document
log "--- Doctrine ---"
test -f "$REPO_ROOT/docs/methods/INVERSE_SCIENTIFIC_METHOD.md" && log "  doctrine: OK" || { log "  doctrine: MISSING"; exit 1; }

# Warning must be present
grep -q "Inverse science is an optional planning and evidence discipline" "$REPO_ROOT/docs/methods/INVERSE_SCIENTIFIC_METHOD.md" 2>/dev/null \
  && log "  warning: OK" || { log "  warning: MISSING"; exit 1; }

# Schemas
log "--- Schemas ---"
for f in \
  schemas/inverse_science_plan.schema.json \
  schemas/inverse_science_candidate.schema.json \
  schemas/inverse_science_governance_decision.schema.json \
  schemas/inverse_science_observation.schema.json \
  schemas/inverse_science_evidence_record.schema.json \
  schemas/inverse_science_negative_knowledge.schema.json \
  schemas/inverse_science_best_known_solution.schema.json \
  schemas/inverse_science_final_report.schema.json; do
  if [ -f "$REPO_ROOT/$f" ]; then log "  $f: OK"; else log "  $f: MISSING"; fi
done

log "=== prove-inverse-science: PASS ==="
