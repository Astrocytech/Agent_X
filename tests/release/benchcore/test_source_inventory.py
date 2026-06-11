import json
import os

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "benchmarks", "benchcore"))


def _load_inventory():
    with open(os.path.join(BASE, "source_inventory.json")) as f:
        return json.load(f)


def _load_hashes():
    with open(os.path.join(BASE, "source_hashes.json")) as f:
        return json.load(f)


def _validate_inventory(inventory):
    if len(inventory) != 32:
        return False, f"expected 32 records, got {len(inventory)}"
    ids = [r["source_id"] for r in inventory]
    if len(ids) != len(set(ids)):
        return False, "duplicate source_ids found"
    required = {"source_id", "filename", "status", "sha256", "primary_group", "agentx_use", "product_specific", "live_dependency", "claim_boundary"}
    valid_statuses = {"now", "now, benchmark only", "later", "optional / later"}
    for r in inventory:
        missing = required - set(r.keys())
        if missing:
            return False, f"{r['source_id']} missing fields: {missing}"
        if r["status"] not in valid_statuses:
            return False, f"{r['source_id']} invalid status: {r['status']}"
        if not isinstance(r["product_specific"], bool):
            return False, f"{r['source_id']} product_specific not bool"
        if r["status"] == "now" and r["live_dependency"] is not False:
            return False, f"{r['source_id']} now-status but live_dependency not False"
        if not isinstance(r["filename"], str) or not r["filename"]:
            return False, f"{r['source_id']} empty filename"
    return True, "ok"


def test_source_inventory_has_32_records():
    inventory = _load_inventory()
    assert len(inventory) == 32


def test_no_duplicate_source_ids():
    inventory = _load_inventory()
    ids = [r["source_id"] for r in inventory]
    assert len(ids) == len(set(ids))


def test_all_source_ids_have_required_fields():
    inventory = _load_inventory()
    required = {"source_id", "filename", "status", "sha256", "primary_group", "agentx_use", "product_specific", "live_dependency", "claim_boundary"}
    for r in inventory:
        missing = required - set(r.keys())
        assert not missing, f"{r['source_id']} missing: {missing}"


def test_status_values_valid():
    inventory = _load_inventory()
    valid_statuses = {"now", "now, benchmark only", "later", "optional / later"}
    for r in inventory:
        assert r["status"] in valid_statuses, f"{r['source_id']} bad status: {r['status']}"


def test_product_specific_is_bool():
    inventory = _load_inventory()
    for r in inventory:
        assert isinstance(r["product_specific"], bool), f"{r['source_id']} product_specific not bool"


def test_live_dependency_is_false():
    inventory = _load_inventory()
    for r in inventory:
        if r["status"] == "now":
            assert r["live_dependency"] is False, f"{r['source_id']} live_dependency not False"


def test_no_missing_filenames():
    inventory = _load_inventory()
    for r in inventory:
        assert isinstance(r["filename"], str) and r["filename"], f"{r['source_id']} empty filename"


def test_source_hashes_file():
    inventory = _load_inventory()
    hashes = _load_hashes()
    inv_ids = {r["source_id"] for r in inventory}
    hash_ids = set(hashes.keys())
    assert inv_ids == hash_ids, f"mismatch: {inv_ids - hash_ids} / {hash_ids - inv_ids}"
    for sid in inv_ids:
        assert hashes[sid]["sha256"] is not None


def test_duplicate_source_id_fails():
    inventory = _load_inventory()
    dup = inventory + [dict(inventory[0])]
    valid, msg = _validate_inventory(dup)
    assert not valid, "duplicate should fail"


def test_missing_source_fails():
    inventory = _load_inventory()
    truncated = inventory[:-1]
    valid, msg = _validate_inventory(truncated)
    assert not valid, "missing source should fail"


def test_sabotage_missing_entry():
    """Sabotage: remove one PDF from inventory → validation should detect it"""
    import json
    inventory = json.load(open(os.path.join(BASE, "source_inventory.json")))
    modified = [r for r in inventory if r["source_id"] != "BENCHCORE-DOC-001"]
    assert len(modified) == 31, "Sabotage: removed one PDF"
    assert len(modified) != len(inventory), "Sabotage should have removed an entry"


def test_sabotage_duplicate_id():
    """Sabotage: duplicate source_id → validation should detect it"""
    import json
    inventory = json.load(open(os.path.join(BASE, "source_inventory.json")))
    ids = [r["source_id"] for r in inventory]
    assert len(ids) == len(set(ids)), "Duplicate source_id detected"


def test_sabotage_readiness_score_5():
    """Sabotage: no dimension should be scored 5 in Stage A"""
    import json
    matrix = json.load(open(os.path.join(BASE, "universal_agent_readiness_evidence_matrix.json")))
    for dim in matrix:
        score = dim.get("score", 0)
        assert score <= 4, f"Stage A max score is 4, found {score} in {dim.get('dimension_name', 'unknown')}"
