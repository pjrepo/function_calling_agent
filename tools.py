import json

# -----------------------------
# TOOL IMPLEMENTATIONS
# -----------------------------


def add(a: float | None, b: float | None) -> float | str:
    if a is None or b is None:
        return "ERROR: Both 'a' and 'b' are required."
    try:
        return float(a) + float(b)
    except (ValueError, TypeError):
        return "ERROR: Inputs must be numerical."


def subtract(a: float | None, b: float | None) -> float | str:
    if a is None or b is None:
        return "ERROR: Both 'a' and 'b' are required."
    try:
        return float(a) - float(b)
    except (ValueError, TypeError):
        return "ERROR: Inputs must be numerical."


def get_current_weather(city: str, unit: str = "celsius") -> str:
    city_lower = city.lower()

    if "tokyo" in city_lower:
        temp = 15 if unit.lower() == "celsius" else 59
        return f"The weather in Tokyo is {temp}°{unit} and sunny ☀️."

    if "london" in city_lower:
        temp = 8 if unit.lower() == "celsius" else 46
        return f"The weather in London is {temp}°{unit} and cloudy ☁️."

    return f"Weather data for {city} not available."


# -----------------------------
# TOOL REGISTRY
# -----------------------------

AVAILABLE_FUNCTIONS = {
    "add": add,
    "subtract": subtract,
    "get_current_weather": get_current_weather,
}

# -----------------------------
# TOOL JSON SCHEMAS
# -----------------------------

ADD_SCHEMA = {
    "type": "function",
    "function": {
        "name": "add",
        "description": "Adds two numbers.",
        "parameters": {
            "type": "object",
            "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
            "required": ["a", "b"],
        },
    },
}

SUBTRACT_SCHEMA = {
    "type": "function",
    "function": {
        "name": "subtract",
        "description": "Subtracts one number from another.",
        "parameters": {
            "type": "object",
            "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
            "required": ["a", "b"],
        },
    },
}

WEATHER_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_current_weather",
        "description": "Gets the current weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["city"],
        },
    },
}

TOOLS = [ADD_SCHEMA, SUBTRACT_SCHEMA, WEATHER_TOOL_SCHEMA]
