import csv
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL = os.path.join(BASE, "evaluation")


def _csv_rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _validate_csv_has_column(rows, column):
    return column in rows[0] if rows else False


def test_evaluation_config_schema_valid():
    rows = _csv_rows(os.path.join(EVAL, "valid_dataset_fixture.csv"))
    assert len(rows) > 0
    assert _validate_csv_has_column(rows, "id")
    assert _validate_csv_has_column(rows, "input_text")


def test_missing_keys_fails():
    rows = _csv_rows(os.path.join(EVAL, "invalid_dataset_missing_keys.csv"))
    has_label = _validate_csv_has_column(rows, "expected_label")
    assert not has_label, "missing_keys csv should lack expected_label"


def test_bad_ranked_list_fails():
    rows = _csv_rows(os.path.join(EVAL, "invalid_dataset_bad_ranked_list.csv"))
    lengths = set()
    for row in rows:
        rank = row.get("rank", "")
        parts = rank.split(",") if rank else []
        lengths.add(len(parts))
    assert len(lengths) > 1, "expected varying rank lengths, but all were same"


def test_expected_metrics_has_required_metrics():
    with open(os.path.join(EVAL, "expected_metrics_fixture.json")) as f:
        data = json.load(f)
    metrics = data["expected_metrics"]
    for m in ("exact_match_accuracy", "macro_f1", "micro_f1", "mrr"):
        assert m in metrics, f"missing metric {m}"


def test_deployment_gate_conditions():
    with open(os.path.join(EVAL, "deployment_gate_contract.json")) as f:
        data = json.load(f)
    assert "conditions" in data
    assert len(data["conditions"]) > 0


def test_valid_csv_parses():
    rows = _csv_rows(os.path.join(EVAL, "valid_dataset_fixture.csv"))
    assert len(rows) >= 10


def test_missing_key_not_caught_fails():
    rows = _csv_rows(os.path.join(EVAL, "invalid_dataset_missing_keys.csv"))
    assert not _validate_csv_has_column(rows, "expected_label"), \
        "validation should catch missing expected_label"


def test_sabotage_invalid_ranked_list_length():
    """Sabotage: invalid ranked-list length must be rejected"""
    import csv
    with open(os.path.join(EVAL, "invalid_dataset_bad_ranked_list.csv")) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    rank_lengths = [len(row.get("rank", "").split(",")) for row in rows]
    assert len(set(rank_lengths)) > 1, \
        "Ranked list CSV must contain rows of varying rank lengths"
