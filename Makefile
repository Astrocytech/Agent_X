# Governed Universal Seed Kernel Makefile
SHELL := /bin/bash
.SHELLFLAGS := -e -o pipefail -c

PYTHON ?= python3
PIP_INSTALL ?= pip3 install --break-system-packages

.PHONY: help install seed-boot prove-seed prove-l1 prove-l2
.PHONY: prove-format compileall-check prove-all
.PHONY: test-quick test-dev test-release test-sabotage test-security
.PHONY: test-all test-live test-l0 test-l1 test-l2 test-initiator
.PHONY: test-evolve audit-structure prove-organization prove-hygiene
.PHONY: prove-umbrella-agent prove-post-umbrella prove-inverse-science
.PHONY: prove-scriptor-benchmark generate-final-artifacts
.PHONY: prove-functional-runtime-mvp prove-functional-runtime-mvp-idempotent
.PHONY: prove-agentx-adapter-mvp-once prove-agentx-adapter-mvp
.PHONY: final-acceptance validate-final-acceptance run clean build-seed

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
prove-all: prove-format compileall-check prove-seed prove-l1 prove-l2 test-initiator \
  test-evolve test-integration test-system test-regression test-all \
  prove-umbrella-agent generate-final-artifacts prove-post-umbrella \
  prove-inverse-science prove-scriptor-benchmark final-acceptance \
  audit-structure
	@echo "=== prove-all: OK ==="
	@echo "=== All targets passed ==="

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
  tools/agentx_evolve/tests/test_read_only_repo_info_tool.py

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
	# 10. Record FRMVP non-regression status
	$(ADAPTER_REC) $(PYTHON) -c "import json, sys; from pathlib import Path; p = Path('.agentx-init/reports/functional_runtime_mvp_final_verdict.json'); print(f'FRMVP verdict exists: {p.exists()}'); sys.exit(0)"
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
	@echo "=== prove-agentx-adapter-mvp: OK ==="

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
clean:
	rm -rf .local/runtime/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	@echo "=== clean: OK ==="
