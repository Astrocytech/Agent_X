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
  test -f "$REPO_ROOT/$f" && log "  $f: OK" || { log "  $f: MISSING"; exit 1; }
done

# Schema validation — all must be valid JSON
log "--- Schema validation ---"
for f in \
  schemas/inverse_science_plan.schema.json \
  schemas/inverse_science_candidate.schema.json \
  schemas/inverse_science_governance_decision.schema.json \
  schemas/inverse_science_observation.schema.json \
  schemas/inverse_science_evidence_record.schema.json \
  schemas/inverse_science_negative_knowledge.schema.json \
  schemas/inverse_science_best_known_solution.schema.json \
  schemas/inverse_science_final_report.schema.json; do
  python3 -c "import json; json.load(open('$REPO_ROOT/$f'))" && log "  $f: valid JSON" || { log "  $f: invalid JSON"; exit 1; }
done

# Traceability matrix
log "--- Traceability matrix ---"
test -f "$REPO_ROOT/.agentx-init/reports/inverse_science_traceability_matrix.json" || { log "  traceability matrix: MISSING"; exit 1; }
python3 -c "import json; d=json.load(open('$REPO_ROOT/.agentx-init/reports/inverse_science_traceability_matrix.json')); assert len(d.get('concepts',[])) >= 12" && log "  traceability matrix: OK" || { log "  traceability matrix: invalid"; exit 1; }

# L0 non-import check
log "--- L0 non-import check ---"
l0_imports=$(grep -r "inverse.science\|inverse_science" "$REPO_ROOT/L0/CODE/" --include="*.py" 2>/dev/null | wc -l) || true
if [ "$l0_imports" -eq 0 ]; then
  log "  inverse science NOT imported in L0/CODE: OK"
else
  log "  inverse science IS imported in L0/CODE ($l0_imports occurrences) — hard blocker"
  exit 1
fi

# Profile check
log "--- Profile check ---"
test -f "$REPO_ROOT/profiles/inverse_science_planner.yaml" && log "  inverse_science_planner.yaml: OK" || { log "  inverse_science_planner.yaml: MISSING"; exit 1; }

# Governance routing test
log "--- Governance routing test ---"
set +e
is_output=$(python3 -m pytest "$REPO_ROOT/tests/release/test_inverse_science_integration.py" -q --tb=short 2>&1)
is_rc=$?
set -e
echo "$is_output" | tail -1
test "$is_rc" -eq 0 && log "  governance routing: PASS" || { log "  governance routing: FAIL"; exit 1; }

# Security boundary test
log "--- Security boundary test ---"
set +e
sec_output=$(python3 -m pytest "$REPO_ROOT/tests/release/test_inverse_science_security.py" -q --tb=short 2>&1)
sec_rc=$?
set -e
echo "$sec_output" | tail -1
test "$sec_rc" -eq 0 && log "  security boundary: PASS" || { log "  security boundary: FAIL"; exit 1; }

# Full inverse-science workflow proof (generates then validates)
log "--- Full workflow proof ---"
log "  running full inverse-science workflow..."
PYTHONPATH="$REPO_ROOT/tools/agentx_evolve" python3 "$REPO_ROOT/tools/agentx_evolve/inverse_science/cli.py" 2>&1 | tail -1
log "  validating workflow artifacts..."
PYTHONPATH="$REPO_ROOT/tools/agentx_evolve" python3 "$REPO_ROOT/tools/agentx_evolve/inverse_science/cli.py" validate 2>&1 | tail -1 || { log "  workflow validation: FAIL"; exit 1; }

log "=== prove-inverse-science: PASS ==="
exit 0
