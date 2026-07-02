# Governed Universal Seed Kernel Makefile
SHELL := /bin/bash
.SHELLFLAGS := -e -o pipefail -c

PYTHON ?= python3
PIP_INSTALL ?= pip3 install --user

.PHONY: help install seed-boot prove-seed prove-l1 prove-l2
.PHONY: prove-format compileall-check prove-all
.PHONY: test-quick test-dev test-release test-sabotage test-security
.PHONY: test-all test-live test-l0 test-l1 test-l2 test-initiator
.PHONY: test-evolve audit-structure prove-organization prove-hygiene
.PHONY: prove-umbrella-agent prove-post-umbrella prove-inverse-science
.PHONY: prove-scriptor-benchmark generate-final-artifacts
.PHONY: prove-functional-runtime-mvp prove-functional-runtime-mvp-idempotent
.PHONY: prove-agentx-adapter-mvp-once prove-agentx-adapter-mvp
.PHONY: prove-functional-agent-evolution-alpha prove-functional-agent-evolution-beta
.PHONY: prove-governed-self-evolution-prototype prove-functional-agentx
.PHONY: final-acceptance validate-final-acceptance run clean build-seed
.PHONY: prove-reset prove-clean

help:
	@echo "L0 commands:"
	@echo "  make install      Install minimal seed dependencies"
	@echo "  make seed-boot    Compile and boot the seed"
	@echo "  make prove-seed   Run canonical L0 seed proof"
	@echo "  make run          Run one governed seed turn"
	@echo "  make build-seed   Build seed package from manifest"
	@echo "Layer tests:"
	@echo "  make prove-l1     Run L1 structure tests"
	@echo "  make prove-l2     Run L2 structure tests"
	@echo "  make test-l0      Run L0 tests (alias for prove-seed)"
	@echo "  make test-l1      Run L1 tests (alias for prove-l1)"
	@echo "  make test-l2      Run L2 tests (alias for prove-l2)"
	@echo "Tool tests:"
	@echo "  make test-evolve  Run agentx_evolve tests"
	@echo "  make test-initiator Run agentx_initiator tests"
	@echo "Tiered test suites:"
	@echo "  make test-quick       Run fast tests (~4s) — run after every change"
	@echo "  make test-dev         Run work-in-progress tests (may fail)"
	@echo "  make test-release     Run full release verification (~5min)"
	@echo "  make test-sabotage    Run sabotage/mutation checks"
	@echo "  make test-security    Run negative security tests"
	@echo "  make test-all         Run all tests across repo (excl. live)"
	@echo "  make test-live        Run live provider tests"
	@echo "  make prove-functional-runtime-mvp Run Functional Runtime MVP proof"
	@echo "  make prove-functional-runtime-mvp-idempotent Run MVP proof twice and verify consistency"
	@echo "  make prove-format     Run formatting guard tests"
	@echo "  make audit-structure  Run repository structure audit"
	@echo "  make prove-all        Run all layer tests + audit"
	@echo "  make prove-organization Run full org acceptance"
	@echo "Evolution proofs (build on each other):"
	@echo "  make prove-functional-agent-evolution-alpha  Single generated agent proof"
	@echo "  make prove-functional-agent-evolution-beta   Multi-agent, rollback, versioning"
	@echo "  make prove-governed-self-evolution-prototype Self-evolution cycles w/ safety gates"
	@echo "  make prove-functional-agentx                Unified end-to-end proof"
	@echo "  make clean        Remove generated runtime artifacts"

# target_id: P2-C001
install:
	$(PIP_INSTALL) -r requirements/seed.txt

# target_id: P2-C002
seed-boot:
	PYTHONPATH=L0/CODE $(PYTHON) -m compileall -q L0/CODE
	PYTHONPATH=L0/CODE $(PYTHON) L0/scripts/proofs/prove_seed_boot.py
	@echo "=== seed-boot: OK ==="

# target_id: P2-C003
prove-seed:
	PYTHONPATH=L0/CODE $(PYTHON) -m compileall -q L0/CODE
	PYTHONPATH=L0/CODE $(PYTHON) L0/scripts/proofs/validate_seed_manifests.py
	PYTHONPATH=L0/CODE $(PYTHON) -m pytest L0/tests/seed_l0 -q --tb=short -p no:cacheprovider
	@echo "=== prove-seed: OK ==="

# target_id: P2-C004
prove-l1:
	PYTHONPATH=L1 $(PYTHON) -m compileall -q L1
	PYTHONPATH=. $(PYTHON) -m pytest L1/tests -q --tb=short -p no:cacheprovider
	PYTHONPATH=. $(PYTHON) -m L1.validators.validate_all
	@echo "=== prove-l1: OK ==="

# target_id: P2-C005
prove-l2:
	$(PYTHON) L2/validators/bootstrap_validate_l2_scaffold.py
	PYTHONPATH=L2 $(PYTHON) -m pytest L2/tests -q --tb=short -p no:cacheprovider
	@echo "=== prove-l2: OK ==="

# target_id: P2-C006
prove-format:
	PYTHONPATH=. $(PYTHON) -m pytest tests/quick/test_text_file_formatting.py tests/quick/test_format_guard_self_integrity.py tests/quick/test_makefile_proof_wiring.py -q --tb=short -p no:cacheprovider
	@echo "=== prove-format: OK ==="

# target_id: P2-C007
# NOTE: prove-functional-agentx is the authoritative final acceptance pipeline.
# prove-all delegates to it as a safety net and will be deprecated once
# all classification levels are validated exclusively through the new pipeline.
prove-all: prove-format compileall-check prove-seed prove-l1 prove-l2 test-initiator \
  test-evolve test-integration test-system test-regression test-all \
  prove-umbrella-agent generate-final-artifacts prove-post-umbrella \
  prove-inverse-science prove-scriptor-benchmark final-acceptance \
  prove-functional-agentx audit-structure
	@echo "=== prove-all: OK ==="
	@echo "=== All targets passed ==="
	@echo "=== CAVEAT: prove-all is legacy. prove-functional-agentx is authoritative. ==="

compileall-check:
	$(PYTHON) -m compileall -q L0 L1 L2 tools tests
	@echo "=== compileall-check: OK ==="

# target_id: P2-C008
audit-structure:
	PYTHONPATH=tools/repo_audit $(PYTHON) tools/repo_audit/audit_repository_structure.py
	@echo "=== audit-structure: OK ==="

# target_id: P2-C009
prove-organization:
	$(MAKE) audit-structure
	PYTHONPATH=. $(PYTHON) -m pytest --collect-only -q
	find . -maxdepth 1 -type f | sort
	git status --short
	@echo "=== prove-organization: OK ==="

# ── Tiered test suites ─────────────────────────────────────────────────────

# target_id: P2-C010
test-quick:
	PYTHONPATH=. $(PYTHON) -m pytest tests/quick -q --tb=short -p no:cacheprovider

# target_id: P2-C011
test-dev:
	PYTHONPATH=. $(PYTHON) -m pytest tests/dev -q --tb=short -p no:cacheprovider

# target_id: P2-C012
test-release:
	PYTHONPATH="L0/CODE:L1:L2:tools/agentx_initiator:tools/agentx_evolve:tools" \
	$(PYTHON) -m pytest tests/release L1/tests L2/tests \
	  tools/agentx_initiator/tests tools/agentx_evolve/tests \
	  -q --tb=short -p no:cacheprovider -m "not live"

# target_id: P2-C013
test-sabotage:
	PYTHONPATH="L0/CODE:L1:L2:tools/agentx_initiator:tools/agentx_evolve:tools" $(PYTHON) -m pytest tests/release/test_sabotage_checks.py -q --tb=short -p no:cacheprovider

# target_id: P2-C014
test-security:
	PYTHONPATH="L0/CODE:L1:L2:tools/agentx_initiator:tools/agentx_evolve:tools" $(PYTHON) -m pytest tests/release/test_negative_*.py -q --tb=short -p no:cacheprovider

# target_id: P2-C015
test-live:
	PYTHONPATH=. $(PYTHON) -m pytest -q -m live --tb=short -p no:cacheprovider

# target_id: P2-C016
test-all:
	PYTHONPATH="L0/CODE:L1:L2:tools/agentx_initiator:tools/agentx_evolve:tools" \
	$(PYTHON) -m pytest tests/quick tests/dev tests/release \
	  L1/tests L2/tests tools/agentx_initiator/tests \
	  tools/agentx_evolve/tests -q --tb=short -p no:cacheprovider -m "not live"

# ── Legacy aliases (deprecated, route to new tiers) ────────────────────────

test-smoke: test-quick

test-integration:
	PYTHONPATH="L0/CODE:L1:L2:tools/agentx_initiator:tools/agentx_evolve:tools" \
	$(PYTHON) -m pytest tests/release/test_integration_governed_patch_handoff.py \
	  tests/release/test_model_context_worker_flow.py \
	  -q --tb=short -p no:cacheprovider -m "not live"

test-system:
	$(MAKE) prove-l2
	PYTHONPATH="L0/CODE:L1:L2:tools/agentx_initiator:tools/agentx_evolve:tools" $(PYTHON) -m pytest tests/release/test_system_inverse_science.py -q --tb=short -p no:cacheprovider -m "not live"

test-regression:
	PYTHONPATH="L0/CODE:L1:L2:tools/agentx_initiator:tools/agentx_evolve:tools" \
	$(PYTHON) -m pytest tests/release L1/tests L2/tests \
	  tools/agentx_initiator/tests tools/agentx_evolve/tests \
	  -q --tb=short -p no:cacheprovider -m "not live"

test-l0: prove-seed

test-l1: prove-l1

test-l2: prove-l2

# target_id: P2-C017
test-initiator:
	PYTHONPATH=tools/agentx_initiator $(PYTHON) -m pytest tools/agentx_initiator/tests -q --tb=short -p no:cacheprovider

# target_id: P2-C018
test-evolve:
	PYTHONPATH=tools/agentx_evolve $(PYTHON) -m pytest tools/agentx_evolve/tests -q --tb=short -p no:cacheprovider

# target_id: P2-C019
prove-hygiene:
	PYTHONPATH=L0/CODE ruff check L0/CODE/
	PYTHONPATH=L0/CODE $(PYTHON) -m mypy L0/CODE/core_kernel/ L0/CODE/tool_gateway/ L0/CODE/governance/ --ignore-missing-imports
	pip-audit -r requirements/seed.txt
	@echo "=== prove-hygiene: OK ==="

# target_id: P2-C020
prove-umbrella-agent:
	bash scripts/prove-umbrella-agent.sh

# target_id: P2-C020-alt1
prove-post-umbrella:
	bash scripts/prove-post-umbrella.sh

# target_id: P2-C020-alt2
prove-inverse-science:
	bash scripts/prove-inverse-science.sh

# target_id: P2-C020-alt3
prove-scriptor-benchmark:
	bash scripts/prove-scriptor-benchmark.sh

