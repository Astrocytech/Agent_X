import json
import os

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "benchmarks", "benchcore"))


def _load_visual():
    with open(os.path.join(BASE, "visual_inventory.json")) as f:
        return json.load(f)


def _load_inventory():
    with open(os.path.join(BASE, "source_inventory.json")) as f:
        return json.load(f)


def test_visual_records_have_required_fields():
    records = _load_visual()
    required = {"source_id", "filename", "visual_type", "content_role", "summary", "mapped_artifacts", "status"}
    for r in records:
        missing = required - set(r.keys())
        assert not missing, f"record missing {missing}"


def test_content_role_valid():
    records = _load_visual()
    for r in records:
        assert r["content_role"] in ("requirement_bearing", "explanatory_only", "explanatory"), f"bad role: {r['content_role']}"


def test_visual_type_valid():
    records = _load_visual()
    known_types = {"slide", "workflow_diagram", "table", "flowchart", "architecture_diagram",
                   "screenshot", "ui_mockup", "org_chart"}
    for r in records:
        assert r["visual_type"] in known_types, f"bad type: {r['visual_type']}"


def test_missing_visual_for_diagram_pdf_fails():
    records = _load_visual()
    inventory = _load_inventory()
    doc005 = next(r for r in inventory if r["source_id"] == "BENCHCORE-DOC-005")
    assert doc005 is not None
    doc005_visuals = [v for v in records if v["source_id"] == "BENCHCORE-DOC-005"]
    assert len(doc005_visuals) > 0, "BENCHCORE-DOC-005 should have visuals"


def test_sabotage_missing_visual_coverage():
    """Sabotage: BENCHCORE-DOC-005 has workflow diagrams but must have visual coverage"""
    import json
    records = json.load(open(os.path.join(BASE, "visual_inventory.json")))
    doc_005 = [v for v in records if v["source_id"] == "BENCHCORE-DOC-005"]
    assert len(doc_005) > 0, "DOC-005 has diagrams but no visual coverage"
    for v in doc_005:
        if v["visual_type"] in ("workflow_diagram",):
            assert v["content_role"] == "requirement_bearing"
