# Governed Universal Seed Kernel Makefile

PYTHON ?= python3
PIP_INSTALL ?= pip3 install --break-system-packages

.PHONY: help install seed-boot prove-seed prove-hygiene run clean build-seed

help:
	@echo "L0 commands:"
	@echo "  make install      Install minimal seed dependencies"
	@echo "  make seed-boot    Compile and boot the seed"
	@echo "  make prove-seed   Run canonical L0 seed proof"
	@echo "  make run          Run one governed seed turn"
	@echo "  make clean        Remove generated runtime artifacts"
	@echo "  make build-seed   Build seed package from manifest"

install:
	$(PIP_INSTALL) -r requirements/seed.txt

seed-boot:
	PYTHONPATH=CODE $(PYTHON) -m compileall -q CODE
	PYTHONPATH=CODE $(PYTHON) scripts/proofs/prove_seed_boot.py
	@echo "=== seed-boot: OK ==="

prove-seed:
	PYTHONPATH=CODE $(PYTHON) -m compileall -q CODE
	PYTHONPATH=CODE $(PYTHON) scripts/proofs/validate_seed_manifests.py
	PYTHONPATH=CODE $(PYTHON) -m pytest tests/seed_l0 -q --tb=short -p no:cacheprovider
	@echo "=== prove-seed: OK ==="

prove-hygiene:
	PYTHONPATH=CODE ruff check CODE/
	PYTHONPATH=CODE $(PYTHON) -m mypy CODE/core_kernel/ CODE/tool_gateway/ CODE/governance/ --ignore-missing-imports
	pip-audit -r requirements/seed.txt
	@echo "=== prove-hygiene: OK ==="

run:
	PYTHONPATH=CODE $(PYTHON) -c "from core_kernel.public.kernel_service import KernelService; from core_kernel.models.kernel_requests import KernelTurnRequest; k=KernelService(); print(k.run_turn(KernelTurnRequest(user_input='Say hello from the governed seed.', session_id='cli')))"

build-seed:
	PYTHONPATH=CODE $(PYTHON) scripts/build_seed_package.py

clean:
	rm -rf .local/runtime/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	@echo "=== clean: OK ==="
