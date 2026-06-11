# Example Agents

## 1. Umbrella Agent
`ask_umbrella(location)` → Should I bring an umbrella?
- 11 fixture locations
- Uses LLM for decision interpretation
- Fallback: Python rule engine

## 2. Clothing Advice Agent
`ask_clothing(location)` → What should I wear today?
- 15 fixture cases (temperature bands + weather conditions)
- Rule-based + safe_failure

## 3. Daily Planning Agent
`ask_planning(scenario_id)` → What should I prioritize today?
- 15 fixture scenarios (urgency/effort/dependency combinations)
- Prioritization: urgency > effort > deadline
- Circular dependency detection
