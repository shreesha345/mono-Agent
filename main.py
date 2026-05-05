from mono_agent import MonoAgent

def main():
    # 1. Initialize the Agent
    # Note: Ensure OPENAI_API_KEY is set in your environment
    agent = MonoAgent()

    # 2. Load the Hello World Specialist
    agent.load_agent("HelloWorld")

    # 3. Run the Agent
    print("--- Running HelloWorld Agent ---")
    response = agent.run("Please greet the world!")
    print(f"Agent Response: {response}")

if __name__ == "__main__":
    main()
