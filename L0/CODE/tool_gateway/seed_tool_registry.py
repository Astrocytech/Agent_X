"""Seed tool registry — registers L0 seed tools.

Currently exposes:
  - seed.emit_answer          — final answer output
  - weather.fixture.read      — deterministic weather fixture data
  - clothing.fixture.read     — deterministic clothing/weather fixture data
  - planning.fixture.read     — deterministic daily-planning fixture data

read_text, write_scratch, search_memory, and run_local_check are not part
of the minimal governed seed surface.
"""

from __future__ import annotations

from typing import Any

from tool_gateway.tool_contracts import ToolContract, ToolRiskLevel
from tool_gateway.seed_tools.emit_answer import EmitAnswerTool
from tool_gateway.seed_tools.weather_fixture_read import WeatherFixtureReadTool
from tool_gateway.seed_tools.clothing_fixture_read import ClothingFixtureReadTool
from tool_gateway.seed_tools.planning_fixture_read import PlanningFixtureReadTool


def _seed_emit_answer() -> ToolContract:
    return ToolContract(
        name="seed.emit_answer",
        description="Produce the final answer output for a seed run",
        risk_level=ToolRiskLevel.LOW,
        input_schema={
            "type": "object",
            "properties": {"answer": {"type": "string"}, "run_id": {"type": "string"}},
            "required": ["answer"],
        },
        side_effect_class="read_only",
        permission_scope="seed.answer.emit",
        requires_approval=False,
        rollback_behavior="not_applicable",
        evidence_required=["run_id", "request_id"],
    )


def _seed_weather_fixture_read() -> ToolContract:
    return ToolContract(
        name="weather.fixture.read",
        description="Read deterministic weather fixture data for umbrella recommendations",
        risk_level=ToolRiskLevel.LOW,
        input_schema={
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"},
                "date": {"type": "string", "description": "ISO-8601 date string (defaults to 2026-06-10 fixture date if omitted)"},
            },
            "required": ["location"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {"type": "object"},
                "error": {"type": "string"},
            },
        },
        side_effect_class="read_only",
        permission_scope="weather.fixture.read",
        requires_approval=False,
        rollback_behavior="not_applicable",
        evidence_required=["location", "date"],
    )


def _seed_clothing_fixture_read() -> ToolContract:
    return ToolContract(
        name="clothing.fixture.read",
        description="Read deterministic weather fixture data for clothing advice",
        risk_level=ToolRiskLevel.LOW,
        input_schema={
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Location name"},
            },
            "required": ["location"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {"type": "object"},
                "error": {"type": "string"},
            },
        },
        side_effect_class="read_only",
        permission_scope="clothing.fixture.read",
        requires_approval=False,
        rollback_behavior="not_applicable",
        evidence_required=["location"],
    )


def _seed_planning_fixture_read() -> ToolContract:
    return ToolContract(
        name="planning.fixture.read",
        description="Read deterministic task-list fixture data for daily planning",
        risk_level=ToolRiskLevel.LOW,
        input_schema={
            "type": "object",
            "properties": {
                "scenario_id": {"type": "string", "description": "Scenario identifier"},
            },
            "required": ["scenario_id"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {"type": "object"},
                "error": {"type": "string"},
            },
        },
        side_effect_class="read_only",
        permission_scope="planning.fixture.read",
        requires_approval=False,
        rollback_behavior="not_applicable",
        evidence_required=["scenario_id"],
    )


DEFAULT_SEED_TOOL_DEFS: list[tuple[ToolContract, Any]] = [
    (_seed_emit_answer(), EmitAnswerTool()),
    (_seed_weather_fixture_read(), WeatherFixtureReadTool()),
    (_seed_clothing_fixture_read(), ClothingFixtureReadTool()),
    (_seed_planning_fixture_read(), PlanningFixtureReadTool()),
]

CONTROLLED_SEED_TOOL_DEFS: list[tuple[ToolContract, Any]] = []


def register_seed_tools(registry) -> None:
    for contract, handler in DEFAULT_SEED_TOOL_DEFS:
        registry.register(contract, handler)
    for contract, handler in CONTROLLED_SEED_TOOL_DEFS:
        registry.register(contract, handler)


def list_seed_tool_names() -> list[str]:
    names = [c.name for c, _h in DEFAULT_SEED_TOOL_DEFS]
    names.extend(c.name for c, _h in CONTROLLED_SEED_TOOL_DEFS)
    return names
