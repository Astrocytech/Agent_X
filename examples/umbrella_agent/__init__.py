from umbrella_agent.runtime import UmbrellaAgentRuntime


def ask_umbrella(location: str, date: str = "today") -> dict:
    return UmbrellaAgentRuntime().answer(location, date)
