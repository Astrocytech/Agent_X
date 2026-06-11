from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class ReadinessCheckItem:
    name: str
    check_fn: Callable[[], bool]
    critical: bool = True
    message: str = ""

    def run(self) -> bool:
        try:
            return self.check_fn()
        except Exception:
            return False


@dataclass
class ReadinessResult:
    all_pass: bool = False
    items: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"all_pass": self.all_pass, "items": list(self.items)}


class MvpReadinessCheck:
    def __init__(self) -> None:
        self._checks: list[ReadinessCheckItem] = []

    def add_check(self, check: ReadinessCheckItem) -> None:
        self._checks.append(check)

    def add(self, name: str, fn: Callable[[], bool],
            critical: bool = True, message: str = "") -> None:
        self._checks.append(ReadinessCheckItem(name=name, check_fn=fn,
                                                critical=critical, message=message))

    def run_all(self) -> ReadinessResult:
        results = []
        all_pass = True
        for check in self._checks:
            ok = check.run()
            results.append({
                "name": check.name,
                "passed": ok,
                "critical": check.critical,
                "message": check.message if not ok else "",
            })
            if check.critical and not ok:
                all_pass = False
        return ReadinessResult(all_pass=all_pass, items=results)

    def is_ready(self) -> bool:
        return self.run_all().all_pass
