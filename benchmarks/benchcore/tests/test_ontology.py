import json
import os

BENCHCORE = os.path.join(os.path.dirname(__file__), "..")

ONTOLOGY_FILES = {
    "acronym_map.json": {"min_entries": 25, "type": "dict"},
    "glossary.json": {"min_entries": 20, "type": "list"},
    "protocol_terms.json": {"min_entries": 15, "type": "list"},
    "command_terms.json": {"min_entries": 15, "type": "list"},
    "ui_terms.json": {"min_entries": 10, "type": "list"},
    "ml_terms.json": {"min_entries": 15, "type": "list"},
}


def load_ontology(filename):
    path = os.path.join(BENCHCORE, "ontology", filename)
    with open(path) as f:
        return json.load(f)


class TestOntology:

    def test_all_ontology_files_exist(self):
        for filename in ONTOLOGY_FILES:
            path = os.path.join(BENCHCORE, "ontology", filename)
            assert os.path.isfile(path), f"Missing ontology file: {filename}"

    def test_all_files_have_minimum_entries(self):
        for filename, spec in ONTOLOGY_FILES.items():
            data = load_ontology(filename)
            if spec["type"] == "dict":
                count = len(data)
            else:
                count = len(data)
            assert count >= spec["min_entries"], (
                f"{filename} has {count} entries, minimum {spec['min_entries']}"
            )

    def test_acronym_map_entries_have_required_fields(self):
        data = load_ontology("acronym_map.json")
        required = {"acronym", "expansion", "context", "term_type", "source_ids"}
        for key, entry in data.items():
            missing = required - set(entry.keys())
            assert not missing, f"Acronym {key} missing: {missing}"
            assert entry["acronym"] == key

    def test_acronym_map_has_valid_term_types(self):
        data = load_ontology("acronym_map.json")
        valid_types = {"benchcore_specific", "protocol_specific", "generic", "ui_specific"}
        for entry in data.values():
            assert entry["term_type"] in valid_types, f"Bad term_type: {entry['term_type']}"

    def test_acronym_map_all_source_ids_resolve(self):
        data = load_ontology("acronym_map.json")
        inv_path = os.path.join(BENCHCORE, "source_inventory.json")
        with open(inv_path) as f:
            inv = json.load(f)
        inv_ids = {e["source_id"] for e in inv}
        for entry in data.values():
            for sid in entry["source_ids"]:
                assert sid in inv_ids, f"Unknown source_id {sid} in acronym_map"

    def test_acronym_map_has_non_empty_expansions(self):
        data = load_ontology("acronym_map.json")
        for entry in data.values():
            assert entry["expansion"] and len(entry["expansion"]) > 2

    def test_acronym_map_has_non_empty_contexts(self):
        data = load_ontology("acronym_map.json")
        for entry in data.values():
            assert entry["context"] and len(entry["context"]) > 10

    def test_glossary_is_non_empty_list(self):
        data = load_ontology("glossary.json")
        assert isinstance(data, list)
        assert len(data) >= 20

    def test_glossary_entries_have_required_fields(self):
        data = load_ontology("glossary.json")
        for entry in data:
            assert "term" in entry
            assert "definition" in entry
            assert entry["term"] and len(entry["term"]) > 1
            assert entry["definition"] and len(entry["definition"]) > 5

    def test_protocol_terms_is_non_empty_list(self):
        data = load_ontology("protocol_terms.json")
        assert isinstance(data, list)
        assert len(data) >= 15

    def test_command_terms_is_non_empty_list(self):
        data = load_ontology("command_terms.json")
        assert isinstance(data, list)
        assert len(data) >= 15

    def test_ui_terms_is_non_empty_list(self):
        data = load_ontology("ui_terms.json")
        assert isinstance(data, list)
        assert len(data) >= 10

    def test_ml_terms_is_non_empty_list(self):
        data = load_ontology("ml_terms.json")
        assert isinstance(data, list)
        assert len(data) >= 15