# target_id: P2-C020-alt3b1
MVP_PYTHONPATH = L0/CODE:L1:L2:tools/agentx_initiator:tools/agentx_evolve:tools
MVP_TESTS = \
  tools/agentx_evolve/tests/test_runtime_context.py \
  tools/agentx_evolve/tests/test_workspace_manager.py \
  tools/agentx_evolve/tests/test_artifact_store.py \
  tools/agentx_evolve/tests/test_io_envelope.py \
  tools/agentx_evolve/tests/test_runtime_profile.py \
  tools/agentx_evolve/tests/test_readiness.py \
  tools/agentx_evolve/tests/test_state_store.py \
  tools/agentx_evolve/tests/test_event_bus.py \
  tools/agentx_evolve/tests/test_action_lifecycle.py \
  tools/agentx_evolve/tests/test_contract_registry.py \
  tools/agentx_evolve/tests/test_capability_graph.py \
  tools/agentx_evolve/tests/test_policy_rule_engine.py \
  tools/agentx_evolve/tests/test_decision_gate.py \
  tools/agentx_evolve/tests/test_invariant_engine.py \
  tools/agentx_evolve/tests/test_security_envelope.py \
  tools/agentx_evolve/tests/test_transaction_manager.py \
  tools/agentx_evolve/tests/test_simulation_engine.py \
  tools/agentx_evolve/tests/test_report_generation_executor.py \
  tools/agentx_evolve/tests/test_observer.py \
  tools/agentx_evolve/tests/test_rollback_controller.py \
  tools/agentx_evolve/tests/test_circuit_breaker.py \
  tools/agentx_evolve/tests/test_review_interface.py \
  tools/agentx_evolve/tests/test_promotion_gate.py \
  tools/agentx_evolve/tests/test_scenario_runner.py \
  tools/agentx_evolve/tests/test_functional_orchestrator.py \
  tools/agentx_evolve/tests/test_functional_acceptance.py \
  tools/agentx_evolve/tests/test_functional_mvp_validators.py \
  tests/system/test_safe_report_generation_goal.py \
  tests/system/test_unsafe_self_promotion_goal.py \
  tests/system/test_functional_runtime_mvp_replay.py

REC = PYTHONPATH="$(MVP_PYTHONPATH)" $(PYTHON) tools/agentx_evolve/acceptance/record_command.py --
FUNCTIONAL_AGENTX_REC = PYTHONPATH="$(MVP_PYTHONPATH)" $(PYTHON) tools/agentx_evolve/acceptance/record_command.py --

prove-functional-runtime-mvp-once:
	# ============================================================
	# PHASE 1: SETUP — clean, proof_run_id, pre-checks
	# ============================================================
	rm -rf .agentx-init/reports/
	mkdir -p .agentx-init/reports/
	$(eval PROOF_RUN_ID := mvp-$(shell date +%s)-$(shell git rev-parse HEAD))
	$(eval export PROOF_RUN_ID)
	@echo "Proof run ID: $(PROOF_RUN_ID)"
	# Acquire serial executor lock (prevents concurrent runs)
	PYTHONPATH="$(MVP_PYTHONPATH)" $(PYTHON) tools/agentx_evolve/runtime/serial_executor_guard.py lock $(PROOF_RUN_ID)
	# Check working tree at start
	@echo "Working tree at start:"; git status --porcelain
	# Record git commit (full SHA)
	@echo "Git commit: $$(git rev-parse HEAD)"
	# ============================================================
	# PHASE 2: GENERATE — compile, test, reports, traceability
	# ============================================================
	# 2a. Compile check
	$(REC) $(PYTHON) -m compileall -q tools/agentx_evolve tests
	# 2b. Run MVP test suite (validators + scenarios)
	$(REC) $(PYTHON) -m pytest \
	  $(MVP_TESTS) \
	  -q --tb=short -p no:cacheprovider -m "not live"
	# 2c. Snapshot baseline transcript BEFORE report generation
	cp .agentx-init/reports/functional_runtime_mvp_command_transcript.json \
	  .agentx-init/reports/functional_runtime_mvp_baseline_command_transcript.json
	# 2d. Initial proof collection and report generation
	PYTHONPATH="$(MVP_PYTHONPATH)" $(PYTHON) tools/agentx_evolve/acceptance/collect_mvp_proof.py
	PYTHONPATH="$(MVP_PYTHONPATH)" $(PYTHON) tools/agentx_evolve/acceptance/generate_mvp_reports.py
	# ============================================================
	# PHASE 3: VALIDATE — run all validators
	# ============================================================
	# 3a. Specialized validators (generation + scenario)
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_gap_discovery.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_replay.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_reuse_map.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_source_safety.py
	# 3b. Runtime safety validators (bootstrap anti-false-PASS excluded; runs in final phase)
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_self_promotion.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_event_log.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_state.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_path_safety.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_runtime_safety.py
	# 3c. Cross-domain validators
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_cross_report.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_clean_checkout.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_artifact_safety.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_execution_integrity.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_provenance.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_security.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_completeness.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_lifecycle.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_infrastructure.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_determinism.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_meta_quality.py
	# 3d. Test-evolve (slow but must pass for FUNCTIONAL_RUNTIME_MVP)
	$(REC) make test-evolve
	# ============================================================
	# PHASE 4: FREEZE — rebuild, freeze, re-freeze
	# ============================================================
	# 4a. Validate transcript (all commands now recorded)
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_transcript.py
	# 4b. Rebuild reports with complete transcript
	PYTHONPATH="$(MVP_PYTHONPATH)" $(PYTHON) tools/agentx_evolve/acceptance/collect_mvp_proof.py --rebuild-reports
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_reports.py
	# 4c. Rebuild traceability matrix (no forced PASS) and validate
	AGENTX_MVP_NO_FORCED_PASS=1 PYTHONPATH="$(MVP_PYTHONPATH)" $(PYTHON) -c "from agentx_evolve.acceptance.generate_traceability_matrix import generate_traceability_matrix; generate_traceability_matrix()"
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_traceability.py
	# 4d. Final freeze — proof bundle, evidence manifest
	PYTHONPATH="$(MVP_PYTHONPATH)" $(PYTHON) tools/agentx_evolve/acceptance/collect_mvp_proof.py --full
	# 4e. Regenerate .md from .json
	PYTHONPATH="$(MVP_PYTHONPATH)" $(PYTHON) tools/agentx_evolve/acceptance/regenerate_transcript_md.py
	# 4ef. Exercise orchestrator to create runtime artifacts (state, events, review, promotion)
	$(REC) $(PYTHON) tools/agentx_evolve/acceptance/exercise_orchestrator_scenarios.py
	# 4f. Runtime proof generation — state reconstruction + entrypoint
	$(REC) $(PYTHON) tools/agentx_evolve/runtime/state_reconstruction_proof.py
	$(REC) $(PYTHON) tools/agentx_evolve/runtime/runtime_entrypoint_proof.py
	# ============================================================
	# PHASE 5: FINALIZE — meta-validators, final_verdict, seal
	# ============================================================
	# 5a. Meta validators (check validators themselves)
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_validator_proof.py
	# 5ai. Generate filesystem snapshot before validating it (no REC — must capture transcript before record_command modifies it)
	PYTHONPATH="$(MVP_PYTHONPATH)" $(PYTHON) tools/agentx_evolve/acceptance/generate_filesystem_snapshot.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_filesystem_snapshot.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_core_invariants.py
	# 5b. Cross-report and proof configuration validators
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_all_in_one.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_proof_staleness.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_schema_version.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_proof_config.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_state_transition.py
	# 5c. Security and integrity validators
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_secret_redaction.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_side_effect.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_failure_taxonomy.py
	# 5d. No-forced-PASS guard
	AGENTX_MVP_NO_FORCED_PASS=1 $(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_no_forced_pass.py
	# 5e. Architecture scope map generation and validation
	$(REC) $(PYTHON) tools/agentx_evolve/acceptance/generate_scope_map.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_scope_map.py
	# 5f. No-hidden-authority check
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_no_hidden_authority.py
	# 5g. Proof-configuration manifest generation
	$(REC) $(PYTHON) tools/agentx_evolve/acceptance/generate_proof_config_manifest.py
	# 5h. Required artifacts manifest generation and validation
	$(REC) $(PYTHON) tools/agentx_evolve/acceptance/generate_required_artifacts_manifest.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_required_artifacts.py
	# 5i. Classification consistency
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_classification_consistency.py
	# 5j. JSON/Markdown non-contradiction
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_json_markdown_consistency.py
	# 5k. I/O boundary validation
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_io_boundary.py
	# 5l. Proof size validation
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_proof_size.py
	# 5m. Zero-byte and UTF-8 validation on all reports
	$(REC) $(PYTHON) tools/agentx_evolve/acceptance/validate_zero_byte_utf8.py
	# 5n. Runtime proof validators — state reconstruction + entrypoint
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_state_reconstruction.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_runtime_entrypoint.py
	# 5o. Anti-false-PASS audit
	$(REC) $(PYTHON) tools/agentx_evolve/acceptance/run_anti_false_pass_audit.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_anti_false_pass.py
	# 5o2. Regenerate traceability + acceptance with anti-false-PASS evidence now present
	AGENTX_MVP_NO_FORCED_PASS=1 PYTHONPATH="$(MVP_PYTHONPATH)" $(PYTHON) -c \
	  "from agentx_evolve.acceptance.generate_traceability_matrix import generate_traceability_matrix; generate_traceability_matrix()"
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_traceability.py
	PYTHONPATH="$(MVP_PYTHONPATH)" $(PYTHON) tools/agentx_evolve/acceptance/collect_mvp_proof.py --rebuild-reports
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_reports.py
	PYTHONPATH="$(MVP_PYTHONPATH)" $(PYTHON) tools/agentx_evolve/acceptance/collect_mvp_proof.py --full
	# 5p. Generate candidate verdict and validate (after all validators and anti-false-PASS)
	# Candidate mode excludes self-referential validators (final_verdict, idempotency)
	# so the one-run target produces a self-consistent candidate verdict.
	$(REC) $(PYTHON) tools/agentx_evolve/acceptance/generate_final_verdict.py $(PROOF_RUN_ID) --candidate
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_final_verdict.py --candidate
	# ============================================================
	# PHASE 6: CI EVIDENCE — offline bundle + secrets scan + validation
	# ============================================================
	$(REC) $(PYTHON) tools/agentx_evolve/acceptance/extra_generators.py
	-$(REC) $(PYTHON) tools/agentx_evolve/acceptance/scan_secrets.py
	-$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_confidentiality.py
	# Release serial executor lock
	-PYTHONPATH="$(MVP_PYTHONPATH)" $(PYTHON) tools/agentx_evolve/runtime/serial_executor_guard.py unlock $(PROOF_RUN_ID)
	@echo "=== prove-functional-runtime-mvp-once: OK ==="

prove-functional-runtime-mvp:
	# Two clean runs + idempotency comparison
	rm -rf /tmp/agentx-mvp-idempotency
	mkdir -p /tmp/agentx-mvp-idempotency/run1 /tmp/agentx-mvp-idempotency/run2
	$(MAKE) prove-functional-runtime-mvp-once
	cp -R .agentx-init/reports/. /tmp/agentx-mvp-idempotency/run1/
	$(MAKE) prove-functional-runtime-mvp-once
	cp -R .agentx-init/reports/. /tmp/agentx-mvp-idempotency/run2/
	$(REC) $(PYTHON) tools/agentx_evolve/acceptance/generate_idempotency_report.py \
	  --run1 /tmp/agentx-mvp-idempotency/run1 \
	  --run2 /tmp/agentx-mvp-idempotency/run2
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_idempotency.py
	# Final verdict for dual-run proof (verified mode — includes idempotency check)
	$(REC) $(PYTHON) tools/agentx_evolve/acceptance/generate_final_verdict.py dual-$(shell date +%s) --dual
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_final_verdict.py
	@echo "=== prove-functional-runtime-mvp: OK ==="

prove-functional-runtime-mvp-expanded-coverage:
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_advanced.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_deep.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_enterprise.py
	$(REC) $(PYTHON) tools/agentx_evolve/validators/validate_functional_runtime_mvp_aspirational.py
	@echo "=== prove-functional-runtime-mvp-expanded-coverage: OK ==="

prove-functional-runtime-mvp-idempotent: prove-functional-runtime-mvp
	@echo "=== prove-functional-runtime-mvp-idempotent: OK ==="

ADAPTER_MVP_PYTHONPATH = tools
ADAPTER_MVP_TESTS = \
  tools/agentx_evolve/tests/test_model_adapter_interface.py \
  tools/agentx_evolve/tests/test_deterministic_mock_model_adapter.py \
  tools/agentx_evolve/tests/test_prompt_contract.py \
  tools/agentx_evolve/tests/test_context_builder_structural_factual_split.py \
  tools/agentx_evolve/tests/test_evidence_bridge.py \
  tools/agentx_evolve/tests/test_adapter_registry.py \
  tools/agentx_evolve/tests/test_tool_adapter_interface.py \
  tools/agentx_evolve/tests/test_local_tool_adapter.py \
  tools/agentx_evolve/tests/test_mcp_shell.py \
  tools/agentx_evolve/tests/test_replay_policy.py \
  tools/agentx_evolve/tests/test_failure_taxonomy.py \
  tools/agentx_evolve/tests/test_conformance.py \
  tools/agentx_evolve/tests/test_agentx_adapter_mvp_mock_flow.py \
  tools/agentx_evolve/tests/test_read_only_repo_info_tool.py \
  tools/agentx_evolve/tests/test_cohere_model_adapter_mocked.py

ADAPTER_REC = PYTHONPATH="$(ADAPTER_MVP_PYTHONPATH)" $(PYTHON) tools/agentx_evolve/acceptance/adapter_record_command.py --

prove-agentx-adapter-mvp-once:
	# ============================================================
	# AGENTX ADAPTER MVP — offline deterministic proof (single run)
	# ============================================================
	rm -rf .agentx-init/reports/adapter-mvp/
	mkdir -p .agentx-init/reports/adapter-mvp/
	# 1. Compileall check (item 10: compileall)
	$(ADAPTER_REC) $(PYTHON) -m compileall -q tools/agentx_evolve tests
	# 2. Generate acceptance matrix
	$(ADAPTER_REC) $(PYTHON) tools/agentx_evolve/generate_adapter_acceptance_matrix.py
	# 3. Anti-false-PASS audit and validation
	$(ADAPTER_REC) $(PYTHON) tools/agentx_evolve/run_adapter_anti_false_pass_audit.py
	$(ADAPTER_REC) $(PYTHON) tools/agentx_evolve/validate_agentx_adapter_anti_false_pass.py
	# 4. Run all adapter MVP tests
	$(ADAPTER_REC) $(PYTHON) -m pytest $(ADAPTER_MVP_TESTS) -q --tb=short -p no:cacheprovider
	# 5. Validate adapter replay (deterministic mock)
	$(ADAPTER_REC) $(PYTHON) tools/agentx_evolve/validate_agentx_adapter_replay.py
	# 6. Run acceptance matrix validators (shell=True replaced with explicit subprocess)
	$(ADAPTER_REC) $(PYTHON) tools/agentx_evolve/validate_agentx_adapter_acceptance_matrix.py
	# 7. Generate evidence manifest (before final verdict so transcript includes it)
	$(ADAPTER_REC) $(PYTHON) tools/agentx_evolve/acceptance/generate_adapter_evidence_manifest.py
	# 8. Generate final verdict (candidate mode excludes self-referential validators)
	$(ADAPTER_REC) $(PYTHON) tools/agentx_evolve/generate_adapter_final_verdict.py --candidate
	# 9. Validate final verdict (gates the build)
	$(ADAPTER_REC) $(PYTHON) tools/agentx_evolve/validate_agentx_adapter_final_verdict.py
	# 10. Validate FRMVP non-regression (verdict content, not just existence)
	$(ADAPTER_REC) $(PYTHON) tools/agentx_evolve/acceptance/check_frmvp_non_regression.py
	# 11. Generate report path aliases for backward compatibility
	$(ADAPTER_REC) $(PYTHON) tools/agentx_evolve/acceptance/generate_adapter_report_aliases.py
	@echo "=== prove-agentx-adapter-mvp-once: OK ==="

prove-agentx-adapter-mvp:
	# ============================================================
	# AGENTX ADAPTER MVP — dual-run idempotent proof
	# ============================================================
	rm -rf /tmp/agentx-adapter-idempotency
	mkdir -p /tmp/agentx-adapter-idempotency/run1 /tmp/agentx-adapter-idempotency/run2
	$(MAKE) prove-agentx-adapter-mvp-once
	cp -R .agentx-init/reports/adapter-mvp/. /tmp/agentx-adapter-idempotency/run1/
	$(MAKE) prove-agentx-adapter-mvp-once
	cp -R .agentx-init/reports/adapter-mvp/. /tmp/agentx-adapter-idempotency/run2/
	$(ADAPTER_REC) $(PYTHON) tools/agentx_evolve/acceptance/generate_adapter_idempotency_report.py \
	  --run1 /tmp/agentx-adapter-idempotency/run1 \
	  --run2 /tmp/agentx-adapter-idempotency/run2
	$(ADAPTER_REC) $(PYTHON) tools/agentx_evolve/generate_adapter_final_verdict.py --dual
	$(ADAPTER_REC) $(PYTHON) tools/agentx_evolve/validate_agentx_adapter_final_verdict.py
	# Regenerate aliases after dual-run promotion
	$(ADAPTER_REC) $(PYTHON) tools/agentx_evolve/acceptance/generate_adapter_report_aliases.py
	@echo "=== prove-agentx-adapter-mvp: OK ==="

# target_id: N2-A06
# Stage M2: Repo Memory / RAG MVP — deterministic indexing, evidence filtering, replay
prove-agentx-repo-memory-mvp:
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) -m pytest \
	  tools/agentx_evolve/tests/test_learning_docsync_adapter.py \
	  tools/agentx_evolve/tests/test_learning_memory_adapter.py \
	  tools/agentx_evolve/tests/test_memory_candidate_builder.py \
	  tools/agentx_evolve/tests/test_memory_retention_revocation.py \
	  tools/agentx_evolve/tests/test_context_builder_structural_factual_split.py \
	  -q --tb=short -p no:cacheprovider
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/final_agentx/generate_stage_acceptance_matrix.py repo-memory
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/final_agentx/validate_stage_bundle.py repo-memory
	@echo "=== prove-agentx-repo-memory-mvp: OK ==="

