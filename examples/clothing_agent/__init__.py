from __future__ import annotations

from clothing_agent.agent import ClothingAgent


def get_clothing_advice(location: str) -> dict:
    return ClothingAgent().recommend(location)
