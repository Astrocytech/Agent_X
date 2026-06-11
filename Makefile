# Governed Universal Seed Kernel Makefile

PYTHON ?= python3
PIP_INSTALL ?= pip3 install --break-system-packages

.PHONY: help install seed-boot prove-seed prove-l1 prove-l2 prove-format prove-all test-quick test-dev test-release test-sabotage test-security test-all test-live test-l0 test-l1 test-l2 test-initiator test-evolve audit-structure prove-organization prove-hygiene prove-umbrella-agent prove-post-umbrella prove-inverse-science prove-scriptor-benchmark final-acceptance run clean build-seed

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
prove-all: prove-seed prove-format prove-l1 prove-l2 test-initiator test-evolve test-integration test-system test-regression test-all prove-umbrella-agent prove-post-umbrella prove-inverse-science prove-scriptor-benchmark final-acceptance audit-structure
	@echo "=== prove-all: OK ==="

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
	PYTHONPATH="L0/CODE:L1:L2:tools/agentx_initiator:tools/agentx_evolve:tools" $(PYTHON) -m pytest tests/release L1/tests L2/tests tools/agentx_initiator/tests tools/agentx_evolve/tests -q --tb=short -p no:cacheprovider -m "not live"

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
	PYTHONPATH="L0/CODE:L1:L2:tools/agentx_initiator:tools/agentx_evolve:tools" $(PYTHON) -m pytest tests/quick tests/dev tests/release L1/tests L2/tests tools/agentx_initiator/tests tools/agentx_evolve/tests -q --tb=short -p no:cacheprovider -m "not live"

# ── Legacy aliases (deprecated, route to new tiers) ────────────────────────

test-smoke: test-quick

test-integration: test-release

test-system: test-release

test-regression: test-release

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

# target_id: P2-C020-alt4
final-acceptance:
	$(PYTHON) tools/agentx_evolve/validators/validate_five_document_matrix.py .agentx-init/five_document_closure/matrix/five_document_traceability_matrix.json
	$(PYTHON) tools/agentx_evolve/validators/validate_evidence_manifest.py .agentx-init/five_document_closure/final/five_document_evidence_manifest.json
	$(PYTHON) tools/agentx_evolve/validators/validate_event_log.py .agentx-init/five_document_closure/final/five_document_event_log_validation.json
	$(PYTHON) tools/agentx_evolve/validators/validate_clean_replay_report.py .agentx-init/five_document_closure/final/five_document_clean_checkout_replay.json
	$(PYTHON) tools/agentx_evolve/validators/validate_claims.py .agentx-init/five_document_closure/final/five_document_claim_validation.json
	$(PYTHON) tools/agentx_evolve/validators/scan_secrets_in_evidence.py
	$(PYTHON) -c "import json; json.load(open('.agentx-init/five_document_closure/final/five_document_source_hash_manifest_after.json')); print('PASS: source hash manifest validates')"
	@echo "=== final-acceptance: OK ==="

# target_id: P2-C021
run:
	PYTHONPATH=L0/CODE $(PYTHON) -c "from core_kernel.public.kernel_service import KernelService; from core_kernel.models.kernel_requests import KernelTurnRequest; k=KernelService(); print(k.run_turn(KernelTurnRequest(user_input='Say hello from the governed seed.', session_id='cli')))"

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