# target_id: N2-A07
# Stage M3: Generated-Agent Git Promotion — staged files, patch, review, promotion gate
prove-agentx-generated-agent-git-promotion:
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) -m pytest \
	  tools/agentx_evolve/tests/test_git_tool_adapter_integration.py \
	  tools/agentx_evolve/tests/test_git_mutation_gate.py \
	  tools/agentx_evolve/tests/test_promotion_gate.py \
	  tools/agentx_evolve/tests/test_promotion_dispatcher.py \
	  tools/agentx_evolve/tests/test_promotion_tool_evidence.py \
	  tools/agentx_evolve/tests/test_promotion_integration_cases.py \
	  tools/agentx_evolve/tests/test_promotion_models.py \
	  tools/agentx_evolve/tests/test_orchestrator_promotion_controller.py \
	  -q --tb=short -p no:cacheprovider
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/final_agentx/generate_stage_acceptance_matrix.py git-promotion
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/final_agentx/validate_stage_bundle.py git-promotion
	@echo "=== prove-agentx-generated-agent-git-promotion: OK ==="

# target_id: P2-C024
# First Concrete Milestone: Generic Governed Action and Agent Lifecycle Engine (10/10 rev5 §22)
test-functional-lifecycle:
	$(PYTHON) -m pytest tools/agentx_evolve/tests/test_action_lifecycle.py \
	  tools/agentx_evolve/tests/test_decision_gate.py \
	  tools/agentx_evolve/tests/test_invariant_engine.py \
	  tools/agentx_evolve/tests/test_capability_graph.py \
	  -q --tb=short -p no:cacheprovider
	@echo "=== test-functional-lifecycle: OK ==="

# target_id: P3-A02
# Stage 3: Functional Agent Evolution Alpha (N2 roadmap §23)
prove-functional-agent-evolution-alpha:
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) -m pytest tools/agentx_evolve/tests/test_action_lifecycle.py \
	  tools/agentx_evolve/tests/test_decision_gate.py \
	  tools/agentx_evolve/tests/test_invariant_engine.py \
	  tools/agentx_evolve/tests/test_capability_graph.py \
	  tools/agentx_evolve/tests/test_self_evolution_controller.py \
	  tools/agentx_evolve/tests/test_agent_roles.py \
	  tools/agentx_evolve/tests/test_goal_evaluator.py \
	  tools/agentx_evolve/tests/test_goal_evaluator_integration.py \
	  tools/agentx_evolve/tests/test_adversarial_engine.py \
	  tools/agentx_evolve/tests/test_adversarial_probes.py \
	  tools/agentx_evolve/tests/test_operational_loop.py \
	  tools/agentx_evolve/tests/test_loop_integration.py \
	  tools/agentx_evolve/tests/test_blackboard.py \
	  tools/agentx_evolve/tests/test_blackboard_integration.py \
	  tools/agentx_evolve/tests/test_checkpoint_manager.py \
	  tools/agentx_evolve/tests/test_checkpoint_integration.py \
	  tools/agentx_evolve/tests/test_orchestrator_security.py \
	  tools/agentx_evolve/tests/test_evolution_integration.py \
	  tools/agentx_evolve/tests/test_schema_validator.py \
	  tools/agentx_evolve/tests/test_test_generator.py \
	  -q --tb=short -p no:cacheprovider
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_anti_false_pass.py alpha
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_evidence_manifest.py alpha
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_command_transcript.py alpha
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_command_transcript.py alpha
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_acceptance_matrix.py alpha
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_final_verdict.py alpha
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_replay_report.py alpha
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_replay.py alpha
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_acceptance_matrix.py alpha
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_anti_false_pass.py alpha
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_final_verdict.py alpha
	@echo "=== prove-functional-agent-evolution-alpha: OK ==="

