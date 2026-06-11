#!/usr/bin/env bash
set -euo pipefail
# prove-post-umbrella.sh — Post-umbrella phase verification
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
log() { echo "[$(date +%H:%M:%S)] $*"; }
log "=== Post-Umbrella Phase Verification ==="
log "Root: $REPO_ROOT"

# Phase 0: Prior verification artifacts
log "--- Phase 0: Prior verification ---"
for f in \
  .agentx-init/five_document_closure/source_documents/source_document_inventory.json \
  .agentx-init/five_document_closure/baseline/baseline_repository_snapshot.json \
  .agentx-init/five_document_closure/baseline/baseline_command_transcript.json; do
  test -f "$REPO_ROOT/$f" && log "  $f: OK" || { log "  $f: MISSING"; exit 1; }
done

# Phase 1: Baseline manifests
log "--- Phase 1: Baseline manifests ---"
for f in \
  .agentx-init/post_umbrella/path_mapping_report.json; do
  if [ -f "$REPO_ROOT/$f" ]; then log "  $f: OK"; else log "  $f: MISSING (optional)"; fi
done

# Schemas
log "--- Infrastructure: Schemas ---"
for f in \
  schemas/benchmark_case.schema.json \
  schemas/benchmark_result.schema.json \
  schemas/command_transcript.schema.json \
  schemas/evidence_manifest.schema.json \
  schemas/event_log_entry.schema.json \
  schemas/provenance_record.schema.json \
  schemas/source_manifest.schema.json \
  schemas/umbrella_agent_input.schema.json \
  schemas/umbrella_agent_output.schema.json \
  schemas/umbrella_weather_fixture.schema.json; do
  test -f "$REPO_ROOT/$f" && log "  $f: OK" || { log "  $f: MISSING"; exit 1; }
done

# Example agents
log "--- Example Agents ---"
for agent_dir in examples/clothing_advice_agent examples/daily_planning_agent; do
  if [ -d "$REPO_ROOT/$agent_dir" ]; then
    log "  $agent_dir: OK"
  else
    log "  $agent_dir: MISSING (optional)"
  fi
done

log "=== prove-post-umbrella: PASS ==="
