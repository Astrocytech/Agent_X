from __future__ import annotations

import logging

from agentx_evolve.providers.weather_fixture import (
    WeatherFixtureProvider,
    FIXTURES,
    FIXTURE_DATE_UTC,
)

__all__ = ["WeatherFixtureReadTool", "FIXTURES"]

logger = logging.getLogger(__name__)


class WeatherFixtureReadTool:
    """Delegates to the canonical WeatherFixtureProvider.

    This L0 seed tool is a thin wrapper that preserves the
    weather.fixture.read capability interface while the
    implementation lives outside L0.
    """

    FIXTURE_DATE_UTC = FIXTURE_DATE_UTC

    def __init__(self) -> None:
        self._provider = WeatherFixtureProvider(simulate_delay=True)

    def __call__(self, location: str, date: str | None = None) -> dict:
        logger.info("[weather.fixture.read] Delegating to WeatherFixtureProvider")
        return self._provider.fetch(location, date)