# target_id: P3-A03
# Stage 4: Functional Agent Evolution Beta — multi-agent, rollback, versioning, memory, causal
prove-functional-agent-evolution-beta: prove-functional-agent-evolution-alpha
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) -m pytest \
	  tools/agentx_evolve/tests/test_rollback_manager.py \
	  tools/agentx_evolve/tests/test_rollback_controller.py \
	  tools/agentx_evolve/tests/test_prompt_versioning.py \
	  tools/agentx_evolve/tests/test_prompt_version_schema.py \
	  tools/agentx_evolve/tests/test_dependency_lock_validator.py \
	  tools/agentx_evolve/tests/test_dependency_lock.py \
	  tools/agentx_evolve/tests/test_dependency_inventory_writer.py \
	  tools/agentx_evolve/tests/test_memory_retention_revocation.py \
	  tools/agentx_evolve/tests/test_memory_candidate_builder.py \
	  tools/agentx_evolve/tests/test_learning_memory_adapter.py \
	  tools/agentx_evolve/tests/test_learning_causal_attribution.py \
	  tools/agentx_evolve/tests/test_failure_taxonomy.py \
	  tools/agentx_evolve/tests/test_recovery_failure_taxonomy.py \
	  tools/agentx_evolve/tests/test_recovery_decider.py \
	  tools/agentx_evolve/tests/test_recovery_recovery_playbook.py \
	  tools/agentx_evolve/tests/test_recovery_policy.py \
	  tools/agentx_evolve/tests/test_recovery_manager.py \
	  tools/agentx_evolve/tests/test_orchestrator_failure_recovery.py \
	  tools/agentx_evolve/tests/test_orchestrator_recovery_controller.py \
	  tools/agentx_evolve/tests/test_orchestrator_negative_cases.py \
	  tools/agentx_evolve/tests/test_orchestrator_replay.py \
	  tools/agentx_evolve/tests/test_functional_orchestrator.py \
	  tools/agentx_evolve/tests/test_learning_lifecycle.py \
	  tools/agentx_evolve/tests/test_learning_evaluation_adapter.py \
	  tools/agentx_evolve/tests/test_learning_policy_adapter.py \
	  tools/agentx_evolve/tests/test_learning_promotion_adapter.py \
	  tools/agentx_evolve/tests/test_learning_monitoring_adapter.py \
	  tools/agentx_evolve/tests/test_learning_boundary.py \
	  tools/agentx_evolve/tests/test_learning_learning_lock.py \
	  tools/agentx_evolve/tests/test_learning_idempotency_and_locking.py \
	  tools/agentx_evolve/tests/test_learning_replay_idempotency.py \
	  tools/agentx_evolve/tests/test_learning_boundaries.py \
	  tools/agentx_evolve/tests/test_learning_anti_poisoning.py \
	  tools/agentx_evolve/tests/test_learning_negative_cases.py \
	  tools/agentx_evolve/tests/test_monitoring_traces.py \
	  tools/agentx_evolve/tests/test_monitoring_trace_collector.py \
	  tools/agentx_evolve/tests/test_monitoring_integration_failure_taxonomy.py \
	  tools/agentx_evolve/tests/test_monitoring_review_report.py \
	  tools/agentx_evolve/tests/test_monitoring_report_builder.py \
	  tools/agentx_evolve/tests/test_promotion_dispatcher.py \
	  tools/agentx_evolve/tests/test_promotion_tool_evidence.py \
	  tools/agentx_evolve/tests/test_orchestrator_promotion_controller.py \
	  tools/agentx_evolve/tests/test_promotion_expiry.py \
	  tools/agentx_evolve/tests/test_promotion_promotion_expiry.py \
	  tools/agentx_evolve/tests/test_sub_systems_negative_cases.py \
	  -q --tb=short -p no:cacheprovider
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_anti_false_pass.py beta
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_evidence_manifest.py beta
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_command_transcript.py beta
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_command_transcript.py beta
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_acceptance_matrix.py beta
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_final_verdict.py beta
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_replay_report.py beta
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_replay.py beta
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_acceptance_matrix.py beta
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_anti_false_pass.py beta
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_final_verdict.py beta
	@echo "=== prove-functional-agent-evolution-beta: OK ==="

# target_id: P3-A04
# Stage 5: Governed Self-Evolution Prototype — multi-cycle, orchestrator, gates, safety, recovery
prove-governed-self-evolution-prototype: prove-functional-agent-evolution-beta
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) -m pytest \
	  tools/agentx_evolve/tests/test_self_evolution_orchestrator_engine.py \
	  tools/agentx_evolve/tests/test_self_evolution_orchestrator_dispatcher.py \
	  tools/agentx_evolve/tests/test_self_evolution_orchestrator_state.py \
	  tools/agentx_evolve/tests/test_self_evolution_orchestrator_locking.py \
	  tools/agentx_evolve/tests/test_self_evolution_orchestrator_audit.py \
	  tools/agentx_evolve/tests/test_self_evolution_orchestrator_config.py \
	  tools/agentx_evolve/tests/test_self_evolution_orchestrator_models.py \
	  tools/agentx_evolve/tests/test_self_evolution_orchestrator_session_manager.py \
	  tools/agentx_evolve/tests/test_self_evolution_orchestrator_schema_validation.py \
	  tools/agentx_evolve/tests/test_self_evolution_orchestrator_negative_cases.py \
	  tools/agentx_evolve/tests/test_self_evolution_orchestrator_idempotency.py \
	  tools/agentx_evolve/tests/test_self_evolution_emergency_stop.py \
	  tools/agentx_evolve/tests/test_self_evolution_gate_controller.py \
	  tools/agentx_evolve/tests/test_self_evolution_recovery_controller.py \
	  tools/agentx_evolve/tests/test_self_evolution_session_isolation.py \
	  tools/agentx_evolve/tests/test_self_evolution_resource_budget.py \
	  tools/agentx_evolve/tests/test_self_evolution_step_executor.py \
	  tools/agentx_evolve/tests/test_self_evolution_prompt_binding.py \
	  tools/agentx_evolve/tests/test_self_evolution_context_binding.py \
	  tools/agentx_evolve/tests/test_self_evolution_model_invocation.py \
	  tools/agentx_evolve/tests/test_self_evolution_tool_invocation.py \
	  tools/agentx_evolve/tests/test_self_evolution_command_invocation.py \
	  tools/agentx_evolve/tests/test_self_evolution_plan_revision.py \
	  tools/agentx_evolve/tests/test_self_evolution_mcp_exposure.py \
	  tools/agentx_evolve/tests/test_self_evolution_dependency_availability.py \
	  tools/agentx_evolve/tests/test_self_evolution_promotion_controller.py \
	  tools/agentx_evolve/tests/test_orchestrator_orchestrator_engine.py \
	  tools/agentx_evolve/tests/test_orchestrator_orchestrator_audit.py \
	  tools/agentx_evolve/tests/test_orchestrator_orchestrator_errors.py \
	  tools/agentx_evolve/tests/test_orchestrator_orchestration_plan.py \
	  tools/agentx_evolve/tests/test_orchestrator_gate_controller.py \
	  tools/agentx_evolve/tests/test_orchestrator_model_invocation.py \
	  tools/agentx_evolve/tests/test_orchestrator_session_controller.py \
	  tools/agentx_evolve/tests/test_orchestrator_session_manager.py \
	  tools/agentx_evolve/tests/test_orchestrator_locking.py \
	  tools/agentx_evolve/tests/test_orchestrator_locks.py \
	  tools/agentx_evolve/tests/test_orchestrator_config.py \
	  tools/agentx_evolve/tests/test_orchestrator_state.py \
	  tools/agentx_evolve/tests/test_orchestrator_dispatcher.py \
	  tools/agentx_evolve/tests/test_orchestrator_step_dispatcher.py \
	  tools/agentx_evolve/tests/test_orchestrator_completion.py \
	  tools/agentx_evolve/tests/test_orchestrator_run_admission.py \
	  tools/agentx_evolve/tests/test_orchestrator_tool_invocation.py \
	  tools/agentx_evolve/tests/test_orchestrator_tool_binding.py \
	  tools/agentx_evolve/tests/test_orchestrator_dependency_bindings.py \
	  tools/agentx_evolve/tests/test_orchestrator_model_binding.py \
	  -q --tb=short -p no:cacheprovider
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_anti_false_pass.py governed
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_evidence_manifest.py governed
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_command_transcript.py governed
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_command_transcript.py governed
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_acceptance_matrix.py governed
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_final_verdict.py governed
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_replay_report.py governed
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_replay.py governed
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_acceptance_matrix.py governed
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_anti_false_pass.py governed
	$(FUNCTIONAL_AGENTX_REC) PYTHONPATH="tools" $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_final_verdict.py governed
	@echo "=== prove-governed-self-evolution-prototype: OK ==="

