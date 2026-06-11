import json
import os

BENCHCORE = os.path.join(os.path.dirname(__file__), "..")

VALID_LAYERS = {
    "grammar_validation", "requirements", "evaluation", "feedback_loop",
    "dynamic_retrieval", "learning_policy", "inverse_science_alignment",
    "data_quality", "protocol_architecture", "human_review_ui",
}


def load_pattern_map():
    path = os.path.join(BENCHCORE, "generic_pattern_map.json")
    with open(path) as f:
        return json.load(f)


class TestGenericPatternBoundaries:

    def test_has_15_patterns(self):
        patterns = load_pattern_map()
        assert len(patterns) == 15

    def test_all_entries_have_required_fields(self):
        patterns = load_pattern_map()
        required = {
            "benchcore_specific_concept", "generic_agentx_pattern",
            "source_ids", "agent_x_layer", "allowed_scope",
            "forbidden_scope", "required_tests",
        }
        for p in patterns:
            missing = required - set(p.keys())
            assert not missing, f"Pattern missing: {missing}"

    def test_all_have_non_empty_benchcore_specific_concept(self):
        patterns = load_pattern_map()
        for p in patterns:
            assert p["benchcore_specific_concept"] and len(p["benchcore_specific_concept"]) > 5

    def test_all_have_non_empty_generic_agentx_pattern(self):
        patterns = load_pattern_map()
        for p in patterns:
            assert p["generic_agentx_pattern"] and len(p["generic_agentx_pattern"]) > 10

    def test_agent_x_layer_is_valid(self):
        patterns = load_pattern_map()
        for p in patterns:
            assert p["agent_x_layer"] in VALID_LAYERS, f"Bad layer: {p['agent_x_layer']}"

    def test_source_ids_is_non_empty_list(self):
        patterns = load_pattern_map()
        for p in patterns:
            assert isinstance(p["source_ids"], list)
            assert len(p["source_ids"]) > 0

    def test_allowed_scope_is_non_empty(self):
        patterns = load_pattern_map()
        for p in patterns:
            assert p["allowed_scope"] and len(p["allowed_scope"]) > 10

    def test_forbidden_scope_is_non_empty(self):
        patterns = load_pattern_map()
        for p in patterns:
            assert p["forbidden_scope"] and len(p["forbidden_scope"]) > 10

    def test_required_tests_is_non_empty_list(self):
        patterns = load_pattern_map()
        for p in patterns:
            assert isinstance(p["required_tests"], list)
            assert len(p["required_tests"]) > 0

    def test_all_source_ids_reference_inventory(self):
        patterns = load_pattern_map()
        inv_path = os.path.join(BENCHCORE, "source_inventory.json")
        with open(inv_path) as f:
            inv = json.load(f)
        inv_ids = {e["source_id"] for e in inv}
        for p in patterns:
            for sid in p["source_ids"]:
                assert sid in inv_ids, f"Unknown source_id {sid} in pattern"

    def test_no_duplicate_benchcore_concepts(self):
        patterns = load_pattern_map()
        concepts = [p["benchcore_specific_concept"] for p in patterns]
        assert len(concepts) == len(set(concepts))

    def test_forbidden_scope_differs_from_allowed_scope(self):
        patterns = load_pattern_map()
        for p in patterns:
            assert p["forbidden_scope"] != p["allowed_scope"]
