import os
import sys
import json
import shutil
from .agent import MonoAgent

def setup_env():
    """Interactive setup for .env file."""
    print("\n--- Model Configuration ---")
    provider = input("Select provider (openai/ollama/groq/other): ").lower()
    
    config = {
        "MONO_API_KEY": "",
        "MONO_BASE_URL": "",
        "MONO_MODEL": ""
    }

    if provider == "openai":
        config["MONO_API_KEY"] = input("Enter OpenAI API Key: ")
        config["MONO_MODEL"] = "gpt-4o"
    elif provider == "ollama":
        config["MONO_API_KEY"] = "ollama"
        config["MONO_BASE_URL"] = "http://localhost:11434/v1"
        config["MONO_MODEL"] = input("Enter Ollama model name (e.g. llama3): ")
    elif provider == "groq":
        config["MONO_API_KEY"] = input("Enter Groq API Key: ")
        config["MONO_BASE_URL"] = "https://api.groq.com/openai/v1"
        config["MONO_MODEL"] = "llama-3.3-70b-versatile"
    else:
        config["MONO_API_KEY"] = input("Enter API Key: ")
        config["MONO_BASE_URL"] = input("Enter Base URL: ")
        config["MONO_MODEL"] = input("Enter Model Name: ")

    with open(".env", "w", encoding="utf-8") as f:
        for key, value in config.items():
            f.write(f"{key}={value}\n")
    print("--- Configuration saved to .env ---")

import time

def status_check(message, condition):
    """Print a message with a dotted loading animation and a success/fail status."""
    sys.stdout.write(f"{message:.<40}")
    sys.stdout.flush()
    time.sleep(0.3) # Snappy dynamic feel
    
    if condition:
        print(" [ SUCCESS ]")
    else:
        print(" [ FAILED  ]")
    return condition

def test_project():
    """Perform a dry run to test the setup."""
    print("\n--- Mono-Agent Dry Run ---")
    
    # 1. Check directories
    status_check("Checking Agents directory", os.path.exists("Agents"))
    status_check("Checking Tools directory", os.path.exists("Tools"))

    # 2. Check .env
    status_check("Checking .env file", os.path.exists(".env"))

    # 3. Check HelloWorld Agent
    status_check("Checking HelloWorld agent", os.path.exists("Agents/HelloWorld.md"))

    # 4. Check HelloTool
    status_check("Checking hello_tool", os.path.exists("Tools/hello_tool.py"))

    print("\nDry run complete. If all checks passed, you are ready to run 'uv run main.py'!")

def scaffold_project():
    """Scaffold a new Mono-Agent project structure without live client initialization."""
    print("--- Scaffolding Mono-Agent Project ---")
    
    # 1. Create Directories
    os.makedirs("Agents", exist_ok=True)
    os.makedirs("Tools", exist_ok=True)
    
    # 2. Create a sample Tool
    hello_tool_path = "Tools/hello_tool.py"
    if not os.path.exists(hello_tool_path):
        with open(hello_tool_path, "w", encoding="utf-8") as f:
            f.write('def run(name: str) -> str:\n')
            f.write('    """A simple tool that says hello."""\n')
            f.write('    return f"Hello, {name} from the Mono-Agent framework!"\n')
        print(f"Created: {hello_tool_path}")

    # 3. Create a sample Agent Markdown file (Directly, no LLM needed)
    agent_name = "HelloWorld"
    agent_file = f"Agents/{agent_name}.md"
    if not os.path.exists(agent_file):
        # We use the static methods from MonoAgent to stay consistent
        func = MonoAgent.import_tool("hello_tool")
        schema = MonoAgent.generate_tool_schema(func)
        
        instructions = "You are a friendly greeting agent. Use the hello_tool to greet the user by name."
        content = f"# {agent_name} Agent\n\n{instructions}\n\n---TOOLS---\n"
        content += json.dumps([schema], indent=2)
        
        with open(agent_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Created: {agent_file}")
    
    # 4. Create main.py
    main_py_path = "main.py"
    if not os.path.exists(main_py_path):
        with open(main_py_path, "w", encoding="utf-8") as f:
            f.write('from mono_agent import MonoAgent\n\n')
            f.write('def main():\n')
            f.write('    # 1. Initialize the Agent\n')
            f.write('    agent = MonoAgent()\n\n')
            f.write('    # 2. Load the Hello World Specialist\n')
            f.write('    agent.load_agent("HelloWorld")\n\n')
            f.write('    # 3. Run the Agent\n')
            f.write('    print("--- Running HelloWorld Agent ---")\n')
            f.write('    response = agent.run("Please greet the world!")\n')
            f.write('    print(f"Agent Response: {response}")\n\n')
            f.write('if __name__ == "__main__":\n')
            f.write('    main()\n')
        print(f"Created: {main_py_path}")

    # 5. Setup .env
    setup_env()

    print("\nProject setup complete! Run it with: uv run main.py")

def main():
    if len(sys.argv) < 2:
        print("Usage: mono <command>")
        print("Commands:")
        print("  create    Scaffold a new project structure and configure model")
        print("  test      Perform a dry run to verify the setup")
        return

    command = sys.argv[1]
    if command == "create":
        scaffold_project()
    elif command == "test":
        test_project()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