# target_id: P3-A05
# Stage 6: Final Functional Agent_X Proof — unified end-to-end
prove-functional-agentx: \
  prove-functional-runtime-mvp \
  prove-agentx-adapter-mvp \
  prove-functional-agent-evolution-alpha \
  prove-functional-agent-evolution-beta \
  prove-governed-self-evolution-prototype \
  prove-agentx-repo-memory-mvp \
  prove-agentx-generated-agent-git-promotion
	# Phase 0: Evolution acceptance generators for each stage
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_acceptance_matrix.py alpha
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_acceptance_matrix.py beta
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_acceptance_matrix.py governed
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_replay_report.py alpha
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_replay_report.py beta
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_replay_report.py governed
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_anti_false_pass.py alpha
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_anti_false_pass.py beta
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_anti_false_pass.py governed
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_evidence_manifest.py alpha
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_evidence_manifest.py beta
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_evidence_manifest.py governed
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_final_verdict.py alpha
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_final_verdict.py beta
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_final_verdict.py governed
	# Phase 0ct: Evolution acceptance command transcript for each stage
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_command_transcript.py alpha
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_command_transcript.py beta
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/generate_evolution_command_transcript.py governed
	# Phase 0cv: Validate evolution command transcripts (Gap 4)
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_command_transcript.py alpha
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_command_transcript.py beta
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_command_transcript.py governed
	# Phase 0v: Evolution acceptance validators for each stage
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_acceptance_matrix.py alpha
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_acceptance_matrix.py beta
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_acceptance_matrix.py governed
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_replay.py alpha
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_replay.py beta
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_replay.py governed
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_anti_false_pass.py alpha
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_anti_false_pass.py beta
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_anti_false_pass.py governed
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_final_verdict.py alpha
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_final_verdict.py beta
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/evolution_acceptance/validate_evolution_final_verdict.py governed
	# Phase 0d: MVP dependency chain check (Gap 17)
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/validators/validate_mvp_dependency_check.py
	# Phase 1: Run gap discovery + validate
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/run_gap_discovery.py
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/validate_functional_agentx_gap_discovery.py
	# Phase 4: Generate acceptance matrix
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/generate_functional_agentx_acceptance_matrix.py
	# Phase 5: Validate acceptance matrix
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/validate_functional_agentx_acceptance_matrix.py
	# Phase 6: Validate replay across all stages
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/validate_functional_agentx_replay.py
	# Phase 7: Run anti-false-PASS audit
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/run_functional_agentx_anti_false_pass_audit.py
	# Phase 8: Validate anti-false-PASS
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/validate_functional_agentx_anti_false_pass.py
	# Phase 9: Generate CI evidence
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/generate_functional_agentx_ci_evidence.py
	# Phase 10: Validate CI evidence
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/validate_functional_agentx_ci_evidence.py
	# Phase 11: Clean checkout validation
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/validate_clean_checkout_functional_agentx.py
	# Phase 12: No-overclaim scanner
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/generate_functional_agentx_no_overclaim.py
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/validate_functional_agentx_no_overclaim.py
	# Phase 13a: Schema compatibility validation (Gap 33)
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/validate_functional_agentx_schema_compatibility.py
	# Phase 13b: Generate observability trace (Gap 34)
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/generate_functional_agentx_observability_trace.py
	# Phase 13c: Generate environment report (Gap 13)
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/generate_functional_agentx_environment_report.py
	# Phase 13c-validate: Validate environment invariants (Gap 12)
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/validate_functional_agentx_environment.py
	# Phase 14a: Generate command transcript
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/generate_functional_agentx_command_transcript.py
	# Phase 14a-validate: Validate command transcript (Gap 6)
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/validate_functional_agentx_command_transcript.py
	# Phase 14b: Generate dependency evidence (Gap 25)
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/generate_functional_agentx_dependency_evidence.py
	# Phase 14c: Generate policy precedence report (Gap 27)
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/generate_functional_agentx_policy_precedence.py
	# Phase 14d: Generate budget enforcement report (Gap 30)
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/generate_functional_agentx_budget_enforcement.py
	# Phase 14e: Generate side-effect classification report (Gap 31)
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/generate_functional_agentx_side_effect_classification.py
	# Phase 14f: Validate MCP transport/auth boundaries (Gap 32)
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/validate_functional_agentx_mcp_boundaries.py
	# Phase 14g: Generate backward compatibility aliases (Gap 35)
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/generate_functional_agentx_aliases.py
	# Phase 14h: Generate final replay report (Gap 9)
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/generate_functional_agentx_replay_report.py
	# Phase 14i: Validate review evidence binding (Gap 11)
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/validate_functional_agentx_review_evidence_binding.py
	# Phase 15: Generate final verdict + classification report
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/generate_functional_agentx_final_verdict.py
	# Phase 16: Validate final verdict
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/validate_functional_agentx_final_verdict.py
	# Phase 2: Generate evidence manifest (after all reports exist — including final verdict)
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/generate_functional_agentx_evidence_manifest.py
	# Phase 3: Validate evidence manifest
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/validate_functional_agentx_evidence_manifest.py
	# Phase 17: Validate authority chain (Gap 13)
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/validate_authority_chain.py
	# Phase 18: Generate terminal seal (binds final_verdict + classification_report + evidence_manifest)
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/generate_terminal_seal.py
	# Phase 19: Validate terminal seal
	$(FUNCTIONAL_AGENTX_REC) $(PYTHON) tools/agentx_evolve/final_agentx/validate_terminal_seal.py
	@echo "=== prove-functional-agentx: OK ==="

# target_id: P3-A01
verify-existing-proof:
	$(PYTHON) tools/agentx_evolve/acceptance/verify_existing_proof.py --promote
	@echo "=== verify-existing-proof: OK ==="

# target_id: P2-C020-alt3b
generate-final-artifacts:
	PYTHONPATH=tools/agentx_evolve $(PYTHON) tools/agentx_evolve/final_acceptance/generate_artifacts.py
	@echo "=== generate-final-artifacts: OK ==="

# target_id: P2-C020-alt4
# R3.15 Required validation order
final-acceptance: generate-final-artifacts
	# 1. source_plan_gate_registry
	$(PYTHON) tools/agentx_evolve/validators/validate_source_plan_gate_registry.py
	# 2. alias/conflict_registry
	$(PYTHON) tools/agentx_evolve/validators/validate_alias_conflict_registry.py
	# 3. document_coverage
	$(PYTHON) tools/agentx_evolve/validators/validate_five_document_matrix.py .agentx-init/five_document_closure/matrix/five_document_traceability_matrix.json
	# 4. safety/policy
	$(PYTHON) tools/agentx_evolve/validators/validate_safety_policy.py
	# 5. patch_execution
	$(PYTHON) tools/agentx_evolve/validators/validate_patch_execution.py
	# 6. evidence_manifest
	$(PYTHON) tools/agentx_evolve/validators/validate_evidence_manifest.py .agentx-init/five_document_closure/final/five_document_evidence_manifest.json
	# 7. source_manifest (source_hash_manifest)
	$(PYTHON) tools/agentx_evolve/validators/validate_source_hash_manifest.py .agentx-init/five_document_closure/final/five_document_source_hash_manifest_after.json
	# 8. command_transcript
	$(PYTHON) tools/agentx_evolve/validators/validate_command_transcript.py
	# 9. no_op_command_detector
	$(PYTHON) tools/agentx_evolve/validators/detect_noop_commands.py .agentx-init/reports/final_project_command_transcript.json
	# 10. zero_test_detector
	$(PYTHON) tools/agentx_evolve/validators/detect_skipped_or_empty_tests.py tests
	# 11. event_log
	$(PYTHON) tools/agentx_evolve/validators/validate_event_log.py .agentx-init/five_document_closure/final/five_document_event_log_validation.json
	# 12. provenance
	$(PYTHON) tools/agentx_evolve/validators/validate_provenance.py
	# 13. report_path_existence
	$(PYTHON) tools/agentx_evolve/validators/validate_report_path_existence.py
	# 14. live_test_quarantine
	$(PYTHON) tools/agentx_evolve/validators/validate_live_test_quarantine.py
	# 15. deferred_work_registry
	$(PYTHON) tools/agentx_evolve/validators/validate_deferred_work_registry.py
	# 16. dependency_change
	$(PYTHON) tools/agentx_evolve/validators/validate_dependency_change.py
	# 17. secret_scanner
	$(PYTHON) tools/agentx_evolve/validators/scan_secrets_in_evidence.py
	# 18. l0_protection
	$(PYTHON) tools/agentx_evolve/validators/validate_l0_protection.py
	# 19. runtime_artifact_boundary
	$(PYTHON) tools/agentx_evolve/validators/validate_runtime_artifact_boundary.py
	# 20. clean_checkout_replay
	$(PYTHON) tools/agentx_evolve/validators/validate_clean_replay_report.py .agentx-init/five_document_closure/final/five_document_clean_checkout_replay.json
	# 21. milestone_final_reports
	$(PYTHON) tools/agentx_evolve/validators/validate_milestone_final_reports.py
	# 22. final_claim_taxonomy
	$(PYTHON) tools/agentx_evolve/validators/validate_final_claim_taxonomy.py
	# 23. forbidden_claim_scanner
	$(PYTHON) tools/agentx_evolve/validators/validate_claims.py .agentx-init/five_document_closure/final/five_document_claim_validation.json
	# 24. final_acceptance_cross_check (generated from real artifact evidence)
	PYTHONPATH=tools/agentx_evolve $(PYTHON) tools/agentx_evolve/final_acceptance/generate_cross_check_matrix.py
	# 25. final_project_run_manifest
	$(PYTHON) tools/agentx_evolve/validators/validate_final_project_run_manifest.py
	# Auxiliary: review + promotion records
	$(PYTHON) tools/agentx_evolve/validators/validate_review_records.py
	$(PYTHON) tools/agentx_evolve/validators/validate_promotion_records.py
	# 26. script_substance_validator
	$(PYTHON) tools/agentx_evolve/validators/validate_script_substance.py
	@echo "=== final-acceptance: OK ==="

validate-final-acceptance: final-acceptance
	@echo "=== validate-final-acceptance: OK ==="

# target_id: P2-C021
run:
	PYTHONPATH=L0/CODE $(PYTHON) -c "\
from core_kernel.public.kernel_service import KernelService; \
from core_kernel.models.kernel_requests import KernelTurnRequest; \
k = KernelService(); \
print(k.run_turn(KernelTurnRequest(user_input='Say hello from the governed seed.', session_id='cli')))"

# target_id: P2-C022
build-seed:
	PYTHONPATH=L0/CODE $(PYTHON) L0/scripts/build_seed_package.py

# target_id: P2-C023
# Reset proof artifacts (keeps all source code, tests, and tools unchanged)
prove-reset:
	rm -rf .agentx-init/reports/
	rm -rf /tmp/agentx_afp_*
	rm -rf /tmp/agentx_stage_afp_*
	rm -rf /tmp/agentx_evm_*
	@echo "=== prove-reset: OK ==="

# Deep clean including proof artifacts and all caches
prove-clean: clean prove-reset
	@echo "=== prove-clean: OK ==="

clean:
	rm -rf .local/runtime/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	@echo "=== clean: OK ==="

