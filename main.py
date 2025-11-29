from agent import Agent

if __name__ == "__main__":
    agent = Agent()

    print("Agent is ready! Type 'exit' to quit.\n")

    while True:
        user_prompt = input("You: ")

        if user_prompt.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        result = agent.run(user_prompt)
        print("Agent:", result, "\n")
