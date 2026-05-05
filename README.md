# Mono-Agent Framework

A minimal, file-based agent framework inspired by smolagents and LangGraph, optimized for offline use and context efficiency.

## Features

- **CLI Scaffolding**: Quickly start projects with `mono create`.
- **Markdown Agents**: Define agent personas and tools in simple Markdown files.
- **Auto-Tool Sync**: Python functions in `Tools/` are automatically converted to OpenAI JSON schemas.
- **Context Efficient**: Automatically wipes previous agent context during handoffs to save tokens.
- **Persistent Memory**: SQLite-based conversation history and Mem0 fact extraction.
- **Human-in-the-Loop**: Built-in support for human validation and steering.

## Installation

Install the framework using your preferred package manager:

```bash
# Using uv (Recommended)
uv add mono-agent

# Using pip
pip install mono-agent
```

## Quick Start

Once installed, you can set up a new project in seconds using the CLI:

1. **Scaffold your project**:
   This command creates the `Agents/` and `Tools/` folders, a sample agent, and a `main.py` entry point. It also helps you configure your LLM provider.
   ```bash
   mono create
   ```

2. **Test your setup**:
   Perform a dynamic dry run to ensure all files and configurations are correct.
   ```bash
   mono test
   ```

3. **Run your agent**:
   ```bash
   python main.py
   ```

## Creating a Specialist Agent

1. **Create a tool** in `Tools/my_tool.py`:
   ```python
   def run(query: str) -> str:
       """Does something cool."""
       return f"Result for {query}"
   ```

2. **Generate the Agent file**:
   ```python
   from mono_agent import MonoAgent
   agent = MonoAgent()
   agent.create_agent_file(
       name="MySpecialist",
       instructions="You are a specialist...",
       tool_names=["my_tool"]
   )
   ```

3. **Load and Run**:
   ```python
   agent.load_agent("MySpecialist")
   agent.run("Do the cool thing.")
   ```

## License

MIT License. See [LICENSE](LICENSE) for details.