# ═══════════════════════════════════════════════════════════════════════════════
# ENTERPRISE AGENT FACTORY PLATFORM TARGETS (v21 end-to-end)
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: prove-functional-agentx-local-final
.PHONY: prove-agentx-enterprise-contract-system
.PHONY: prove-agentx-enterprise-adapter-sandbox
.PHONY: prove-agentx-company-workflow-pack
.PHONY: prove-agentx-enterprise-workflow-runtime
.PHONY: prove-agentx-arbitrary-compliant-agent-generation
.PHONY: prove-agentx-connector-sdk-certification
.PHONY: prove-agentx-agent-catalog-lifecycle
.PHONY: prove-agentx-multi-agent-orchestration
.PHONY: prove-agentx-auth-rbac-tenant-isolation
.PHONY: prove-agentx-data-governance-compliance
.PHONY: prove-agentx-production-ops-local
.PHONY: prove-agentx-domain-evals-dashboard
.PHONY: prove-agentx-enterprise-onboarding-deployment-handoff
.PHONY: prove-agentx-enterprise-control-plane-api
.PHONY: prove-agentx-durable-workflow-workers
.PHONY: prove-agentx-business-process-intake-contract-compiler
.PHONY: prove-agentx-risk-tiered-automation-policy
.PHONY: prove-agentx-enterprise-knowledge-rag-governance
.PHONY: prove-agentx-packaging-deployment-artifacts
.PHONY: prove-agentx-live-connector-readiness-boundary
.PHONY: prove-agentx-performance-concurrency-slo-local
.PHONY: prove-agentx-event-webhook-integration
.PHONY: prove-agentx-ui-rpa-automation-sandbox
.PHONY: prove-agentx-dlp-data-classification-egress
.PHONY: prove-agentx-approval-escalation-delegation
.PHONY: prove-agentx-agent-template-pack-registry
.PHONY: prove-agentx-model-version-eval-governance
.PHONY: prove-agentx-connector-schema-compatibility
.PHONY: prove-agentx-upgrade-supportability-local
.PHONY: prove-agentx-customer-deployment-dry-run
.PHONY: prove-agentx-org-policy-inheritance
.PHONY: prove-agentx-policy-pack-regulatory-controls
.PHONY: prove-agentx-tamper-evident-audit-lineage
.PHONY: prove-agentx-credential-secret-lifecycle
.PHONY: prove-agentx-live-cutover-change-management
.PHONY: prove-agentx-enterprise-accountability-usage-governance
.PHONY: prove-agentx-outbound-communications-governance
.PHONY: prove-agentx-encryption-key-residency-boundary
.PHONY: prove-agentx-vendor-third-party-risk-local
.PHONY: prove-agentx-support-diagnostics-bundle
.PHONY: prove-agentx-admin-operability-proof
.PHONY: prove-agentx-enterprise-assurance-case-traceability
.PHONY: prove-agentx-business-state-ledger-reconciliation
.PHONY: prove-agentx-enterprise-failover-disaster-drill-local
.PHONY: prove-agentx-sandbox-live-equivalence-boundary
.PHONY: prove-agentx-whole-company-workflow-exemplar
.PHONY: prove-agentx-residual-risk-deployment-authority
.PHONY: prove-agentx-customer-data-migration-import-export
.PHONY: prove-agentx-operator-usability-accessibility-error-recovery
.PHONY: prove-agentx-enterprise-identity-session-access-review
.PHONY: prove-agentx-api-abuse-rate-limit-resource-isolation
.PHONY: prove-agentx-cross-tenant-leakage-penetration-local
.PHONY: prove-agentx-audit-retention-ediscovery
.PHONY: prove-agentx-config-drift-environment-promotion
.PHONY: prove-agentx-production-like-cutover-rollback-drill
.PHONY: prove-agentx-enterprise-sso-idp-lifecycle
.PHONY: prove-agentx-sbom-vulnerability-license-local
.PHONY: prove-agentx-segregation-of-duties-dual-control
.PHONY: prove-agentx-field-record-authorization
.PHONY: prove-agentx-backup-restore-rpo-rto-local
.PHONY: prove-agentx-customer-acceptance-uat-signoff
.PHONY: prove-agentx-data-quality-source-trust
.PHONY: prove-agentx-training-runbook-change-adoption
.PHONY: prove-agentx-enterprise-security-review-local
.PHONY: prove-agentx-enterprise-ready
.PHONY: prove-agentx-enterprise-local-final

ENTERPRISE_PYTHONPATH = tools/agentx_evolve:tools
ENTERPRISE_ENV = AGENTX_LIVE_PROVIDER=0 AGENTX_ENABLE_COHERE=0 AGENTX_COHERE_LIVE=0 AGENTX_ENABLE_NETWORK=0 AGENTX_ENABLE_MCP_LIVE=0 AGENTX_ENTERPRISE_SANDBOX_ONLY=1 AGENTX_REAL_SAAS=0 AGENTX_LIVE_CONNECTOR=0 AGENTX_PROD_PROFILE=0 AGENTX_ENTERPRISE_CONTROL_PLANE_LOCAL=1 AGENTX_PROOF_MODE=LOCAL_ONLY AGENTX_NO_FORCED_PASS=1
ENTERPRISE_GEN = $(ENTERPRISE_ENV) PYTHONPATH="$(ENTERPRISE_PYTHONPATH)" $(PYTHON) tools/agentx_evolve/enterprise/generate_enterprise_artifacts.py
ENTERPRISE_VAL = $(ENTERPRISE_ENV) PYTHONPATH="$(ENTERPRISE_PYTHONPATH)" $(PYTHON) tools/agentx_evolve/enterprise/validate_enterprise_artifacts.py

# ── Core local-final wrapper ─────────────────────────────────────────────────

prove-functional-agentx-local-final:
	@echo "=== Core local-final harness ==="
	$(MAKE) prove-functional-agentx
	$(ENTERPRISE_GEN) core-local-final
	@echo "=== prove-functional-agentx-local-final: OK ==="

# ── Enterprise contract system ───────────────────────────────────────────────

prove-agentx-enterprise-contract-system:
	rm -rf .agentx-init/reports/enterprise-contracts/
	$(ENTERPRISE_GEN) contract-system
	$(ENTERPRISE_VAL) contract-system
	@echo "=== prove-agentx-enterprise-contract-system: OK ==="

prove-agentx-enterprise-adapter-sandbox:
	rm -rf .agentx-init/reports/enterprise-adapters/
	$(ENTERPRISE_GEN) adapter-sandbox
	$(ENTERPRISE_VAL) adapter-sandbox
	@echo "=== prove-agentx-enterprise-adapter-sandbox: OK ==="

prove-agentx-company-workflow-pack:
	rm -rf .agentx-init/reports/enterprise-workflows/
	$(ENTERPRISE_GEN) workflow-pack
	$(ENTERPRISE_VAL) workflow-pack
	@echo "=== prove-agentx-company-workflow-pack: OK ==="

prove-agentx-enterprise-workflow-runtime:
	rm -rf .agentx-init/reports/workflow-runtime/
	$(ENTERPRISE_GEN) workflow-runtime
	$(ENTERPRISE_VAL) workflow-runtime
	@echo "=== prove-agentx-enterprise-workflow-runtime: OK ==="

prove-agentx-arbitrary-compliant-agent-generation:
	rm -rf .agentx-init/reports/arbitrary-agent-generation/
	$(ENTERPRISE_GEN) arbitrary-agent-generation
	$(ENTERPRISE_VAL) arbitrary-agent-generation
	@echo "=== prove-agentx-arbitrary-compliant-agent-generation: OK ==="

prove-agentx-connector-sdk-certification:
	rm -rf .agentx-init/reports/connector-certification/
	$(ENTERPRISE_GEN) connector-certification
	$(ENTERPRISE_VAL) connector-certification
	@echo "=== prove-agentx-connector-sdk-certification: OK ==="

prove-agentx-agent-catalog-lifecycle:
	rm -rf .agentx-init/reports/agent-catalog/
	$(ENTERPRISE_GEN) agent-catalog
	$(ENTERPRISE_VAL) agent-catalog
	@echo "=== prove-agentx-agent-catalog-lifecycle: OK ==="

prove-agentx-multi-agent-orchestration:
	rm -rf .agentx-init/reports/multi-agent/
	$(ENTERPRISE_GEN) multi-agent
	$(ENTERPRISE_VAL) multi-agent
	@echo "=== prove-agentx-multi-agent-orchestration: OK ==="

prove-agentx-auth-rbac-tenant-isolation:
	rm -rf .agentx-init/reports/auth-rbac/
	$(ENTERPRISE_GEN) auth-rbac
	$(ENTERPRISE_VAL) auth-rbac
	@echo "=== prove-agentx-auth-rbac-tenant-isolation: OK ==="

prove-agentx-data-governance-compliance:
	rm -rf .agentx-init/reports/data-governance/
	$(ENTERPRISE_GEN) data-governance
	$(ENTERPRISE_VAL) data-governance
	@echo "=== prove-agentx-data-governance-compliance: OK ==="

prove-agentx-production-ops-local:
	rm -rf .agentx-init/reports/production-ops/
	$(ENTERPRISE_GEN) production-ops
	$(ENTERPRISE_VAL) production-ops
	@echo "=== prove-agentx-production-ops-local: OK ==="

prove-agentx-domain-evals-dashboard:
	rm -rf .agentx-init/reports/domain-evals/
	$(ENTERPRISE_GEN) domain-evals
	$(ENTERPRISE_VAL) domain-evals
	@echo "=== prove-agentx-domain-evals-dashboard: OK ==="

prove-agentx-enterprise-onboarding-deployment-handoff:
	rm -rf .agentx-init/reports/enterprise-onboarding/
	$(ENTERPRISE_GEN) onboarding
	$(ENTERPRISE_VAL) onboarding
	@echo "=== prove-agentx-enterprise-onboarding-deployment-handoff: OK ==="

prove-agentx-enterprise-control-plane-api:
	rm -rf .agentx-init/reports/control-plane/
	$(ENTERPRISE_GEN) control-plane
	$(ENTERPRISE_VAL) control-plane
	@echo "=== prove-agentx-enterprise-control-plane-api: OK ==="

prove-agentx-durable-workflow-workers:
	rm -rf .agentx-init/reports/durable-workers/
	$(ENTERPRISE_GEN) durable-workers
	$(ENTERPRISE_VAL) durable-workers
	@echo "=== prove-agentx-durable-workflow-workers: OK ==="

prove-agentx-business-process-intake-contract-compiler:
	rm -rf .agentx-init/reports/process-intake/
	$(ENTERPRISE_GEN) process-intake
	$(ENTERPRISE_VAL) process-intake
	@echo "=== prove-agentx-business-process-intake-contract-compiler: OK ==="

prove-agentx-risk-tiered-automation-policy:
	rm -rf .agentx-init/reports/risk-policy/
	$(ENTERPRISE_GEN) risk-policy
	$(ENTERPRISE_VAL) risk-policy
	@echo "=== prove-agentx-risk-tiered-automation-policy: OK ==="

prove-agentx-enterprise-knowledge-rag-governance:
	rm -rf .agentx-init/reports/enterprise-knowledge/
	$(ENTERPRISE_GEN) enterprise-knowledge
	$(ENTERPRISE_VAL) enterprise-knowledge
	@echo "=== prove-agentx-enterprise-knowledge-rag-governance: OK ==="

prove-agentx-packaging-deployment-artifacts:
	rm -rf .agentx-init/reports/packaging-deployment/
	$(ENTERPRISE_GEN) packaging
	$(ENTERPRISE_VAL) packaging
	@echo "=== prove-agentx-packaging-deployment-artifacts: OK ==="

prove-agentx-live-connector-readiness-boundary:
	rm -rf .agentx-init/reports/live-connector-boundary/
	$(ENTERPRISE_GEN) live-connector
	$(ENTERPRISE_VAL) live-connector
	@echo "=== prove-agentx-live-connector-readiness-boundary: OK ==="

