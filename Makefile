# Governed Universal Seed Kernel Makefile

PYTHON ?= python3
PIP_INSTALL ?= pip3 install --break-system-packages

.PHONY: help install seed-boot prove-seed prove-l1 prove-l2 prove-format prove-all prove-hygiene run clean build-seed

help:
	@echo "L0 commands:"
	@echo "  make install      Install minimal seed dependencies"
	@echo "  make seed-boot    Compile and boot the seed"
	@echo "  make prove-seed   Run canonical L0 seed proof"
	@echo "  make run          Run one governed seed turn"
	@echo "  make build-seed   Build seed package from manifest"
	@echo "L1 commands:"
	@echo "  make prove-l1     Run L1 structure tests"
	@echo "L2 commands:"
	@echo "  make prove-l2     Run L2 structure tests"
	@echo "  make prove-format Run formatting guard tests"
	@echo "  make prove-all    Run all tests across layers"
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
	PYTHONPATH=. $(PYTHON) -m pytest L0/tests L1/tests L2/tests -q --tb=short -p no:cacheprovider -k "formatting or text_file"
	@echo "=== prove-format: OK ==="

prove-all: prove-seed prove-l1 prove-l2
	@echo "=== prove-all: OK ==="

prove-hygiene:
	PYTHONPATH=L0/CODE ruff check L0/CODE/
	PYTHONPATH=L0/CODE $(PYTHON) -m mypy L0/CODE/core_kernel/ L0/CODE/tool_gateway/ L0/CODE/governance/ --ignore-missing-imports
	pip-audit -r requirements/seed.txt
	@echo "=== prove-hygiene: OK ==="

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
