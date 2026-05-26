from __future__ import annotations

from pathlib import Path

import yaml

from core_kernel.contracts.seed_phase_order import REQUIRED_PHASES

ROOT = Path(__file__).resolve().parents[2]


def test_required_phase_order_matches_seed_invariants() -> None:
    invariants_path = ROOT / "SEED_INVARIANTS.yaml"
    invariants = yaml.safe_load(invariants_path.read_text(encoding="utf-8"))
    invariant_phases = invariants["runtime_order"]["required_phase_order"]

    for phase in invariant_phases:
        assert phase in REQUIRED_PHASES, (
            f"SEED_INVARIANTS phase '{phase}' not found in runtime REQUIRED_PHASES"
        )


def test_canonical_phase_order_starts_with_input() -> None:
    assert REQUIRED_PHASES[0] == "input_received"


def test_canonical_phase_order_ends_with_output() -> None:
    assert REQUIRED_PHASES[-1] == "output_returned"


def test_governance_before_gateway_in_required_phases() -> None:
    gov_idx = REQUIRED_PHASES.index("governance_checked")
    gw_idx = REQUIRED_PHASES.index("tool_requested")
    assert gov_idx < gw_idx, "governance_checked must precede tool_requested"
