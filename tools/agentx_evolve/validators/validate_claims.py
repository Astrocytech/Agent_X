#!/usr/bin/env python3
"""Validate final claim assertions."""
import json, sys, os

FORBIDDEN_CLAIMS = [
    "universal agent", "instantly universal", "production-ready",
    "bypass human review", "fully implemented scriptor",
    "inverse science is mandatory", "proves general intelligence",
    "unrestricted autonomy", "live api default"
]

NEGATION_PREFIXES = ["not ", "no ", "cannot ", "can't ", "doesn't ", "isn't ", "aren't ", "won't ", "never "]

def is_negated(text, forbidden):
    idx = text.find(forbidden)
    if idx == -1:
        return False
    start = max(0, idx - 20)
    prefix = text[start:idx]
    for neg in NEGATION_PREFIXES:
        if neg in prefix:
            return True
    return False

def validate(path):
    errors = []
    with open(path) as f:
        data = json.load(f)
    claims = data.get("claims", data.get("final_claim", ""))
    if isinstance(claims, str):
        claims = [claims]
    for i, claim in enumerate(claims):
        text = claim.lower() if isinstance(claim, str) else claim.get("claim", "").lower()
        for forbidden in FORBIDDEN_CLAIMS:
            if forbidden in text and not is_negated(text, forbidden):
                errors.append(f"Claim {i}: contains forbidden claim: '{forbidden}'")
    return errors

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else ".agentx-init/five_document_closure/final/five_document_claim_validation.json"
    if not os.path.exists(path):
        print(f"FAIL: {path} not found"); sys.exit(1)
    errors = validate(path)
    if errors:
        print(f"FAIL: {len(errors)} forbidden claim(s)"); [print(f"  - {e}") for e in errors]
        sys.exit(1)
    print(f"PASS: {path} validates")

if __name__ == "__main__":
    main()
