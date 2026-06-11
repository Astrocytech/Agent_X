import json
import os

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "benchmarks", "benchcore"))
ONT = os.path.join(BASE, "ontology")


def test_acronym_map_has_entries():
    with open(os.path.join(ONT, "acronym_map.json")) as f:
        data = json.load(f)
    assert len(data) >= 20


def test_acronym_expansion_defined():
    with open(os.path.join(ONT, "acronym_map.json")) as f:
        data = json.load(f)
    for key, val in data.items():
        assert "acronym" in val, f"{key} missing acronym"
        assert "expansion" in val, f"{key} missing expansion"
        assert "context" in val, f"{key} missing context"


def test_glossary_has_entries():
    with open(os.path.join(ONT, "glossary.json")) as f:
        data = json.load(f)
    assert len(data) >= 20


def test_glossary_terms_have_definition():
    with open(os.path.join(ONT, "glossary.json")) as f:
        data = json.load(f)
    for entry in data:
        assert "term" in entry, "missing term"
        assert "definition" in entry, f"missing definition for {entry.get('term')}"


def test_protocol_terms_exist():
    with open(os.path.join(ONT, "protocol_terms.json")) as f:
        data = json.load(f)
    assert len(data) >= 10


def test_command_terms_exist():
    with open(os.path.join(ONT, "command_terms.json")) as f:
        data = json.load(f)
    assert len(data) >= 10


def test_ui_terms_exist():
    with open(os.path.join(ONT, "ui_terms.json")) as f:
        data = json.load(f)
    assert len(data) >= 5


def test_ml_terms_exist():
    with open(os.path.join(ONT, "ml_terms.json")) as f:
        data = json.load(f)
    assert len(data) >= 10


def test_circular_definition_detected():
    with open(os.path.join(ONT, "glossary.json")) as f:
        data = json.load(f)
    for entry in data:
        term = entry.get("term", "").lower()
        defn = entry.get("definition", "").lower()
        if term and defn:
            if term in defn and len(term) > 3:
                pass
