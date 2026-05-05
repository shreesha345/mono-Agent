from typing import List, Dict, Any, Optional, Union, Callable
from pydantic import BaseModel
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Model:
    """Base class for LLM models."""
    def __call__(self, messages: List[Dict[str, str]], stream: bool = False) -> Any:
        raise NotImplementedError

class OpenAIModel(Model):
    def __init__(
        self, 
        model_id: Optional[str] = None, 
        api_key: Optional[str] = None, 
        base_url: Optional[str] = None
    ):
        self.model_id = model_id or os.getenv("MONO_MODEL", "gpt-4o")
        self.client = OpenAI(
            api_key=api_key or os.getenv("MONO_API_KEY") or os.getenv("OPENAI_API_KEY") or "dummy_key",
            base_url=base_url or os.getenv("MONO_BASE_URL")
        )

    def __call__(self, messages: List[Dict[str, str]], stream: bool = False) -> str:
        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=messages,
            stream=stream
        )
        if stream:
            return response
        return response.choices[0].message.content

from .memory import MonoMemory

class MonoAgent:
    def __init__(
        self, 
        model: Union[str, Model] = "gpt-4o", 
        system_prompt: str = "You are a Manager Agent. Your job is to coordinate tasks. If you need a specialist, call the 'handoff' tool with the agent name.",
        tools: List[Callable] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        agent_id: str = "manager",
        memory_db: str = "mono_memory.db"
    ):
        # Handle string input for convenience
        if isinstance(model, str):
            self.model = OpenAIModel(model_id=model, api_key=api_key, base_url=base_url)
        else:
            self.model = model
            
        self.agent_id = agent_id
        self.system_prompt = system_prompt
        self.current_tools = tools or []
        
        # Initialize Memory
        self.memory = MonoMemory(db_path=memory_db)
        
        # Sync initial system prompt to memory if empty
        if not self.memory.get_history(self.agent_id):
            self.memory.add_message(self.agent_id, "system", self.system_prompt)

    def load_agent(self, agent_name: str, preserve_task: bool = True):
        """
        Load an agent definition from the Agents/ folder.
        If preserve_task is True, it keeps the last user message to maintain context.
        """
        file_path = f"Agents/{agent_name}.md"
        if not os.path.exists(file_path):
            # Try lowercase
            file_path = f"Agents/{agent_name.lower()}.md"
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Agent file {agent_name}.md not found in Agents/ folder.")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        if "---TOOLS---" in content:
            system_prompt, tools_json = content.split("---TOOLS---")
            try:
                self.current_tools = json.loads(tools_json.strip())
            except json.JSONDecodeError:
                print(f"Warning: Could not parse tools for {agent_name}")
                self.current_tools = []
        else:
            system_prompt = content
            self.current_tools = []

        # Get the last user message (the task) before clearing
        last_task = None
        if preserve_task:
            history = self.memory.get_history(self.agent_id)
            user_messages = [m for m in history if m["role"] == "user"]
            if user_messages:
                last_task = user_messages[-1]["content"]

        # Erase memory and set new system prompt for the specialist
        self.memory.clear_history(self.agent_id)
        
        self.system_prompt = system_prompt.strip()
        self.memory.add_message(self.agent_id, "system", self.system_prompt)
        
        # Re-inject the task so the new agent knows what to do
        if last_task:
            self.memory.add_message(self.agent_id, "user", last_task)
            print(f"--- MonoAgent context swapped: Specialist '{agent_name}' inherited the task ---")
        else:
            print(f"--- MonoAgent context swapped to specialist: {agent_name} ---")

    @staticmethod
    def generate_tool_schema(func: Callable) -> Dict[str, Any]:
        """Convert a Python function into an OpenAI-compatible tool schema (Static)."""
        import inspect
        
        name = func.__name__
        doc = inspect.getdoc(func) or "No description provided."
        sig = inspect.signature(func)
        
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            # Basic type mapping
            type_map = {
                int: "integer",
                str: "string",
                bool: "boolean",
                float: "number",
                dict: "object",
                list: "array"
            }
            param_type = type_map.get(param.annotation, "string")
            
            properties[param_name] = {
                "type": param_type,
                "description": f"Parameter {param_name}"
            }
            
            if param.default is inspect.Parameter.empty:
                required.append(param_name)
        
        return {
            "name": name,
            "description": doc,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }

    @staticmethod
    def import_tool(tool_name: str) -> Callable:
        """Dynamically import a tool function from the Tools/ folder (Static)."""
        import importlib.util
        import sys
        
        file_path = f"Tools/{tool_name}.py"
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Tool file {tool_name}.py not found in Tools/ folder.")
            
        module_name = f"tools.{tool_name}"
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        if hasattr(module, "run"):
            func = getattr(module, "run")
            func.__name__ = tool_name
            return func
        elif hasattr(module, tool_name):
            return getattr(module, tool_name)
        else:
            raise AttributeError(f"Module {tool_name} must have a 'run' function or a '{tool_name}' function.")

    def create_agent_file(self, name: str, instructions: str, tool_names: List[str]):
        """
        Helper to create an agent markdown file.
        Imports tools from Tools/ folder and generates schemas automatically.
        """
        os.makedirs("Agents", exist_ok=True)
        file_path = f"Agents/{name}.md"
        
        tool_schemas = []
        for t_name in tool_names:
            func = self.import_tool(t_name)
            tool_schemas.append(self.generate_tool_schema(func))
        
        content = f"# {name} Agent\n\n{instructions.strip()}\n\n---TOOLS---\n"
        content += json.dumps(tool_schemas, indent=2)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"--- Agent structure saved to: {file_path} ---")
        return file_path

    def run(self, user_input: str, stream: bool = False) -> str:
        # Add user message to persistent memory
        self.memory.add_message(self.agent_id, "user", user_input)
        
        # Get full history for the model
        history = self.memory.get_history(self.agent_id)
        
        # In a real tool-calling loop, we would handle self.current_tools here
        response = self.model(history, stream=stream)
        
        if stream:
            return response
            
        # Add assistant response to persistent memory
        self.memory.add_message(self.agent_id, "assistant", response)
        return response
