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

```bash
uv init
uv add pydantic openai mem0ai
# Or just install this package
uv sync
```

## Quick Start

1. **Scaffold your project**:
   ```bash
   uv run mono create
   ```

2. **Run the example**:
   ```bash
   # Make sure your OPENAI_API_KEY is set
   uv run main.py
   ```

## Creating an Agent

1. Create a tool in `Tools/my_tool.py`:
   ```python
   def run(query: str) -> str:
       """Does something cool."""
       return f"Result for {query}"
   ```

2. Use the framework to generate the Agent Markdown:
   ```python
   from mono_agent import MonoAgent
   agent = MonoAgent()
   agent.create_agent_file(
       name="MySpecialist",
       instructions="You are a specialist...",
       tool_names=["my_tool"]
   )
   ```

3. Load and run:
   ```python
   agent.load_agent("MySpecialist")
   agent.run("Do the cool thing.")
   ```
