import json
import os

BENCHCORE = os.path.join(os.path.dirname(__file__), "..")
ISA_DIR = os.path.join(BENCHCORE, "inverse_science_alignment")


class TestInverseScienceAlignment:

    def test_directory_exists(self):
        assert os.path.isdir(ISA_DIR)

    def test_reasoning_type_rules_exists(self):
        path = os.path.join(ISA_DIR, "reasoning_type_rules.json")
        assert os.path.isfile(path)

    def test_reasoning_type_rules_has_at_least_10_entries(self):
        path = os.path.join(ISA_DIR, "reasoning_type_rules.json")
        with open(path) as f:
            rules = json.load(f)
        assert len(rules) >= 10

    def test_reasoning_type_rules_have_required_fields(self):
        path = os.path.join(ISA_DIR, "reasoning_type_rules.json")
        with open(path) as f:
            rules = json.load(f)
        required = {
            "rule_id", "reasoning_type", "definition",
            "allowed_when", "forbidden_when", "example",
            "source_ids", "validation_test",
        }
        for r in rules:
            missing = required - set(r.keys())
            assert not missing, f"{r['rule_id']} missing: {missing}"

    def test_reasoning_types_are_valid(self):
        path = os.path.join(ISA_DIR, "reasoning_type_rules.json")
        with open(path) as f:
            rules = json.load(f)
        valid_types = {"explanation", "deduction", "abduction"}
        for r in rules:
            assert r["reasoning_type"] in valid_types, f"{r['rule_id']} bad type"

    def test_no_duplicate_rule_ids(self):
        path = os.path.join(ISA_DIR, "reasoning_type_rules.json")
        with open(path) as f:
            rules = json.load(f)
        ids = [r["rule_id"] for r in rules]
        assert len(ids) == len(set(ids))

    def test_all_rules_have_non_empty_definitions(self):
        path = os.path.join(ISA_DIR, "reasoning_type_rules.json")
        with open(path) as f:
            rules = json.load(f)
        for r in rules:
            assert r["definition"] and len(r["definition"]) > 10

    def test_all_rules_have_examples(self):
        path = os.path.join(ISA_DIR, "reasoning_type_rules.json")
        with open(path) as f:
            rules = json.load(f)
        for r in rules:
            assert r["example"] and len(r["example"]) > 5

    def test_observations_jsonl_exists(self):
        path = os.path.join(ISA_DIR, "observations.jsonl")
        assert os.path.isfile(path)

    def test_observations_jsonl_is_non_empty(self):
        path = os.path.join(ISA_DIR, "observations.jsonl")
        with open(path) as f:
            lines = [l for l in f if l.strip()]
        assert len(lines) > 0

    def test_hypotheses_jsonl_exists(self):
        path = os.path.join(ISA_DIR, "hypotheses.jsonl")
        assert os.path.isfile(path)

    def test_hypotheses_jsonl_is_non_empty(self):
        path = os.path.join(ISA_DIR, "hypotheses.jsonl")
        with open(path) as f:
            lines = [l for l in f if l.strip()]
        assert len(lines) > 0

    def test_candidate_tests_jsonl_exists(self):
        path = os.path.join(ISA_DIR, "candidate_tests.jsonl")
        assert os.path.isfile(path)

    def test_candidate_tests_is_non_empty(self):
        path = os.path.join(ISA_DIR, "candidate_tests.jsonl")
        with open(path) as f:
            lines = [l for l in f if l.strip()]
        assert len(lines) > 0

    def test_negative_knowledge_jsonl_exists(self):
        path = os.path.join(ISA_DIR, "negative_knowledge.jsonl")
        assert os.path.isfile(path)

    def test_negative_knowledge_is_non_empty(self):
        path = os.path.join(ISA_DIR, "negative_knowledge.jsonl")
        with open(path) as f:
            lines = [l for l in f if l.strip()]
        assert len(lines) > 0

    def test_all_jsonl_files_contain_valid_json(self):
        for fname in ("observations.jsonl", "hypotheses.jsonl", "candidate_tests.jsonl", "negative_knowledge.jsonl"):
            path = os.path.join(ISA_DIR, fname)
            with open(path) as f:
                for i, line in enumerate(f, 1):
                    if line.strip():
                        json.loads(line)
