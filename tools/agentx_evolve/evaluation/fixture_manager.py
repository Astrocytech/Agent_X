"""Canonical fixture/dataset/source-corpus management.

Item 37 (31.1/31.2): Central fixture registry with versioned
datasets for evaluation, regression, and sabotage testing.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class Fixture:
    fixture_id: str
    name: str
    description: str
    category: str = "generic"  # weather | planning | generic
    data: dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"
    source: str = ""


class FixtureManager:
    def __init__(self, storage_path: str | Path | None = None):
        self._fixtures: dict[str, Fixture] = {}
        self._storage = Path(storage_path) if storage_path else None

    def register(self, fixture: Fixture) -> None:
        if not fixture.fixture_id:
            fixture.fixture_id = hashlib.sha256(
                json.dumps(fixture.data, sort_keys=True).encode()
            ).hexdigest()[:16]
        self._fixtures[fixture.fixture_id] = fixture

    def get(self, fixture_id: str) -> Fixture | None:
        return self._fixtures.get(fixture_id)

    def find_by_category(self, category: str) -> list[Fixture]:
        return [f for f in self._fixtures.values() if f.category == category]

    def list_all(self) -> list[dict]:
        return [asdict(f) for f in self._fixtures.values()]

    def save(self, path: str | Path | None = None) -> None:
        p = Path(path) if path else self._storage
        if p:
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w") as f:
                json.dump(self.list_all(), f, indent=2, default=str)

    def load(self, path: str | Path) -> None:
        p = Path(path)
        if p.exists():
            with open(p) as f:
                for item in json.load(f):
                    self._fixtures[item["fixture_id"]] = Fixture(**item)


_weather_fixtures: list[Fixture] = [
    Fixture("wf-001", "sunny-clear",
            "Sunny conditions, no rain expected", "weather",
            {"temperature": 28, "humidity": 30, "wind_speed": 5, "conditions": "clear"},
            source="bom-observations-2026"),
    Fixture("wf-002", "rain-expected",
            "Rain expected with moderate precipitation", "weather",
            {"temperature": 18, "humidity": 85, "wind_speed": 15, "conditions": "rain",
             "precipitation_mm": 12},
            source="bom-observations-2026"),
    Fixture("wf-003", "borderline-drizzle",
            "Borderline conditions: light drizzle", "weather",
            {"temperature": 20, "humidity": 72, "wind_speed": 8, "conditions": "drizzle",
             "precipitation_mm": 1.5},
            source="bom-observations-2026"),
    Fixture("wf-004", "extreme-storm",
            "Extreme storm conditions", "weather",
            {"temperature": 15, "humidity": 95, "wind_speed": 50, "conditions": "storm",
             "precipitation_mm": 80},
            source="bom-observations-2026"),
    Fixture("wf-005", "lightning-risk",
            "Lightning risk with isolated showers", "weather",
            {"temperature": 22, "humidity": 78, "wind_speed": 12, "conditions": "isolated-showers",
             "lightning_risk": True},
            source="bom-observations-2026"),
]
