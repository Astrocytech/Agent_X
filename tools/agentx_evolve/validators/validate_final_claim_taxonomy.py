#!/usr/bin/env python3
import json, sys, os

CLAIM_FILE = os.path.join(".agentx-init", "reports", "final_claim_taxonomy.json")
REQUIRED_CATEGORIES = ["SUPPORTED_CLAIM", "BOUNDED_CLAIM", "DEFERRED_CLAIM", "FORBIDDEN_CLAIM", "UNSUPPORTED_CLAIM"]

def main():
    if not os.path.isfile(CLAIM_FILE):
        print(f"FAIL: Claim taxonomy file '{CLAIM_FILE}' not found")
        sys.exit(1)

    try:
        with open(CLAIM_FILE) as f:
            data = json.load(f)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"FAIL: '{CLAIM_FILE}' invalid JSON: {e}")
        sys.exit(1)

    errors = []
    categories = data.get("claims", data) if isinstance(data, dict) else {}

    for cat in REQUIRED_CATEGORIES:
        if cat not in categories:
            errors.append(f"Required category '{cat}' missing from claim taxonomy")

    forbidden_list = categories.get("FORBIDDEN_CLAIM", [])
    supported_list = categories.get("SUPPORTED_CLAIM", [])

    if isinstance(forbidden_list, list):
        for forbidden_item in forbidden_list:
            text = forbidden_item if isinstance(forbidden_item, str) else forbidden_item.get("claim", "")
            if not text:
                continue
            text_lower = text.lower()
            for supported_item in supported_list:
                s_text = supported_item if isinstance(supported_item, str) else supported_item.get("claim", "")
                s_lower = s_text.lower()
                if text_lower in s_lower or s_lower in text_lower:
                    errors.append(f"Forbidden claim '{text}' also appears in supported list (matched: '{s_text}')")

    if not isinstance(forbidden_list, list):
        errors.append("FORBIDDEN_CLAIM is not a list")

    if not isinstance(supported_list, list):
        errors.append("SUPPORTED_CLAIM is not a list")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)

    total = sum(len(v) if isinstance(v, list) else 0 for v in categories.values())
    print(f"PASS: claim taxonomy validates with {len(REQUIRED_CATEGORIES)} categories, {total} total claims, no forbidden/supported overlap")
    sys.exit(0)

if __name__ == "__main__":
    main()
