from openai import OpenAI
import json

# -------------------------------------------------------
# Initialize OpenAI Client
# -------------------------------------------------------
try:
    client = OpenAI()
except Exception:
    print("Error: Could not initialize OpenAI client.")
    exit()


# -------------------------------------------------------
# System Prompt
# -------------------------------------------------------
SYSTEM_PROMPT = (
    "You are a highly skilled math agent. "
    "Only use the provided 'add' and 'subtract' tools for all calculations involving explicit numeric values. "
    "If the user does not give enough numbers to perform a calculation, do NOT call a tool—simply explain what information is missing. "
    "Use 'get_current_weather' whenever the user asks about weather."
)


# -------------------------------------------------------
# Tool Implementations (Python functions)
# -------------------------------------------------------
def add(a: float | None, b: float | None) -> float | str:
    """Adds two numbers and returns the result."""
    if a is None or b is None:
        return "ERROR: Both 'a' and 'b' are required."
    try:
        return float(a) + float(b)
    except (ValueError, TypeError):
        return "ERROR: Inputs must be numerical."


def subtract(a: float | None, b: float | None) -> float | str:
    """Subtracts b from a and returns the result."""
    if a is None or b is None:
        return "ERROR: Both 'a' and 'b' are required."
    try:
        return float(a) - float(b)
    except (ValueError, TypeError):
        return "ERROR: Inputs must be numerical."


def get_current_weather(city: str, unit: str = "celsius") -> str:
    """Simulated weather lookup."""
    city_lower = city.lower()

    if "tokyo" in city_lower:
        temp = 15 if unit.lower() == "celsius" else 59
        return f"The weather in Tokyo is {temp}°{unit} and sunny ☀️."

    if "london" in city_lower:
        temp = 8 if unit.lower() == "celsius" else 46
        return f"The weather in London is {temp}°{unit} and cloudy ☁️."

    return f"Weather data for {city} not available."


available_functions = {
    "add": add,
    "subtract": subtract,
    "get_current_weather": get_current_weather,
}


# -------------------------------------------------------
# Tool Schemas
# -------------------------------------------------------
ADD_SCHEMA = {
    "type": "function",
    "function": {
        "name": "add",
        "description": "Adds two numbers.",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"},
            },
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
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"},
            },
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
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                },
            },
            "required": ["city"],
        },
    },
}

TOOLS = [ADD_SCHEMA, SUBTRACT_SCHEMA, WEATHER_TOOL_SCHEMA]


# -------------------------------------------------------
# MAIN AGENT FUNCTION
# -------------------------------------------------------
def run_agent(user_prompt: str) -> str:
    """
    Runs a full agent cycle:
    - Sends prompt to model
    - If tool call requested → executes tool
    - Sends result back to model
    - Returns final text response
    """

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    # --- FIRST CALL: Decide if tool is needed ---
    first_response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )

    first_msg = first_response.choices[0].message

    # NO tool call → return answer directly
    if not first_msg.tool_calls:
        return first_msg.content

    # --- TOOL CALL HAPPENS ---
    tool_call = first_msg.tool_calls[0]
    function_name = tool_call.function.name
    python_function = available_functions[function_name]
    function_args = json.loads(tool_call.function.arguments)

    # Execute Python function
    # try:
    function_result = python_function(**function_args)
    # except TypeError:
    #     function_result = python_function(
    #         function_args.get("a"),
    #         function_args.get("b"),
    #     )

    # Add tool call + result to conversation
    messages.append(first_msg)
    messages.append(
        {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": function_name,
            "content": str(function_result),
        }
    )

    # --- SECOND CALL: Model produces final answer ---
    final_response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )

    return final_response.choices[0].message.content


# -------------------------------------------------------
# Example Usage
# -------------------------------------------------------
if __name__ == "__main__":
    result = run_agent("How is the weather in Delhi?")
    print("\n--- FINAL RESPONSE ---")
    print(result)
