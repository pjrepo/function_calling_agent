from agent import Agent

if __name__ == "__main__":
    agent = Agent()
    result = agent.run("What is 56 plus 98 and also how's the weather in London?")
    print("\n--- FINAL RESPONSE ---")
    print(result)
