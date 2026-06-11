import json
import os

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "benchmarks", "benchcore"))


def _load_patterns():
    with open(os.path.join(BASE, "generic_pattern_map.json")) as f:
        return json.load(f)


def _load_boundaries():
    with open(os.path.join(BASE, "product_specific_boundary_report.json")) as f:
        return json.load(f)


def _load_inventory():
    with open(os.path.join(BASE, "source_inventory.json")) as f:
        return json.load(f)


def test_patterns_have_all_fields():
    patterns = _load_patterns()
    required = {"benchcore_specific_concept", "generic_agentx_pattern", "source_ids",
                "agent_x_layer", "allowed_scope", "forbidden_scope"}
    for p in patterns:
        missing = required - set(p.keys())
        assert not missing, f"pattern missing {missing}"


def test_forbidden_scope_not_agentx_core():
    patterns = _load_patterns()
    for p in patterns:
        fs = p.get("forbidden_scope", "")
        assert "Agent_X core assumption" not in fs, f"forbidden_scope mentions core: {fs}"


def test_all_sources_exist():
    patterns = _load_patterns()
    inventory = _load_inventory()
    inv_ids = {r["source_id"] for r in inventory}
    for p in patterns:
        for sid in p["source_ids"]:
            assert sid in inv_ids, f"pattern references unknown {sid}"


def test_product_boundary_entries_have_all_fields():
    boundaries = _load_boundaries()
    required = {"concept", "source_ids", "boundary_type", "prevented_action"}
    for b in boundaries:
        missing = required - set(b.keys())
        assert not missing, f"boundary missing {missing}"


def test_product_term_as_core_rule_fails():
    patterns = _load_patterns()
    for p in patterns:
        assert p.get("allowed_scope", "") != "Agent_X core rule", \
            f"pattern has core rule scope: {p['benchcore_specific_concept']}"


def test_sabotage_quickcode_as_core_rule():
    """Sabotage: QuickCode must not become an Agent_X core rule"""
    patterns = _load_patterns()
    for p in patterns:
        if "quickcode" in p.get("benchcore_specific_concept", "").lower() or "quickcode" in p.get("generic_agentx_pattern", "").lower():
            assert "Agent_X core" not in p.get("forbidden_scope", ""), \
                "QuickCode must be bounded, not a core rule"
