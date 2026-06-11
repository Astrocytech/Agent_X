import json
import os

BENCHCORE = os.path.join(os.path.dirname(__file__), "..")
LP_DIR = os.path.join(BENCHCORE, "learning_policy")

REQUIRED_LP_FILES = [
    "allowed_learning_mechanisms.json",
    "anti_retraining_policy.md",
    "deferred_training_experiments.md",
    "forbidden_learning_mechanisms.json",
]


class TestLearningPolicy:

    def test_learning_policy_directory_exists(self):
        assert os.path.isdir(LP_DIR)

    def test_all_required_files_exist(self):
        for fname in REQUIRED_LP_FILES:
            path = os.path.join(LP_DIR, fname)
            assert os.path.isfile(path), f"Missing: {fname}"
            assert os.path.getsize(path) > 0, f"Empty: {fname}"

    def test_has_4_files(self):
        files = [f for f in os.listdir(LP_DIR) if os.path.isfile(os.path.join(LP_DIR, f))]
        assert len(files) == 4

    def test_allowed_learning_mechanisms_has_entries(self):
        path = os.path.join(LP_DIR, "allowed_learning_mechanisms.json")
        with open(path) as f:
            mechanisms = json.load(f)
        assert isinstance(mechanisms, list)
        assert len(mechanisms) >= 8

    def test_allowed_mechanisms_have_required_fields(self):
        path = os.path.join(LP_DIR, "allowed_learning_mechanisms.json")
        with open(path) as f:
            mechanisms = json.load(f)
        required = {"mechanism", "description", "constraints", "evaluation_required", "source_ids"}
        for m in mechanisms:
            missing = required - set(m.keys())
            assert not missing, f"{m.get('mechanism')} missing: {missing}"

    def test_allowed_mechanisms_have_non_empty_descriptions(self):
        path = os.path.join(LP_DIR, "allowed_learning_mechanisms.json")
        with open(path) as f:
            mechanisms = json.load(f)
        for m in mechanisms:
            assert m["description"] and len(m["description"]) > 10

    def test_evaluation_required_is_bool(self):
        path = os.path.join(LP_DIR, "allowed_learning_mechanisms.json")
        with open(path) as f:
            mechanisms = json.load(f)
        for m in mechanisms:
            assert isinstance(m["evaluation_required"], bool)

    def test_forbidden_learning_mechanisms_exists(self):
        path = os.path.join(LP_DIR, "forbidden_learning_mechanisms.json")
        with open(path) as f:
            forbidden = json.load(f)
        assert isinstance(forbidden, (dict, list))
        assert len(json.dumps(forbidden)) > 10

    def test_anti_retraining_policy_is_non_empty(self):
        path = os.path.join(LP_DIR, "anti_retraining_policy.md")
        size = os.path.getsize(path)
        assert size > 100

    def test_deferred_training_experiments_is_non_empty(self):
        path = os.path.join(LP_DIR, "deferred_training_experiments.md")
        size = os.path.getsize(path)
        assert size > 50

    def test_no_duplicate_mechanisms_in_allowed(self):
        path = os.path.join(LP_DIR, "allowed_learning_mechanisms.json")
        with open(path) as f:
            mechanisms = json.load(f)
        names = [m["mechanism"] for m in mechanisms]
        assert len(names) == len(set(names))
