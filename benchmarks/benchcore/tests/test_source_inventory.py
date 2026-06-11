import json
import os

BENCHCORE = os.path.join(os.path.dirname(__file__), "..")

REQUIRED_FIELDS = {
    "source_id", "filename", "batch", "sha256", "status",
    "primary_group", "agentx_use", "product_specific",
    "live_dependency", "required_artifacts", "deferred_boundaries",
    "claim_boundary",
}

VALID_STATUSES = {"now", "later", "now, benchmark only", "optional / later"}
VALID_GROUPS = {
    "feedback_loop", "requirements", "evaluation", "data_quality",
    "dynamic_retrieval", "learning_policy", "inverse_science_alignment",
    "operations_reproducibility", "grammar_validation", "protocol_architecture",
    "ontology", "human_review_ui", "optional_benchmarks",
}


def load_inventory():
    path = os.path.join(BENCHCORE, "source_inventory.json")
    with open(path) as f:
        return json.load(f)


def load_hashes():
    path = os.path.join(BENCHCORE, "source_hashes.json")
    with open(path) as f:
        return json.load(f)


class TestSourceInventory:

    def test_has_32_records(self):
        inventory = load_inventory()
        assert len(inventory) == 32

    def test_all_records_have_required_fields(self):
        inventory = load_inventory()
        for entry in inventory:
            missing = REQUIRED_FIELDS - set(entry.keys())
            assert not missing, f"{entry['source_id']} missing fields: {missing}"

    def test_no_duplicate_source_ids(self):
        inventory = load_inventory()
        ids = [e["source_id"] for e in inventory]
        assert len(ids) == len(set(ids))

    def test_no_duplicate_filenames(self):
        inventory = load_inventory()
        filenames = [e["filename"] for e in inventory]
        assert len(filenames) == len(set(filenames))

    def test_all_source_ids_have_dash_three_digit_format(self):
        inventory = load_inventory()
        for entry in inventory:
            assert entry["source_id"].startswith("BENCHCORE-DOC-")
            num = entry["source_id"].split("-")[-1]
            assert num.isdigit() and 1 <= int(num) <= 99

    def test_all_have_sha256_field(self):
        inventory = load_inventory()
        for entry in inventory:
            assert entry["sha256"], f"{entry['source_id']} has empty sha256"

    def test_all_have_non_empty_agentx_use(self):
        inventory = load_inventory()
        for entry in inventory:
            assert entry["agentx_use"] and len(entry["agentx_use"]) > 10

    def test_all_have_valid_status(self):
        inventory = load_inventory()
        for entry in inventory:
            assert entry["status"] in VALID_STATUSES, f"{entry['source_id']} bad status: {entry['status']}"

    def test_all_have_valid_primary_group(self):
        inventory = load_inventory()
        for entry in inventory:
            assert entry["primary_group"] in VALID_GROUPS, f"{entry['source_id']} bad group: {entry['primary_group']}"

    def test_all_have_bool_product_specific(self):
        inventory = load_inventory()
        for entry in inventory:
            assert isinstance(entry["product_specific"], bool)

    def test_all_have_bool_live_dependency(self):
        inventory = load_inventory()
        for entry in inventory:
            assert isinstance(entry["live_dependency"], bool)

    def test_live_dependency_is_always_false(self):
        inventory = load_inventory()
        for entry in inventory:
            assert entry["live_dependency"] is False, f"{entry['source_id']} has live_dependency=true"

    def test_all_have_required_artifacts_as_list(self):
        inventory = load_inventory()
        for entry in inventory:
            assert isinstance(entry["required_artifacts"], list)

    def test_all_have_deferred_boundaries_as_list(self):
        inventory = load_inventory()
        for entry in inventory:
            assert isinstance(entry["deferred_boundaries"], list)

    def test_all_have_claim_boundary(self):
        inventory = load_inventory()
        for entry in inventory:
            assert entry["claim_boundary"] == "benchmark only"

    def test_all_batch_is_int_one(self):
        inventory = load_inventory()
        for entry in inventory:
            assert entry["batch"] == 1

    def test_source_hashes_json_has_all_source_ids(self):
        inventory = load_inventory()
        hashes = load_hashes()
        for entry in inventory:
            sid = entry["source_id"]
            assert sid in hashes, f"{sid} missing from source_hashes.json"
            assert "sha256" in hashes[sid]
            assert "status" in hashes[sid]
