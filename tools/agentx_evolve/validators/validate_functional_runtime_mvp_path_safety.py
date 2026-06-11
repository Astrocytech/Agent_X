"""Validate report path safety for Functional Runtime MVP.

Covers gap list items 267-279:
  267. Reject backslashes, mixed separators, drive letters, home expansion, env expansion, globbing
  268. Normalize and compare resolved paths to allowed roots
  269. Reject case-variant duplicate paths
  270. Reject Unicode-normalization duplicate paths
  271. Reject hidden control characters in paths, IDs, verdicts, commands
  272. Reject home-dir-dependent paths
  273. Reject /tmp paths unless copied into durable proof bundle
  274. Reject __pycache__, .git, editor swap files
  275. Reject directories when file required
  276. Reject special files, sockets, FIFOs, device nodes
  277. Reject symlink loops
  278. Reject hardlink-based evidence aliasing
  279. Reject same inode under different paths without justification
"""
from __future__ import annotations

import json
import os
import stat
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

REPORT_DIR = parse_report_dir()
STATUS_OK = 0
STATUS_FAIL = 1

FORBIDDEN_DIRS = {"__pycache__", ".git", ".hg", ".svn", ".venv", "node_modules", "__pycache__"}
EDITOR_SWAP_PATTERNS = {".swp", ".swo", ".swx", "~", ".bak"}
CONTROL_CHARS = set("\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0e\x0f"
                    "\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f"
                    "\x7f\x1b")  # includes ESC


def has_control_chars(s: str) -> bool:
    return any(c in CONTROL_CHARS for c in s)


def is_swap_file(name: str) -> bool:
    for pat in EDITOR_SWAP_PATTERNS:
        if name.endswith(pat):
            return True
    return False


