"""Scan evidence files for potential secrets.

Item 14.3: Strengthened scanner for API keys, tokens, passwords, private keys,
connection strings, and credential-like patterns.
"""
import os, re, sys

SUSPICIOUS_PATTERNS = [
    r'api[_-]?key[\s"\':]+[A-Za-z0-9_]{16,}',
    r'secret[\s"\':]+[A-Za-z0-9_]{16,}',
    r'token[\s"\':]+[A-Za-z0-9_]{16,}',
    r'password[\s"\':]+[A-Za-z0-9_]{8,}',
    r'-----BEGIN (RSA |EC )?PRIVATE KEY-----',
    r'bearer[\s"\':]+[A-Za-z0-9_]{20,}',
    r'conn[_-]?str(ing)?[\s"\':]+[A-Za-z0-9_/:;@]{20,}',
    r'jdbc:[\w]+://[^\s"\']+',
    r'postgresql://[^\s"\':]+',
    r'mongodb[+srv]*://[^\s"\':]+',
    r'redis://[^\s"\':]+',
    r'ssh-rsa\s+A[A-Za-z0-9+/]{100,}',  # public keys aren't secrets but bulk embedded ones are
]

DEFAULT_ROOTS = [
    "L0", "L1", "L2",
    "tools", "tests",
    "schemas",
    ".agentx-init", "reports",
    "benchmarks",
    "examples",
    "scripts",
]


def scan(roots=None):
    issues = []
    exclude_patterns = ['secret_scan', 'golden_transcript', '__pycache__']
    for root in roots or DEFAULT_ROOTS:
        if not os.path.isdir(root):
            continue
        for dirpath, dirs, files in os.walk(root):
            rel = os.path.relpath(dirpath, root)
            parts = rel.replace(os.sep, '/').split('/')
            if any(ep in p for p in parts for ep in exclude_patterns):
                continue
            files = [f for f in files if not any(ep in f for ep in exclude_patterns)]
            for fn in files:
                fp = os.path.join(dirpath, fn)
                if _is_acceptable_path(fp):
                    continue
                try:
                    with open(fp, errors="ignore") as f:
                        content = f.read()
                    for i, pat in enumerate(SUSPICIOUS_PATTERNS):
                        if re.search(pat, content, re.IGNORECASE):
                            # Avoid flagging obvious test/example values
                            matched = re.search(pat, content, re.IGNORECASE)
                            val = matched.group(0) if matched else ""
                            if "example" in val.lower() or "placeholder" in val.lower():
                                continue
                            issues.append(f"{fp}: matches pattern {i}")
                except Exception:
                    pass
    return issues


def _is_acceptable_path(fp):
    norm = fp.replace(os.sep, '/')
    acceptable_paths = [
        'tools/docs/',
        '/test_sensitive_data_redactor.py',
        '/test_llm_worker_models.py',
        '/test_packaging_models.py',
        '/test_monitoring_utils.py',
        '/test_monitoring_redaction.py',
        '/test_scan_secrets_in_evidence.py',
        '/test_governance_benchmarks.py',
        'learning/outcome_models.py',
    ]
    return any(ap in norm for ap in acceptable_paths)


def main():
    roots = sys.argv[1:] if len(sys.argv) > 1 else None
    issues = scan(roots)
    if issues:
        print(f"SECRETS SCAN: {len(issues)} potential secret(s) found:"); [print(f"  - {i}") for i in issues]
    else:
        target = ", ".join(roots) if roots else ", ".join(DEFAULT_ROOTS)
        print(f"PASS: no secrets detected in {target}")


if __name__ == "__main__":
    main()