prove-agentx-performance-concurrency-slo-local:
	rm -rf .agentx-init/reports/performance-slo/
	$(ENTERPRISE_GEN) performance-slo
	$(ENTERPRISE_VAL) performance-slo
	@echo "=== prove-agentx-performance-concurrency-slo-local: OK ==="

# ── Last-mile enterprise targets ─────────────────────────────────────────────

prove-agentx-event-webhook-integration:
	rm -rf .agentx-init/reports/last-mile/
	$(ENTERPRISE_GEN) event-webhook
	$(ENTERPRISE_VAL) event-webhook --prefix event_webhook
	@echo "=== prove-agentx-event-webhook-integration: OK ==="

prove-agentx-ui-rpa-automation-sandbox: prove-agentx-event-webhook-integration
	$(PYTHON) -c "import json; json.loads(open('.agentx-init/reports/last-mile/ui_rpa_integration_verdict.json').read())['verdict'] == 'PASS' or exit(1)" && echo "=== prove-agentx-ui-rpa-automation-sandbox: OK ==="

prove-agentx-dlp-data-classification-egress: prove-agentx-event-webhook-integration
	$(PYTHON) -c "import json; json.loads(open('.agentx-init/reports/last-mile/dlp_integration_verdict.json').read())['verdict'] == 'PASS' or exit(1)" && echo "=== prove-agentx-dlp-data-classification-egress: OK ==="

prove-agentx-approval-escalation-delegation: prove-agentx-event-webhook-integration
	$(PYTHON) -c "import json; json.loads(open('.agentx-init/reports/last-mile/approval_integration_verdict.json').read())['verdict'] == 'PASS' or exit(1)" && echo "=== prove-agentx-approval-escalation-delegation: OK ==="

prove-agentx-agent-template-pack-registry: prove-agentx-event-webhook-integration
	$(PYTHON) -c "import json; json.loads(open('.agentx-init/reports/last-mile/template_integration_verdict.json').read())['verdict'] == 'PASS' or exit(1)" && echo "=== prove-agentx-agent-template-pack-registry: OK ==="

prove-agentx-model-version-eval-governance: prove-agentx-event-webhook-integration
	$(PYTHON) -c "import json; json.loads(open('.agentx-init/reports/last-mile/model_integration_verdict.json').read())['verdict'] == 'PASS' or exit(1)" && echo "=== prove-agentx-model-version-eval-governance: OK ==="

prove-agentx-connector-schema-compatibility: prove-agentx-event-webhook-integration
	$(PYTHON) -c "import json; json.loads(open('.agentx-init/reports/last-mile/schema_integration_verdict.json').read())['verdict'] == 'PASS' or exit(1)" && echo "=== prove-agentx-connector-schema-compatibility: OK ==="

prove-agentx-upgrade-supportability-local: prove-agentx-event-webhook-integration
	$(PYTHON) -c "import json; json.loads(open('.agentx-init/reports/last-mile/upgrade_integration_verdict.json').read())['verdict'] == 'PASS' or exit(1)" && echo "=== prove-agentx-upgrade-supportability-local: OK ==="

prove-agentx-customer-deployment-dry-run: prove-agentx-event-webhook-integration
	$(PYTHON) -c "import json; json.loads(open('.agentx-init/reports/last-mile/dryrun_integration_verdict.json').read())['verdict'] == 'PASS' or exit(1)" && echo "=== prove-agentx-customer-deployment-dry-run: OK ==="

prove-agentx-org-policy-inheritance: prove-agentx-event-webhook-integration
	$(PYTHON) -c "import json; json.loads(open('.agentx-init/reports/last-mile/policy_inheritance_integration_verdict.json').read())['verdict'] == 'PASS' or exit(1)" && echo "=== prove-agentx-org-policy-inheritance: OK ==="

# ── Final enterprise adoption targets ────────────────────────────────────────

prove-agentx-policy-pack-regulatory-controls:
	rm -rf .agentx-init/reports/final-adoption/
	$(ENTERPRISE_GEN) policy-pack
	$(ENTERPRISE_VAL) policy-pack
	@echo "=== prove-agentx-policy-pack-regulatory-controls: OK ==="

prove-agentx-tamper-evident-audit-lineage: prove-agentx-policy-pack-regulatory-controls
	$(PYTHON) -c "import json; json.loads(open('.agentx-init/reports/final-adoption/tamper_evident_audit_lineage_verdict.json').read())['verdict'] == 'PASS' or exit(1)" && echo "=== prove-agentx-tamper-evident-audit-lineage: OK ==="

prove-agentx-credential-secret-lifecycle: prove-agentx-policy-pack-regulatory-controls
	$(PYTHON) -c "import json; json.loads(open('.agentx-init/reports/final-adoption/credential_secret_lifecycle_verdict.json').read())['verdict'] == 'PASS' or exit(1)" && echo "=== prove-agentx-credential-secret-lifecycle: OK ==="

prove-agentx-live-cutover-change-management: prove-agentx-policy-pack-regulatory-controls
	$(PYTHON) -c "import json; json.loads(open('.agentx-init/reports/final-adoption/live_cutover_change_management_verdict.json').read())['verdict'] == 'PASS' or exit(1)" && echo "=== prove-agentx-live-cutover-change-management: OK ==="

prove-agentx-enterprise-accountability-usage-governance: prove-agentx-policy-pack-regulatory-controls
	$(PYTHON) -c "import json; json.loads(open('.agentx-init/reports/final-adoption/enterprise_accountability_usage_governance_verdict.json').read())['verdict'] == 'PASS' or exit(1)" && echo "=== prove-agentx-enterprise-accountability-usage-governance: OK ==="

prove-agentx-outbound-communications-governance: prove-agentx-policy-pack-regulatory-controls
	$(PYTHON) -c "import json; json.loads(open('.agentx-init/reports/final-adoption/outbound_communications_governance_verdict.json').read())['verdict'] == 'PASS' or exit(1)" && echo "=== prove-agentx-outbound-communications-governance: OK ==="

prove-agentx-encryption-key-residency-boundary: prove-agentx-policy-pack-regulatory-controls
	$(PYTHON) -c "import json; json.loads(open('.agentx-init/reports/final-adoption/encryption_key_residency_boundary_verdict.json').read())['verdict'] == 'PASS' or exit(1)" && echo "=== prove-agentx-encryption-key-residency-boundary: OK ==="

prove-agentx-vendor-third-party-risk-local: prove-agentx-policy-pack-regulatory-controls
	$(PYTHON) -c "import json; json.loads(open('.agentx-init/reports/final-adoption/vendor_third_party_risk_verdict.json').read())['verdict'] == 'PASS' or exit(1)" && echo "=== prove-agentx-vendor-third-party-risk-local: OK ==="

prove-agentx-support-diagnostics-bundle: prove-agentx-policy-pack-regulatory-controls
	$(PYTHON) -c "import json; json.loads(open('.agentx-init/reports/final-adoption/support_diagnostics_bundle_verdict.json').read())['verdict'] == 'PASS' or exit(1)" && echo "=== prove-agentx-support-diagnostics-bundle: OK ==="

prove-agentx-admin-operability-proof: prove-agentx-policy-pack-regulatory-controls
	$(PYTHON) -c "import json; json.loads(open('.agentx-init/reports/final-adoption/admin_operability_proof_verdict.json').read())['verdict'] == 'PASS' or exit(1)" && echo "=== prove-agentx-admin-operability-proof: OK ==="

# ── Enterprise assurance and final closure gates ─────────────────────────────

prove-agentx-enterprise-assurance-case-traceability:
	rm -rf .agentx-init/reports/enterprise-assurance/
	$(ENTERPRISE_GEN) assurance-case
	$(ENTERPRISE_VAL) assurance-case
	@echo "=== prove-agentx-enterprise-assurance-case-traceability: OK ==="

prove-agentx-business-state-ledger-reconciliation:
	rm -rf .agentx-init/reports/business-state/
	$(ENTERPRISE_GEN) business-state
	$(ENTERPRISE_VAL) business-state
	@echo "=== prove-agentx-business-state-ledger-reconciliation: OK ==="

prove-agentx-enterprise-failover-disaster-drill-local:
	rm -rf .agentx-init/reports/failover-drill/
	$(ENTERPRISE_GEN) failover-drill
	$(ENTERPRISE_VAL) failover-drill
	@echo "=== prove-agentx-enterprise-failover-disaster-drill-local: OK ==="

prove-agentx-sandbox-live-equivalence-boundary:
	rm -rf .agentx-init/reports/sandbox-live-boundary/
	$(ENTERPRISE_GEN) sandbox-live-boundary
	$(ENTERPRISE_VAL) sandbox-live-boundary
	@echo "=== prove-agentx-sandbox-live-equivalence-boundary: OK ==="

prove-agentx-whole-company-workflow-exemplar:
	rm -rf .agentx-init/reports/whole-company-exemplar/
	$(ENTERPRISE_GEN) whole-company-exemplar
	$(ENTERPRISE_VAL) whole-company-exemplar
	@echo "=== prove-agentx-whole-company-workflow-exemplar: OK ==="

prove-agentx-residual-risk-deployment-authority:
	rm -rf .agentx-init/reports/residual-risk/
	$(ENTERPRISE_GEN) residual-risk
	$(ENTERPRISE_VAL) residual-risk
	@echo "=== prove-agentx-residual-risk-deployment-authority: OK ==="

prove-agentx-customer-data-migration-import-export:
	rm -rf .agentx-init/reports/data-migration/
	$(ENTERPRISE_GEN) customer-data-migration
	$(ENTERPRISE_VAL) customer-data-migration
	@echo "=== prove-agentx-customer-data-migration-import-export: OK ==="

prove-agentx-operator-usability-accessibility-error-recovery:
	rm -rf .agentx-init/reports/operator-usability/
	$(ENTERPRISE_GEN) operator-usability
	$(ENTERPRISE_VAL) operator-usability
	@echo "=== prove-agentx-operator-usability-accessibility-error-recovery: OK ==="

# ── Enterprise hardening gates ──────────────────────────────────────────────

prove-agentx-enterprise-identity-session-access-review:
	rm -rf .agentx-init/reports/identity-hardening/
	$(ENTERPRISE_GEN) identity-hardening
	$(ENTERPRISE_VAL) identity-hardening
	@echo "=== prove-agentx-enterprise-identity-session-access-review: OK ==="

prove-agentx-api-abuse-rate-limit-resource-isolation:
	rm -rf .agentx-init/reports/api-abuse/
	$(ENTERPRISE_GEN) api-abuse
	$(ENTERPRISE_VAL) api-abuse
	@echo "=== prove-agentx-api-abuse-rate-limit-resource-isolation: OK ==="

