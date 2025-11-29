import json
from openai import OpenAI

from config import SYSTEM_PROMPT
from tools import AVAILABLE_FUNCTIONS, TOOLS


class Agent:
    def __init__(self, model: str = "gpt-4o"):
        try:
            self.client = OpenAI()
        except Exception:
            print("Error: Could not initialize OpenAI client.")
            exit()

        self.model = model

    def _execute_tool(self, tool_call):
        """Executes a tool call by name."""
        function_name = tool_call.function.name

        if function_name not in AVAILABLE_FUNCTIONS:
            return f"ERROR: Unknown tool '{function_name}'."

        try:
            function_args = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError as e:
            return f"ERROR: Invalid JSON for {function_name}. Details: {e}"

        return AVAILABLE_FUNCTIONS[function_name](**function_args)

    def run(self, user_prompt: str) -> str:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        while True:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )

            response_msg = response.choices[0].message

            # If no tool call → final output
            if not response_msg.tool_calls:
                return response_msg.content

            messages.append(response_msg)

            # Execute tools
            for tool_call in response_msg.tool_calls:
                tool_result = self._execute_tool(tool_call)

                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": tool_call.function.name,
                        "content": str(tool_result),
                    }
                )

            # Second pass: model produces final answer
            final = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )

            return final.choices[0].message.content
