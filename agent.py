from openai import OpenAI
import json


try:
    client = OpenAI()
except Exception:
    print("Error: Could not initialize OpenAI client.")
    exit()


SYSTEM_PROMPT = "You are a highly skilled math agent.  Only use the provided 'add' and 'subtract' tools for all calculations involving explicit numeric values. If the user does not give enough numbers to perform a calculation, do NOT call a tool—simply explain what information is missing."

user_prompt = "What is 456 minus x?"


def add(a: float | None, b: float | None) -> float | str:
    """Adds two numbers and returns the result."""
    # Runtime Validation for missing arguments
    if a is None or b is None:
        return "ERROR: Both 'a' and 'b' arguments are required for the add function. Please provide two numbers."
    try:
        # Runtime Validation for correct argument types
        return float(a) + float(b)
    except (ValueError, TypeError):
        return "ERROR: Inputs must be numerical for the add function."


def subtract(a: float | None, b: float | None) -> float | str:
    """Subtracts the second number (b) from the first (a) and returns the result."""
    if a is None or b is None:
        return "ERROR: Both 'a' and 'b' arguments are required for the subtract function. Please provide two numbers."
    try:
        return float(a) - float(b)
    except (ValueError, TypeError):
        return "ERROR: Inputs must be numerical for the subtract function."


available_functions = {
    "add": add,
    "subtract": subtract,
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add",
            "description": "Adds two numbers together. Use this for all addition operations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "The first number."},
                    "b": {"type": "number", "description": "The second number."},
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "subtract",
            "description": "Subtracts one number from another. Use this for all subtraction operations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "The number to subtract from.",
                    },
                    "b": {"type": "number", "description": "The number to subtract."},
                },
                "required": ["a", "b"],
            },
        },
    },
]

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": user_prompt},
]

print("Agent thinking (First Call: Requesting Tool)...")

response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=TOOLS,
    tool_choice="auto",
)

print(response.choices[0].message.content)


if response.choices[0].message.tool_calls:
    message = response.choices[0].message
    tool_calls = message.tool_calls

    function_name = tool_calls[0].function.name
    function_to_call = available_functions[function_name]
    function_args = tool_calls[0].function.arguments

    parsed_args = json.loads(function_args)

    function_result = function_to_call(
        a=parsed_args.get("a"),
        b=parsed_args.get("b"),
    )

    print(f"System executed function: {function_name}...")
    print(f"Result (or Error): {function_result}")

    messages.append(message)

    messages.append(
        {
            "tool_call_id": tool_calls[0].id,
            "role": "tool",
            "name": function_name,
            # IMPORTANT: The result must be sent back as a string in the 'content' field
            "content": str(function_result),
        }
    )

    print("\nAgent processing result and generating final response (Second Call)...")
    final_response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )

    print("\n--- FINAL AGENT RESPONSE ---")
    print(final_response.choices[0].message.content)
else:
    no_tool_call_message = response.choices[0].message
    print("\n--- MODEL TEXT RESPONSE (NO TOOL CALL) ---")
    print(no_tool_call_message.content)
