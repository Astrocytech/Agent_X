from __future__ import annotations

from clothing_advice_agent.runtime import ClothingAdviceRuntime


def ask_clothing(location: str) -> dict:
    return ClothingAdviceRuntime().answer(location)
