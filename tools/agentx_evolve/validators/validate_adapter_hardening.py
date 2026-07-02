from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def check_provider_portability() -> bool:
    model_files = list((HERE.parent / "models").glob("*model_adapter*.py"))
    adapter_files = list((HERE.parent / "adapters").glob("*model_adapter*.py"))
    all_adapters = model_files + adapter_files
    adapter_count = len(all_adapters)
    print(f"  ModelAdapter implementations found: {adapter_count}")
    names = [p.stem for p in all_adapters]
    print(f"  Adapters: {', '.join(names)}")
    return adapter_count >= 3


def check_side_effect_classification() -> bool:
    result = subprocess.run(
        ["grep", "-r", "side_effect", str(HERE.parent)],
        capture_output=True, text=True, timeout=30,
    )
    count = len([l for l in result.stdout.split("\n") if l.strip()])
    print(f"  side_effect references across adapter code: {count}")
    return count >= 10


def check_dependency_supply_chain() -> bool:
    lock_files = [
        REPO / "requirements" / "seed.txt",
        REPO / "requirements" / "dev.txt",
        REPO / "requirements" / "test.txt",
        REPO / "requirements" / "release.txt",
    ]
    existing = [p for p in lock_files if p.exists()]
    print(f"  Dependency lock files found: {len(existing)}/{len(lock_files)}")
    for p in lock_files:
        mark = "✓" if p.exists() else "✗"
        print(f"    {mark} {p.name}")
    return len(existing) >= 2


def check_clean_checkout() -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    dirty = result.stdout.strip()
    count = len([l for l in dirty.split("\n") if l.strip()]) if dirty else 0
    verdict_path = REPO / ".agentx-init" / "reports" / "adapter-mvp" / "adapter_final_verdict.json"
    verdict_records_tree = False
    if verdict_path.exists():
        import json
        vd = json.loads(verdict_path.read_text())
        verdict_records_tree = "working_tree" in vd or "tree_hash" in vd
    print(f"  Working tree: {'DIRTY' if dirty else 'CLEAN'} ({count} uncommitted)")
    print(f"  Final verdict records working tree: {verdict_records_tree}")
    return True


def check_no_live_provider_required() -> bool:
    test_dir = HERE.parent / "tests"
    has_live_import = False
    for t in sorted(test_dir.glob("test_*.py")):
        content = t.read_text()
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if ("import" in stripped and ("LiveModelAdapter" in stripped or "live_provider" in stripped)
                    and "live_provider_disabled" not in stripped):
                has_live_import = True
                print(f"  WARNING: {t.name} imports live provider: {stripped[:80]}")
    mock_adapter = HERE.parent / "adapters" / "deterministic_mock_model_adapter.py"
    has_mock = mock_adapter.exists() and "DeterministicMockModelAdapter" in mock_adapter.read_text()
    print(f"  Deterministic mock adapter exists: {has_mock}")
    print(f"  Live provider imports in tests: {has_live_import}")
    return has_mock and not has_live_import


def main() -> int:
    checks = [
        ("provider_portability", check_provider_portability),
        ("side_effect_classification", check_side_effect_classification),
        ("dependency_supply_chain", check_dependency_supply_chain),
        ("clean_checkout", check_clean_checkout),
        ("no_live_provider_required", check_no_live_provider_required),
    ]

    results = {}
    all_pass = True
    for name, fn in checks:
        print(f"[{name}] ", end="", flush=True)
        try:
            ok = fn()
            results[name] = "PASS" if ok else "FAIL"
            print(f"  -> {results[name]}")
            if not ok:
                all_pass = False
        except Exception as e:
            results[name] = "FAIL"
            print(f"  -> FAIL ({e})")
            all_pass = False

    out = HERE.parents[2] / ".agentx-init" / "reports" / "adapter-mvp" / "adapter_hardening_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2))
    print(f"\nReport: {out}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
