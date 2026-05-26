"""LocalConfigPort — in-process config dictionary."""

from __future__ import annotations

from typing import Any


class LocalConfigPort:
    runtime_safety_class = "production_seed_port"

    def get(self, key: str, default: Any = None) -> Any:
        cfg = {
            "max_files_per_patch": 3,
            "max_diff_lines": 300,
            "allow_fallback_keyword_planner": False,
        }
        return cfg.get(key, default)