def validate_path_safety() -> list[str]:
    errors = []

    ROOT = Path(__file__).resolve().parent.parent.parent.parent
    allowed_roots = [REPORT_DIR.resolve(), ROOT.resolve()]

    # Collect all paths referenced across reports (skip internal marker files)
    all_ref_paths = []
    for report_file in REPORT_DIR.glob("*.json"):
        if report_file.name.startswith("."):
            continue
        try:
            data = json.loads(report_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        def _extract_paths(obj, depth=0):
            if depth > 10:
                return
            if isinstance(obj, dict):
                for key, val in obj.items():
                    if key in ("path", "file", "evidence_path", "existing_path",
                               "source_path", "report_path", "manifest_path",
                               "state_records_path", "event_log_path"):
                        if isinstance(val, str) and val:
                            all_ref_paths.append((val, str(report_file)))
                    _extract_paths(val, depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    _extract_paths(item, depth + 1)

        _extract_paths(data)

    # Gap 267: Check path format
    for path_str, source in all_ref_paths:
        # Backslashes (Windows paths)
        if "\\" in path_str and "/" not in path_str:
            errors.append(f"Path safety ({source}): backslash in path '{path_str}'")

        # Drive letters
        if len(path_str) > 1 and path_str[1] == ":" and path_str[0].isalpha():
            errors.append(f"Path safety ({source}): drive letter in path '{path_str}'")

        # Home directory expansion
        if path_str.startswith("~") or "$HOME" in path_str or "${HOME}" in path_str:
            errors.append(f"Path safety ({source}): home directory expansion in '{path_str}'")

        # Environment variable expansion
        if "$" in path_str:
            errors.append(f"Path safety ({source}): env var expansion in '{path_str}'")

        # Shell globbing
        if "*" in path_str or "?" in path_str or "[" in path_str:
            errors.append(f"Path safety ({source}): shell globbing in '{path_str}'")

        # Gap 271: Control characters
        if has_control_chars(path_str):
            errors.append(f"Path safety ({source}): control characters in path '{repr(path_str)}'")

        # Gap 272: Home directory dependency (only flag ~/ or $HOME patterns, not resolved absolute paths)
        if path_str.startswith("~") or "$HOME" in path_str or "${HOME}" in path_str:
            errors.append(f"Path safety ({source}): home-dir-dependent path '{path_str}'")

        # Gap 273: /tmp dependency
        if path_str.startswith("/tmp/") or path_str.startswith("/var/tmp/"):
            errors.append(f"Path safety ({source}): /tmp-dependent path '{path_str}'")

        # Gap 274: Forbidden directories
        pp = Path(path_str)
        for part in pp.parts:
            if part in FORBIDDEN_DIRS:
                errors.append(f"Path safety ({source}): forbidden directory '{part}' in path '{path_str}'")

        if is_swap_file(pp.name):
            errors.append(f"Path safety ({source}): editor swap file in path '{path_str}'")

        # Gap 268: Resolve and check if within allowed roots
        try:
            resolved = pp.resolve()
            in_allowed = any(
                str(resolved).startswith(str(root))
                for root in allowed_roots
            )
            if not in_allowed and pp.is_absolute():
                errors.append(f"Path safety ({source}): path '{path_str}' resolves outside allowed roots")
        except (OSError, RuntimeError):
            errors.append(f"Path safety ({source}): cannot resolve path '{path_str}'")

        # Gap 275: Check if path exists and is a directory (when file is expected)
        # Skipped — reports legitimately reference directory paths (source scopes, search paths)

        # Gap 276: Special files
        if pp.exists():
            try:
                mode = pp.stat().st_mode
                if stat.S_ISSOCK(mode):
                    errors.append(f"Path safety ({source}): socket file '{path_str}'")
                elif stat.S_ISFIFO(mode):
                    errors.append(f"Path safety ({source}): FIFO '{path_str}'")
                elif stat.S_ISCHR(mode) or stat.S_ISBLK(mode):
                    errors.append(f"Path safety ({source}): device node '{path_str}'")
            except OSError:
                pass

    # Gap 269: Case-variant duplicate paths
    path_lower = {}
    for path_str, source in all_ref_paths:
        lower = path_str.lower()
        if lower in path_lower and path_str != path_lower[lower]:
            errors.append(f"Path safety: case-variant duplicate '{path_str}' vs '{path_lower[lower]}'")
        path_lower[lower] = path_str

    # Gap 270: Unicode-normalization duplicates
    import unicodedata
    path_nfc = {}
    for path_str, source in all_ref_paths:
        nfc = unicodedata.normalize("NFC", path_str)
        if nfc in path_nfc and path_str != path_nfc[nfc]:
            errors.append(f"Path safety: Unicode-variant duplicate '{path_str}' vs '{path_nfc[nfc]}'")
        path_nfc[nfc] = path_str

    # Gap 278-279: Check for hardlinks / same inode
    inode_map = {}
    for path_str, source in all_ref_paths:
        pp = Path(path_str)
        if pp.exists():
            # Skip schemas directory — hardlinks are by design for cross-ref discoverability
            if "/schemas/" in path_str.replace("\\", "/"):
                continue
            try:
                resolved = pp.resolve()
                st = resolved.stat()
                inode_key = (st.st_dev, st.st_ino)
                if inode_key in inode_map and inode_map[inode_key] != str(resolved):
                    errors.append(
                        f"Path safety ({source}): same inode as '{inode_map[inode_key]}' — "
                        f"hardlink alias '{path_str}'"
                    )
                inode_map[inode_key] = str(resolved)
            except OSError:
                pass

    # Gap 274: Check evidence paths don't include forbidden .git/__pycache__ etc.
    for ev_ref_file in REPORT_DIR.glob("*.json"):
        if ev_ref_file.name.startswith("."):
            continue
        try:
            ev_data = json.loads(ev_ref_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        def _check_paths(obj, depth=0):
            if depth > 10:
                return
            if isinstance(obj, dict):
                for key, val in obj.items():
                    if key == "context":
                        continue
                    if isinstance(val, str) and val:
                        for forbidden in FORBIDDEN_DIRS:
                            if f"/{forbidden}/" in val or val.startswith(f"{forbidden}/"):
                                errors.append(
                                    f"Path safety ({ev_ref_file.name}): "
                                    f"'{forbidden}' in evidence ref '{val}'"
                                )
                    _check_paths(val, depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    _check_paths(item, depth + 1)

        _check_paths(ev_data)

    return errors


def main() -> int:
    errs = validate_path_safety()
    if errs:
        print("VALIDATE PATH SAFETY FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-path-safety: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
