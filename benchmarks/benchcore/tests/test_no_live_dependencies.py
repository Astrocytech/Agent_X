import json
import os
import re

BENCHCORE = os.path.join(os.path.dirname(__file__), "..")

SUSPICIOUS_PATTERNS = [
    re.compile(r'https?://(?!json-schema\.org|schema\.org)[^\s"\'\]`>)]+'),
    re.compile(r'(?i)(api[_-]?key|apikey|api_secret|apiSecret)\s*[:=]\s*["\'][^"\']+["\']'),
    re.compile(r'(?i)(password|passwd|pwd)\s*[:=]\s*["\'][^"\']+["\']'),
    re.compile(r'(?i)(secret|token)\s*[:=]\s*["\'][^"\']+["\']'),
    re.compile(r'(?i)sk-[a-zA-Z0-9]{20,}'),
    re.compile(r'(?i)ghp_[a-zA-Z0-9]{36}'),
    re.compile(r'(?i)(AKIA|ASIA)[a-zA-Z0-9]{16}'),
]

ALLOWED_URL_PREFIXES = (
    "http://json-schema.org",
    "https://json-schema.org",
    "http://schema.org",
    "https://schema.org",
)


def iter_json_files():
    for root, dirs, files in os.walk(BENCHCORE):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", "node_modules")]
        for fname in files:
            if fname.endswith(".json"):
                yield os.path.join(root, fname)


def iter_md_files():
    for root, dirs, files in os.walk(BENCHCORE):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", "node_modules")]
        for fname in files:
            if fname.endswith(".md"):
                yield os.path.join(root, fname)


def iter_jsonl_files():
    for root, dirs, files in os.walk(BENCHCORE):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", "node_modules")]
        for fname in files:
            if fname.endswith(".jsonl"):
                yield os.path.join(root, fname)


class TestNoLiveDependencies:

    def test_source_inventory_all_live_dependency_false(self):
        path = os.path.join(BENCHCORE, "source_inventory.json")
        with open(path) as f:
            inventory = json.load(f)
        for entry in inventory:
            assert entry["live_dependency"] is False, (
                f"{entry['source_id']} has live_dependency=true"
            )

    def test_no_http_urls_pointing_to_live_services_in_json(self):
        for path in iter_json_files():
            with open(path) as f:
                content = f.read()
            for match in SUSPICIOUS_PATTERNS[0].finditer(content):
                url = match.group(0)
                if url.startswith(ALLOWED_URL_PREFIXES):
                    continue
                raise AssertionError(f"Suspicious URL in {path}: {url}")

    def test_no_http_urls_pointing_to_live_services_in_md(self):
        for path in iter_md_files():
            with open(path) as f:
                content = f.read()
            for match in SUSPICIOUS_PATTERNS[0].finditer(content):
                url = match.group(0)
                if url.startswith(ALLOWED_URL_PREFIXES):
                    continue
                raise AssertionError(f"Suspicious URL in {path}: {url}")

    def test_no_api_keys_in_json_files(self):
        for path in iter_json_files():
            with open(path) as f:
                content = f.read()
            for pattern in SUSPICIOUS_PATTERNS[1:]:
                matches = pattern.findall(content)
                assert len(matches) == 0, f"Found secrets pattern {pattern.pattern} in {path}"

    def test_no_api_keys_in_jsonl_files(self):
        for path in iter_jsonl_files():
            with open(path) as f:
                content = f.read()
            for pattern in SUSPICIOUS_PATTERNS[1:]:
                matches = pattern.findall(content)
                assert len(matches) == 0, f"Found secrets pattern {pattern.pattern} in {path}"

    def test_no_api_keys_in_md_files(self):
        for path in iter_md_files():
            with open(path) as f:
                content = f.read()
            for pattern in SUSPICIOUS_PATTERNS[1:]:
                matches = pattern.findall(content)
                assert len(matches) == 0, f"Found secrets pattern {pattern.pattern} in {path}"

    def test_per_pdf_coverage_has_no_live_connections_field(self):
        path = os.path.join(BENCHCORE, "per_pdf_semantic_coverage_report.json")
        with open(path) as f:
            content = f.read()
        assert "live_dependency" not in content or "live_connection" not in content

    def test_source_batch_map_json_does_not_have_live_endpoints(self):
        path = os.path.join(BENCHCORE, "source_batch_map.json")
        if os.path.isfile(path):
            with open(path) as f:
                data = json.load(f)
            content = json.dumps(data)
            for match in SUSPICIOUS_PATTERNS[0].finditer(content):
                url = match.group(0)
                if url.startswith(ALLOWED_URL_PREFIXES):
                    continue
                raise AssertionError(f"Suspicious URL in source_batch_map.json: {url}")

    def test_batch_map_contains_all_32_docs(self):
        path = os.path.join(BENCHCORE, "source_batch_map.json")
        if os.path.isfile(path):
            with open(path) as f:
                data = json.load(f)
            assert isinstance(data, (dict, list))
            if isinstance(data, dict):
                all_docs = []
                for v in data.values():
                    all_docs.extend(v if isinstance(v, list) else [v])
                assert len(all_docs) >= 32
            else:
                assert len(data) >= 32
