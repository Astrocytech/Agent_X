# Governed Universal Seed Kernel Makefile

PYTHON ?= python3
PIP_INSTALL ?= pip3 install --break-system-packages

.PHONY: help install seed-boot prove-seed prove-l1 prove-l2 prove-format prove-all test-quick test-dev test-release test-sabotage test-security test-all test-live test-l0 test-l1 test-l2 test-initiator test-evolve audit-structure prove-organization prove-hygiene prove-umbrella-agent run clean build-seed

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

install:
	$(PIP_INSTALL) -r requirements/seed.txt

seed-boot:
	PYTHONPATH=L0/CODE $(PYTHON) -m compileall -q L0/CODE
	PYTHONPATH=L0/CODE $(PYTHON) L0/scripts/proofs/prove_seed_boot.py
	@echo "=== seed-boot: OK ==="

prove-seed:
	PYTHONPATH=L0/CODE $(PYTHON) -m compileall -q L0/CODE
	PYTHONPATH=L0/CODE $(PYTHON) L0/scripts/proofs/validate_seed_manifests.py
	PYTHONPATH=L0/CODE $(PYTHON) -m pytest L0/tests/seed_l0 -q --tb=short -p no:cacheprovider
	@echo "=== prove-seed: OK ==="

prove-l1:
	PYTHONPATH=L1 $(PYTHON) -m compileall -q L1
	PYTHONPATH=. $(PYTHON) -m pytest L1/tests -q --tb=short -p no:cacheprovider
	PYTHONPATH=. $(PYTHON) -m L1.validators.validate_all
	@echo "=== prove-l1: OK ==="

prove-l2:
	$(PYTHON) L2/validators/bootstrap_validate_l2_scaffold.py
	PYTHONPATH=L2 $(PYTHON) -m pytest L2/tests -q --tb=short -p no:cacheprovider
	@echo "=== prove-l2: OK ==="

prove-format:
	PYTHONPATH=. $(PYTHON) -m pytest tests/quick/test_text_file_formatting.py tests/quick/test_format_guard_self_integrity.py tests/quick/test_makefile_proof_wiring.py -q --tb=short -p no:cacheprovider
	@echo "=== prove-format: OK ==="

prove-all: audit-structure prove-seed prove-l1 prove-l2 prove-format
	@echo "=== prove-all: OK ==="

audit-structure:
	PYTHONPATH=tools/repo_audit $(PYTHON) tools/repo_audit/audit_repository_structure.py
	@echo "=== audit-structure: OK ==="

prove-organization:
	$(MAKE) audit-structure
	PYTHONPATH=. $(PYTHON) -m pytest --collect-only -q
	find . -maxdepth 1 -type f | sort
	git status --short
	@echo "=== prove-organization: OK ==="

# ── Tiered test suites ─────────────────────────────────────────────────────

test-quick:
	PYTHONPATH=. $(PYTHON) -m pytest tests/quick -q --tb=short -p no:cacheprovider

test-dev:
	PYTHONPATH=. $(PYTHON) -m pytest tests/dev -q --tb=short -p no:cacheprovider

test-release:
	PYTHONPATH="L0/CODE:tools" $(PYTHON) -m pytest tests/release -q --tb=short -p no:cacheprovider -m "not live"

test-sabotage:
	PYTHONPATH="L0/CODE:tools" $(PYTHON) -m pytest tests/release/test_sabotage_checks.py -q --tb=short -p no:cacheprovider

test-security:
	PYTHONPATH="L0/CODE:tools" $(PYTHON) -m pytest tests/release/test_negative_*.py -q --tb=short -p no:cacheprovider

test-live:
	PYTHONPATH=. $(PYTHON) -m pytest -q -m live --tb=short -p no:cacheprovider

test-all:
	PYTHONPATH="L0/CODE:L1:L2:tools/agentx_initiator:tools/agentx_evolve:tools" $(PYTHON) -m pytest L0/tests L1/tests L2/tests tools/agentx_initiator/tests tools/agentx_evolve/tests tests/quick tests/dev tests/release -q --tb=short -p no:cacheprovider -m "not live"

# ── Legacy aliases (deprecated, route to new tiers) ────────────────────────

test-smoke: test-quick
	@echo "test-smoke is deprecated, use 'make test-quick'"

test-integration: test-release
	@echo "test-integration is deprecated, use 'make test-release'"

test-system: test-release
	@echo "test-system is deprecated, use 'make test-release'"

test-regression: test-release
	@echo "test-regression is deprecated, use 'make test-release'"

test-l0: prove-seed

test-l1: prove-l1

test-l2: prove-l2

test-initiator:
	PYTHONPATH=tools/agentx_initiator $(PYTHON) -m pytest tools/agentx_initiator/tests -q --tb=short -p no:cacheprovider

test-evolve:
	PYTHONPATH=tools/agentx_evolve $(PYTHON) -m pytest tools/agentx_evolve/tests -q --tb=short -p no:cacheprovider

prove-hygiene:
	PYTHONPATH=L0/CODE ruff check L0/CODE/
	PYTHONPATH=L0/CODE $(PYTHON) -m mypy L0/CODE/core_kernel/ L0/CODE/tool_gateway/ L0/CODE/governance/ --ignore-missing-imports
	pip-audit -r requirements/seed.txt
	@echo "=== prove-hygiene: OK ==="

prove-umbrella-agent:
	$(PYTHON) scripts/prove-umbrella-agent.sh

run:
	PYTHONPATH=L0/CODE $(PYTHON) -c "from core_kernel.public.kernel_service import KernelService; from core_kernel.models.kernel_requests import KernelTurnRequest; k=KernelService(); print(k.run_turn(KernelTurnRequest(user_input='Say hello from the governed seed.', session_id='cli')))"

build-seed:
	PYTHONPATH=L0/CODE $(PYTHON) L0/scripts/build_seed_package.py

clean:
	rm -rf .local/runtime/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	@echo "=== clean: OK ==="
