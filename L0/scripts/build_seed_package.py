"""Build and verify a minimal seed package using SEED_PACKAGE_MANIFEST.yaml."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import tempfile
import os
from pathlib import Path
from typing import List

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MANIFEST_PATH = REPO_ROOT / "L0/manifests/SEED_PACKAGE_MANIFEST.yaml"

EXCLUDED_ROOT_SURFACES = [
    "DATA",
    "app",
    "static",
    "server.py",
    "chat.py",
    "Dockerfile",
    "Dockerfile.cpu",
    "Dockerfile.gpu",
    "Makefile.full",
]

ANCILLARY_FILES = [
    "README.md",
    "pyproject.toml",
    "Makefile",
    "L0/manifests/SEED_PACKAGE_MANIFEST.yaml",
    "L0/manifests/CAPABILITY_MANIFEST.yaml",
    "L0/manifests/SEED_INVARIANTS.yaml",
    "L0/docs/EXTENSION_ABI.md",
    "L0/docs/SEED_ACCEPTANCE.md",
    "L0/docs/PUBLIC_CONTRACT_POLICY.md",
    "L1/docs/EVOLUTION_ACCEPTANCE.md",
    "LICENSE",
    "requirements/seed.txt",
    ".gitignore",
]


def _flatten_manifest(manifest: dict) -> List[str]:
    files: set[str] = set()
    for value in manifest.values():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    files.add(item)
    return sorted(files)


def _copy_tree(src: Path, dst: Path) -> None:
    if src.exists():
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"), dirs_exist_ok=True)


def _run(cmd: list[str], target: Path) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["PYTHONPATH"] = "L0/CODE:L0/scripts"
    return subprocess.run(
        cmd,
        cwd=target,
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
    )


def _tail(text: str, limit: int = 1000) -> str:
    return text[-limit:] if len(text) > limit else text


def _collect_dirs(files: List[str]) -> List[str]:
    seen: set[str] = set()
    dirs: list[str] = []
    for f in files:
        parts = f.split("/")
        for i in range(1, len(parts)):
            prefix = "/".join(parts[:i])
            if prefix not in seen:
                seen.add(prefix)
                dirs.append(prefix)
    return sorted(dirs, key=lambda d: (d.count("/"), d))


def main() -> int:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest_files = _flatten_manifest(manifest)

    seed_dirs = _collect_dirs(manifest_files)

    with tempfile.TemporaryDirectory(prefix="agent_x-seed-") as tmpdir:
        target = Path(tmpdir)
        print(f"Building seed package in {target}")

        for d in seed_dirs:
            _copy_tree(REPO_ROOT / d, target / d)

        _copy_tree(REPO_ROOT / "L0/scripts", target / "L0/scripts")

        for d in ["L0/tests/seed_l0", "requirements"]:
            src = REPO_ROOT / d
            if src.exists():
                _copy_tree(src, target / d)

        for f in ANCILLARY_FILES:
            src = REPO_ROOT / f
            if src.exists():
                dst = target / f
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

        (target / ".local").mkdir(parents=True, exist_ok=True)

        for surface in EXCLUDED_ROOT_SURFACES:
            if (target / surface).exists():
                print(f"FAIL: excluded root surface copied into seed package: {surface}")
                return 1

        boot = _run(
            [
                sys.executable,
                "-c",
                (
                    "from core_kernel.public.kernel_service import KernelService; "
                    "from core_kernel.models.kernel_requests import KernelTurnRequest; "
                    "svc=KernelService(); "
                    "out=svc.run_turn(KernelTurnRequest(user_input='what are you', "
                    "profile_id='generalist', session_id='seed-package')); "
                    "assert out.status.name == 'SUCCESS', str(out); "
                    "assert out.trace_id and out.policy_decision_id; "
                    "print(f'OK: seed package turn status={out.status.name} "
                    "trace={out.trace_id}')"
                ),
            ],
            target,
        )
        print(_tail(boot.stdout))
        if boot.returncode != 0:
            print(_tail(boot.stderr))
            print("FAIL: Seed package KernelService turn failed")
            return 1

        inv = _run(
            [sys.executable, "-m", "pytest", "L0/tests/seed_l0/", "-q", "--tb=short"],
            target,
        )
        print(_tail(inv.stdout))
        if inv.returncode != 0:
            print(_tail(inv.stderr))
            print("FAIL: Seed package tests failed")
            return 1

        if (target / "DATA").exists():
            print("FAIL: seed package generated or copied root DATA")
            return 1

        # Write hash of built package
        hasher = hashlib.sha256()
        for rel in sorted(manifest_files):
            path = target / rel
            if path.exists():
                hasher.update(path.read_bytes())
        hash_path = target / ".local" / "runtime" / "seed_package_hash.txt"
        hash_path.parent.mkdir(parents=True, exist_ok=True)
        hash_path.write_text(hasher.hexdigest() + "\n")
        print(f"OK: Seed package built and verified at {target}")
        print(f"Hash: {hasher.hexdigest()}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
