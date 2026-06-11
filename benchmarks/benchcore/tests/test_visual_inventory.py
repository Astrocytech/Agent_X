import json
import os

BENCHCORE = os.path.join(os.path.dirname(__file__), "..")


def load_visual_inventory():
    path = os.path.join(BENCHCORE, "visual_inventory.json")
    with open(path) as f:
        return json.load(f)


VALID_VISUAL_TYPES = {
    "slide", "workflow_diagram", "table", "flowchart",
    "architecture_diagram", "screenshot", "ui_mockup",
    "org_chart",
}
VALID_CONTENT_ROLES = {"requirement_bearing", "explanatory_only"}
VALID_STATUSES = {"covered", "explanatory_only"}


class TestVisualInventory:

    def test_is_non_empty_list(self):
        inventory = load_visual_inventory()
        assert len(inventory) > 0

    def test_all_entries_have_required_fields(self):
        inventory = load_visual_inventory()
        required = {
            "source_id", "filename", "page", "visual_type",
            "content_role", "summary", "mapped_artifacts", "status",
        }
        for entry in inventory:
            missing = required - set(entry.keys())
            assert not missing, f"Entry missing: {missing}"

    def test_all_source_ids_reference_inventory(self):
        inventory = load_visual_inventory()
        inv_path = os.path.join(BENCHCORE, "source_inventory.json")
        with open(inv_path) as f:
            inv = json.load(f)
        inv_ids = {e["source_id"] for e in inv}
        for entry in inventory:
            assert entry["source_id"] in inv_ids, f"Unknown source_id: {entry['source_id']}"

    def test_page_is_positive_int(self):
        inventory = load_visual_inventory()
        for entry in inventory:
            assert isinstance(entry["page"], int) and entry["page"] > 0

    def test_visual_type_is_valid(self):
        inventory = load_visual_inventory()
        for entry in inventory:
            assert entry["visual_type"] in VALID_VISUAL_TYPES, f"Bad visual_type: {entry['visual_type']}"

    def test_content_role_is_valid(self):
        inventory = load_visual_inventory()
        for entry in inventory:
            assert entry["content_role"] in VALID_CONTENT_ROLES, f"Bad content_role: {entry['content_role']}"

    def test_status_is_valid(self):
        inventory = load_visual_inventory()
        for entry in inventory:
            assert entry["status"] in VALID_STATUSES, f"Bad status: {entry['status']}"

    def test_summary_is_non_empty(self):
        inventory = load_visual_inventory()
        for entry in inventory:
            assert entry["summary"] and len(entry["summary"]) > 5

    def test_mapped_artifacts_is_list(self):
        inventory = load_visual_inventory()
        for entry in inventory:
            assert isinstance(entry["mapped_artifacts"], list)

    def test_mapped_artifacts_are_non_empty_when_covered(self):
        inventory = load_visual_inventory()
        for entry in inventory:
            if entry["status"] == "covered":
                assert len(entry["mapped_artifacts"]) > 0

    def test_no_duplicate_entries(self):
        inventory = load_visual_inventory()
        seen = set()
        for entry in inventory:
            key = (entry["source_id"], entry["page"])
            assert key not in seen, f"Duplicate: {key}"
            seen.add(key)

    def test_at_least_21_entries(self):
        inventory = load_visual_inventory()
        assert len(inventory) >= 21

    def test_spans_at_least_11_pdfs(self):
        inventory = load_visual_inventory()
        pdfs = {e["source_id"] for e in inventory}
        assert len(pdfs) >= 11