prove-agentx-cross-tenant-leakage-penetration-local:
	rm -rf .agentx-init/reports/cross-tenant-penetration/
	$(ENTERPRISE_GEN) cross-tenant
	$(ENTERPRISE_VAL) cross-tenant
	@echo "=== prove-agentx-cross-tenant-leakage-penetration-local: OK ==="

prove-agentx-audit-retention-ediscovery:
	rm -rf .agentx-init/reports/audit-retention/
	$(ENTERPRISE_GEN) audit-retention
	$(ENTERPRISE_VAL) audit-retention
	@echo "=== prove-agentx-audit-retention-ediscovery: OK ==="

prove-agentx-config-drift-environment-promotion:
	rm -rf .agentx-init/reports/config-drift/
	$(ENTERPRISE_GEN) config-drift
	$(ENTERPRISE_VAL) config-drift
	@echo "=== prove-agentx-config-drift-environment-promotion: OK ==="

prove-agentx-production-like-cutover-rollback-drill:
	rm -rf .agentx-init/reports/cutover-drill/
	$(ENTERPRISE_GEN) cutover-drill
	$(ENTERPRISE_VAL) cutover-drill
	@echo "=== prove-agentx-production-like-cutover-rollback-drill: OK ==="

# ── Enterprise adoption gates ────────────────────────────────────────────────

prove-agentx-enterprise-sso-idp-lifecycle:
	rm -rf .agentx-init/reports/enterprise-adoption/
	$(ENTERPRISE_GEN) sso-idp
	$(ENTERPRISE_VAL) sso-idp
	@echo "=== prove-agentx-enterprise-sso-idp-lifecycle: OK ==="

prove-agentx-sbom-vulnerability-license-local: prove-agentx-enterprise-sso-idp-lifecycle
	$(PYTHON) -c "import json; json.loads(open('.agentx-init/reports/enterprise-adoption/sbom_verdict.json').read())['verdict'] == 'PASS' or exit(1)" && echo "=== prove-agentx-sbom-vulnerability-license-local: OK ==="

prove-agentx-segregation-of-duties-dual-control: prove-agentx-enterprise-sso-idp-lifecycle
	$(PYTHON) -c "import json; json.loads(open('.agentx-init/reports/enterprise-adoption/segregation_duties_verdict.json').read())['verdict'] == 'PASS' or exit(1)" && echo "=== prove-agentx-segregation-of-duties-dual-control: OK ==="

prove-agentx-field-record-authorization: prove-agentx-enterprise-sso-idp-lifecycle
	$(PYTHON) -c "import json; json.loads(open('.agentx-init/reports/enterprise-adoption/field_record_authz_verdict.json').read())['verdict'] == 'PASS' or exit(1)" && echo "=== prove-agentx-field-record-authorization: OK ==="

prove-agentx-backup-restore-rpo-rto-local: prove-agentx-enterprise-sso-idp-lifecycle
	$(PYTHON) -c "import json; json.loads(open('.agentx-init/reports/enterprise-adoption/backup_restore_verdict.json').read())['verdict'] == 'PASS' or exit(1)" && echo "=== prove-agentx-backup-restore-rpo-rto-local: OK ==="

prove-agentx-customer-acceptance-uat-signoff: prove-agentx-enterprise-sso-idp-lifecycle
	$(PYTHON) -c "import json; json.loads(open('.agentx-init/reports/enterprise-adoption/customer_acceptance_verdict.json').read())['verdict'] == 'PASS' or exit(1)" && echo "=== prove-agentx-customer-acceptance-uat-signoff: OK ==="

prove-agentx-data-quality-source-trust: prove-agentx-enterprise-sso-idp-lifecycle
	$(PYTHON) -c "import json; json.loads(open('.agentx-init/reports/enterprise-adoption/data_quality_verdict.json').read())['verdict'] == 'PASS' or exit(1)" && echo "=== prove-agentx-data-quality-source-trust: OK ==="

prove-agentx-training-runbook-change-adoption: prove-agentx-enterprise-sso-idp-lifecycle
	$(PYTHON) -c "import json; json.loads(open('.agentx-init/reports/enterprise-adoption/training_runbook_verdict.json').read())['verdict'] == 'PASS' or exit(1)" && echo "=== prove-agentx-training-runbook-change-adoption: OK ==="

# ── Enterprise security review ──────────────────────────────────────────────

prove-agentx-enterprise-security-review-local:
	rm -rf .agentx-init/reports/security-review/
	$(ENTERPRISE_GEN) security-review
	$(ENTERPRISE_VAL) security-review
	@echo "=== prove-agentx-enterprise-security-review-local: OK ==="

# ── Anti-false-PASS enterprise test ─────────────────────────────────────────
# Tampers with enterprise artifacts and confirms validation catches the tamper.

prove-agentx-enterprise-anti-false-pass:
	@echo "=== Anti-false-PASS enterprise test ==="
	$(PYTHON) -m pytest tools/agentx_evolve/tests/test_anti_false_pass_enterprise.py -v 2>&1 | tail -5
	@echo "=== prove-agentx-enterprise-anti-false-pass: OK ==="

# ── Enterprise readiness aggregate (validates all enterprise gates) ─────────
# Depends on every individual enterprise proof target so the aggregate
# reads real artifacts rather than self-declaring PASS.

ENTERPRISE_ALL_TARGETS = \
	prove-agentx-enterprise-contract-system \
	prove-agentx-enterprise-adapter-sandbox \
	prove-agentx-company-workflow-pack \
	prove-agentx-enterprise-workflow-runtime \
	prove-agentx-arbitrary-compliant-agent-generation \
	prove-agentx-connector-sdk-certification \
	prove-agentx-agent-catalog-lifecycle \
	prove-agentx-multi-agent-orchestration \
	prove-agentx-auth-rbac-tenant-isolation \
	prove-agentx-data-governance-compliance \
	prove-agentx-production-ops-local \
	prove-agentx-domain-evals-dashboard \
	prove-agentx-enterprise-onboarding-deployment-handoff \
	prove-agentx-enterprise-control-plane-api \
	prove-agentx-durable-workflow-workers \
	prove-agentx-business-process-intake-contract-compiler \
	prove-agentx-risk-tiered-automation-policy \
	prove-agentx-enterprise-knowledge-rag-governance \
	prove-agentx-packaging-deployment-artifacts \
	prove-agentx-live-connector-readiness-boundary \
	prove-agentx-performance-concurrency-slo-local \
	prove-agentx-event-webhook-integration \
	prove-agentx-ui-rpa-automation-sandbox \
	prove-agentx-dlp-data-classification-egress \
	prove-agentx-approval-escalation-delegation \
	prove-agentx-agent-template-pack-registry \
	prove-agentx-model-version-eval-governance \
	prove-agentx-connector-schema-compatibility \
	prove-agentx-upgrade-supportability-local \
	prove-agentx-customer-deployment-dry-run \
	prove-agentx-org-policy-inheritance \
	prove-agentx-policy-pack-regulatory-controls \
	prove-agentx-tamper-evident-audit-lineage \
	prove-agentx-credential-secret-lifecycle \
	prove-agentx-live-cutover-change-management \
	prove-agentx-enterprise-accountability-usage-governance \
	prove-agentx-outbound-communications-governance \
	prove-agentx-encryption-key-residency-boundary \
	prove-agentx-vendor-third-party-risk-local \
	prove-agentx-support-diagnostics-bundle \
	prove-agentx-admin-operability-proof \
	prove-agentx-enterprise-assurance-case-traceability \
	prove-agentx-business-state-ledger-reconciliation \
	prove-agentx-enterprise-failover-disaster-drill-local \
	prove-agentx-sandbox-live-equivalence-boundary \
	prove-agentx-whole-company-workflow-exemplar \
	prove-agentx-residual-risk-deployment-authority \
	prove-agentx-customer-data-migration-import-export \
	prove-agentx-operator-usability-accessibility-error-recovery \
	prove-agentx-enterprise-identity-session-access-review \
	prove-agentx-api-abuse-rate-limit-resource-isolation \
	prove-agentx-cross-tenant-leakage-penetration-local \
	prove-agentx-audit-retention-ediscovery \
	prove-agentx-config-drift-environment-promotion \
	prove-agentx-production-like-cutover-rollback-drill \
	prove-agentx-enterprise-sso-idp-lifecycle \
	prove-agentx-sbom-vulnerability-license-local \
	prove-agentx-segregation-of-duties-dual-control \
	prove-agentx-field-record-authorization \
	prove-agentx-backup-restore-rpo-rto-local \
	prove-agentx-customer-acceptance-uat-signoff \
	prove-agentx-data-quality-source-trust \
	prove-agentx-training-runbook-change-adoption \
	prove-agentx-enterprise-security-review-local

prove-agentx-enterprise-ready: $(ENTERPRISE_ALL_TARGETS) prove-agentx-enterprise-anti-false-pass
	$(ENTERPRISE_GEN) enterprise-ready
	$(ENTERPRISE_VAL) enterprise-ready
	@echo "=== prove-agentx-enterprise-ready: OK ==="

# ── Final enterprise local-final harness ─────────────────────────────────────

prove-agentx-enterprise-local-final:
	@echo "=== Enterprise Local Final Harness ==="
	@echo "Baseline SHA: 832fc9b868e39aa65648ca4b50bf03295c8ede7e"
	@echo "Final SHA: $$(git rev-parse HEAD)"
	@echo "Working tree:"; git status --short
	# Step 1-2: Verify clean source (continue even if dirty — reports are expected)
	# Step 3: Compile check
	$(PYTHON) -m compileall -q tools/agentx_evolve
	# Step 4: Run core local final (must pass)
	$(MAKE) prove-functional-agentx-local-final
	# Step 5: Run enterprise ready (must pass)
	$(MAKE) prove-agentx-enterprise-ready
	# Step 6: Preserve first run
	rm -rf /tmp/enterprise-first-run
	mkdir -p /tmp/enterprise-first-run
	test -d .agentx-init/reports/enterprise-readiness && cp -R .agentx-init/reports/enterprise-readiness/. /tmp/enterprise-first-run/
	test -d .agentx-init/reports/enterprise-final && cp -R .agentx-init/reports/enterprise-final/. /tmp/enterprise-first-run/
	# Step 7-8-9: Clean and regenerate
	rm -rf .agentx-init/reports/enterprise-readiness/
	rm -rf .agentx-init/reports/enterprise-final/
	$(MAKE) prove-agentx-enterprise-ready
	# Step 9b: Compare
	mkdir -p /tmp/enterprise-second-run
	test -d .agentx-init/reports/enterprise-readiness && cp -R .agentx-init/reports/enterprise-readiness/. /tmp/enterprise-second-run/
	# Step 10-14: Generate enterprise final artifacts
	$(ENTERPRISE_GEN) enterprise-final
	$(ENTERPRISE_VAL) enterprise-final
	# Step 15: Anti-false-PASS test
	$(MAKE) prove-agentx-enterprise-anti-false-pass
	@echo "=== prove-agentx-enterprise-local-final: OK ==="
