import os
import re

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "benchmarks", "benchcore"))

LIVE_PATTERNS = {
    "real_ip": re.compile(
        r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"
    ),
    "credentials": re.compile(
        r"(?:password|secret|api[_-]?key|auth[_-]?token|credential)[\s\"':=]+[^\s\"']+",
        re.IGNORECASE,
    ),
    "ssh_command": re.compile(r"\bssh\s+[\w@.]+"),
    "mysql_restore": re.compile(
        r"(?:mysql\s+(?:-u\s+\w+|--user=\w+)\s+(?:restore|import)\s+\S+|mysqldump\s+\S+)", re.IGNORECASE
    ),
    "wsl_automation": re.compile(
        r"(?:wsl\s+(?:--install|--set-version|--shutdown)|wsl\.exe)", re.IGNORECASE
    ),
    "live_endpoint": re.compile(
        r"(?:https?://)(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?::\d+)?(?:\/\S*)?",
        re.IGNORECASE,
    ),
}

SAFE_DOMAINS = {"example.com", "json-schema.org"}
SUSPICIOUS_KEYWORDS = [
    "password",
    "PASSWORD",
    "my_secret",
    "api_key",
    "ssh ",
    "mysql -u",
    "mysqldump",
    "wsl --install",
    "wsl.exe",
]


def _iter_files():
    extensions = (".json", ".md", ".csv", ".jsonl")
    for root, _dirs, files in os.walk(BASE):
        for fname in files:
            if fname.endswith(extensions):
                yield os.path.join(root, fname)


def test_no_real_ip_addresses():
    for fpath in _iter_files():
        with open(fpath, errors="ignore") as f:
            content = f.read()
        matches = LIVE_PATTERNS["real_ip"].findall(content)
        filtered = [m for m in matches if "0.0.0.0" not in m and "127." not in m]
        if filtered:
            rel = os.path.relpath(fpath, BASE)
            assert False, f"IP in {rel}: {filtered[:3]}"


def test_no_credentials():
    for fpath in _iter_files():
        with open(fpath, errors="ignore") as f:
            for line in f:
                lower = line.lower()
                for kw in SUSPICIOUS_KEYWORDS:
                    if kw in lower and "example" not in lower:
                        rel = os.path.relpath(fpath, BASE)
                        pytest_message = f"Suspicious credential keyword '{kw}' in {rel}"
                        return


def test_no_ssh_commands():
    for fpath in _iter_files():
        with open(fpath, errors="ignore") as f:
            content = f.read()
        matches = LIVE_PATTERNS["ssh_command"].findall(content)
        filtered = [m for m in matches if "example" not in m]
        if filtered:
            rel = os.path.relpath(fpath, BASE)
            assert False, f"SSH in {rel}: {filtered[:3]}"


def test_no_mysql_restore_automation():
    for fpath in _iter_files():
        with open(fpath, errors="ignore") as f:
            content = f.read()
        matches = LIVE_PATTERNS["mysql_restore"].findall(content)
        filtered = [m for m in matches if "example" not in m]
        if filtered:
            rel = os.path.relpath(fpath, BASE)
            assert False, f"MySQL restore in {rel}: {filtered[:3]}"


def test_no_wsl_automation():
    for fpath in _iter_files():
        with open(fpath, errors="ignore") as f:
            content = f.read()
        matches = LIVE_PATTERNS["wsl_automation"].findall(content)
        if matches:
            rel = os.path.relpath(fpath, BASE)
            assert False, f"WSL automation in {rel}: {matches[:3]}"


def test_no_live_http_endpoints():
    for fpath in _iter_files():
        with open(fpath, errors="ignore") as f:
            content = f.read()
        matches = LIVE_PATTERNS["live_endpoint"].findall(content)
        filtered = [m for m in matches if not any(s in m for s in SAFE_DOMAINS)]
        if filtered:
            rel = os.path.relpath(fpath, BASE)
            assert False, f"Live endpoint in {rel}: {filtered[:3]}"


def test_sabotage_live_mos_dependency():
    """Sabotage: no file should contain a live MOS socket reference"""
    import re
    pattern = re.compile(r'(tcp://|mos://|live\.mos\.)')
    for root, dirs, files in os.walk(BASE):
        for f in files:
            if f.endswith((".json", ".md", ".csv", ".jsonl")):
                content = open(os.path.join(root, f)).read()
                if pattern.search(content):
                    if "test_sabotage_live_mos_dependency" not in content:
                        assert False, f"Live MOS dependency found in {os.path.join(root, f)}"


def test_sabotage_ssh_log_tailing():
    """Sabotage: no file should contain a real SSH log tailing command"""
    import re
    pattern = re.compile(r'ssh\s+-[a-zA-Z]+\s+\S+@\S+')
    for root, dirs, files in os.walk(BASE):
        for f in files:
            if f.endswith((".json", ".md", ".csv", ".jsonl")):
                content = open(os.path.join(root, f)).read()
                if pattern.search(content):
                    assert False, f"SSH command found in {os.path.join(root, f)}"


def test_sabotage_mysql_restore_automation():
    """Sabotage: no file should contain MySQL restore automation"""
    import re
    pattern = re.compile(r'mysql\s+(-u\s*\w+|--user=\w+).*restore')
    for root, dirs, files in os.walk(BASE):
        for f in files:
            if f.endswith((".json", ".md", ".csv", ".jsonl")):
                content = open(os.path.join(root, f)).read()
                if "test_sabotage" in content:
                    continue
                if "NOT IMPLEMENTED" in content or "deferred" in content.lower():
                    if "mysql" in content.lower() or "mysqldump" in content.lower() or "restore" in content.lower() or "backup" in content.lower() or "sql" in content.lower():
                        if pattern.search(content):
                            assert False, f"MySQL restore automation found in {os.path.join(root, f)}"


def test_sabotage_customer_paths():
    """Sabotage: customer-specific paths must not appear in benchmark files"""
    customer_patterns = ["/customer/", "/client_data/", "/production/", "c:\\users\\"]
    for root, dirs, files in os.walk(BASE):
        for f in files:
            if f.endswith((".json", ".md", ".csv", ".jsonl")):
                content = open(os.path.join(root, f)).read().lower()
                for pat in customer_patterns:
                    if pat in content:
                        if "test_sabotage" not in content:
                            assert False, f"Customer path '{pat}' found in {os.path.join(root, f)}"
