import json
import os
import re

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "benchmarks", "benchcore"))
PA = os.path.join(BASE, "protocol_architecture")

LIVE_PATTERNS = [
    r"https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?::\d+)?(?:/\S*)?",
    r"\b(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b",
]

SAFE_DOMAINS = {"example.com", "json-schema.org"}


def test_rest_mos_contract_exists():
    path = os.path.join(PA, "rest_mos_mapping_contract.md")
    assert os.path.exists(path)


def test_adapter_boundary_contract_exists():
    path = os.path.join(PA, "adapter_boundary_contract.md")
    assert os.path.exists(path)


def test_mock_rest_schema_valid():
    with open(os.path.join(PA, "mock_rest_input.schema.json")) as f:
        schema = json.load(f)
    props = schema.get("properties", {})
    for field in ("endpoint", "method", "headers", "body"):
        assert field in props, f"mock_rest schema missing {field}"


def test_mock_mos_schema_valid():
    with open(os.path.join(PA, "mock_mos_output.schema.json")) as f:
        schema = json.load(f)
    props = schema.get("properties", {})
    for field in ("status", "payload", "timestamp"):
        assert field in props, f"mock_mos schema missing {field}"


def test_failure_modes_documented():
    with open(os.path.join(PA, "failure_modes.json")) as f:
        modes = json.load(f)
    assert len(modes) >= 5


def test_no_live_dependency_in_contracts():
    for fname in os.listdir(PA):
        fpath = os.path.join(PA, fname)
        if fname.endswith(".md") or fname.endswith(".json"):
            with open(fpath) as f:
                content = f.read()
            for pat in LIVE_PATTERNS:
                matches = re.findall(pat, content)
                filtered = [m for m in matches if not any(s in m for s in SAFE_DOMAINS)]
                assert not filtered, f"live dependency found in {fname}: {filtered}"


def test_live_dependency_added_fails():
    for fname in os.listdir(PA):
        fpath = os.path.join(PA, fname)
        if fname.endswith(".md") or fname.endswith(".json"):
            with open(fpath) as f:
                content = f.read()
            lines = [l for l in content.splitlines() if "json-schema.org" not in l]
            safe = "\n".join(lines)
            assert "http://" not in safe, f"http:// found in {fname}"
            for ip_match in re.finditer(r"\b(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b", content):
                assert False, f"IP address found in {fname}: {ip_match.group()}"
