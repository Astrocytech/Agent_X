from __future__ import annotations

from pathlib import Path
from typing import Any

__all__ = [
    "detect_license",
    "generate_notice",
    "validate_license",
]

_KNOWN_LICENSES: dict[str, str] = {
    "MIT": "MIT License",
    "Apache-2.0": "Apache License 2.0",
    "GPL-3.0-only": "GNU General Public License v3.0 only",
    "GPL-3.0-or-later": "GNU General Public License v3.0 or later",
    "LGPL-3.0-only": "GNU Lesser General Public License v3.0 only",
    "BSD-2-Clause": "BSD 2-Clause License",
    "BSD-3-Clause": "BSD 3-Clause License",
    "MPL-2.0": "Mozilla Public License 2.0",
    "Unlicense": "The Unlicense",
    "CC0-1.0": "CC0 1.0 Universal",
}

_ALLOWED_LICENSES: set[str] = {
    "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause",
    "MPL-2.0", "Unlicense", "CC0-1.0",
}

_FORBIDDEN_LICENSES: set[str] = {
    "GPL-3.0-only", "GPL-3.0-or-later", "AGPL-3.0-only", "AGPL-3.0-or-later",
}

_LICENSE_FILE_NAMES = [
    "LICENSE", "LICENSE.txt", "LICENSE.md", "LICENSE.rst",
    "COPYING", "COPYING.txt", "COPYING.md",
]


def detect_license(path: str | Path) -> dict[str, Any]:
    root = Path(path)
    result: dict[str, Any] = {
        "path": str(root),
        "license_file": None,
        "license_name": None,
        "confidence": 0.0,
    }
    for name in _LICENSE_FILE_NAMES:
        license_path = root / name if root.is_dir() else root
        if root.is_dir():
            license_path = root / name
        else:
            license_path = root.parent / name if root.name not in _LICENSE_FILE_NAMES else root

        if root.is_dir():
            candidate = root / name
        elif root.parent:
            candidate = root.parent / name
        else:
            candidate = root / name

        if not candidate.exists():
            continue

        text = candidate.read_text(encoding="utf-8", errors="replace")[:2000]
        result["license_file"] = str(candidate)

        for spdx, full_name in _KNOWN_LICENSES.items():
            if spdx in text or full_name.split()[0] in text:
                result["license_name"] = spdx
                result["confidence"] = 0.8
                break

        if not result["license_name"]:
            result["license_name"] = "CUSTOM"
            result["confidence"] = 0.3

        break

    return result


def generate_notice(dependencies: list[dict[str, str]]) -> str:
    lines: list[str] = [
        "NOTICE",
        "======",
        "",
        "This package includes software from the following dependencies:",
        "",
    ]
    for dep in dependencies:
        name = dep.get("name", "unknown")
        version = dep.get("version", "")
        license_name = dep.get("license", "unknown")
        lines.append(f"- {name} {version} ({license_name})")
    lines.append("")
    lines.append("See LICENSE files for full license text.")
    return "\n".join(lines)


def validate_license(license_name: str) -> dict[str, Any]:
    result: dict[str, Any] = {
        "license_name": license_name,
        "allowed": False,
        "reason": "",
    }
    if license_name in _ALLOWED_LICENSES:
        result["allowed"] = True
        result["reason"] = "License is in the allowed list"
    elif license_name in _FORBIDDEN_LICENSES:
        result["allowed"] = False
        result["reason"] = f"License {license_name} is forbidden"
    else:
        result["allowed"] = False
        result["reason"] = f"License {license_name} is not recognized or not in the allowed list"
    return result
