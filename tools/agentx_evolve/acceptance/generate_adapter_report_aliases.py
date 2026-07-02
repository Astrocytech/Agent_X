from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

REPORTS = Path(__file__).resolve().parents[3] / ".agentx-init" / "reports"
MVP_DIR = REPORTS / "adapter-mvp"

ALIASES: list[tuple[Path, Path]] = [
    (MVP_DIR / "adapter_acceptance_matrix.json", REPORTS / "agentx_adapter_mvp_acceptance_matrix.json"),
    (MVP_DIR / "adapter_final_verdict.json", REPORTS / "agentx_adapter_mvp_final_verdict.json"),
    # Canonical names expected by final proof aggregation
    (MVP_DIR / "adapter_acceptance_matrix.json", MVP_DIR / "acceptance_matrix.json"),
    (MVP_DIR / "adapter_final_verdict.json", REPORTS / "functional_agentx_adapter_final_verdict.json"),
]


def compute_hash(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception:
        return "ERROR"


def main() -> int:
    errors = 0
    for src, dst in ALIASES:
        if not src.exists():
            print(f"ERROR: source missing: {src}")
            errors += 1
            continue

        src_hash = compute_hash(src)
        shutil.copy2(str(src), str(dst))
        dst_hash = compute_hash(dst)

        print(f"  {dst.name} -> {src.name} (hash: {src_hash[:12]}...)")

        if src_hash != dst_hash:
            print(f"  WARNING: {dst.name} hash diverged from {src.name}")
            print(f"    src hash: {src_hash}")
            print(f"    dst hash: {dst_hash}")
            errors += 1
        else:
            print(f"  OK: {dst.name} synchronized (hash matched)")

    if errors == 0:
        print("All adapter report aliases synchronized and hash-verified")
    else:
        print(f"{errors} alias error(s)")

    return errors


if __name__ == "__main__":
    exit(main())
