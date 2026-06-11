# Governed Universal Seed Kernel Makefile

PYTHON ?= python3
PIP_INSTALL ?= pip3 install --break-system-packages

.PHONY: help install seed-boot prove-seed prove-l1 prove-l2
.PHONY: prove-format compileall-check prove-all
.PHONY: test-quick test-dev test-release test-sabotage test-security
.PHONY: test-all test-live test-l0 test-l1 test-l2 test-initiator
.PHONY: test-evolve audit-structure prove-organization prove-hygiene
.PHONY: prove-umbrella-agent prove-post-umbrella prove-inverse-science
.PHONY: prove-scriptor-benchmark generate-final-artifacts
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
