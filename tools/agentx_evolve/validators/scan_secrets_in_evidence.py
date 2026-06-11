#!/usr/bin/env python3
"""Scan evidence files for potential secrets."""
import os, re, sys

SUSPICIOUS_PATTERNS = [
    r'api[_-]?key[\s"\':]+[A-Za-z0-9_]{16,}',
    r'secret[\s"\':]+[A-Za-z0-9_]{16,}',
    r'token[\s"\':]+[A-Za-z0-9_]{16,}',
    r'password[\s"\':]+[A-Za-z0-9_]{8,}',
    r'-----BEGIN (RSA |EC )?PRIVATE KEY-----',
]

DEFAULT_ROOTS = [".agentx-init", "reports"]

def scan(roots=None):
    issues = []
    exclude_patterns = ['secret_scan', 'golden_transcript']
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
                try:
                    with open(fp, errors="ignore") as f:
                        content = f.read()
                    for i, pat in enumerate(SUSPICIOUS_PATTERNS):
                        if re.search(pat, content, re.IGNORECASE):
                            issues.append(f"{fp}: matches pattern {i}")
                except:
                    pass
    return issues

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
