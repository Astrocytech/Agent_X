"""First real inverse-science use case: borderline umbrella weather improvement."""
from datetime import datetime, timezone
import json

def run_borderline_weather_use_case():
    """Demonstrate inverse-science on the umbrella borderline-weather case."""
    plan = {
        "target_capability": "umbrella_weather_improvement",
        "desired_output": "Improved recommendation accuracy for borderline precipitation (30-59% probability)",
        "hard_constraints": ["Must use deterministic fixture data", "No live API"],
        "soft_preferences": ["Better drizzle detection", "More granular probability bands"],
        "allowed_inputs": ["weather.fixture.read", "clothing.fixture.read"],
        "forbidden_inputs": ["shell.exec", "network.fetch", "git.push"],
        "identifiability": "HIGH - clear improvement metric (fixture accuracy)",
    }
    candidates = [
        {"id": "C1", "action": "Add 40-49% and 50-59% probability sub-bands to maybe rule", "priority": "high"},
        {"id": "C2", "action": "Improve drizzle detection with wind/humidity context", "priority": "medium"},
    ]
    ranked = sorted(candidates, key=lambda c: {"high": 0, "medium": 1}.get(c["priority"], 2))
    governance = {"decision": "allow_with_limits", "limits": ["fixture-only", "requires_review"]}
    observation = {"evidence_class": "SIMULATION", "result": "C1 would improve precision by ~15% on fixture data"}
    return {"plan": plan, "candidates": candidates, "ranked": ranked,
            "governance": governance, "observation": observation,
            "source": "inverse_science", "runtime_adoption": False}
