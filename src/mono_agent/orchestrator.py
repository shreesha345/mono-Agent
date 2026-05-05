from typing import List, Dict, Any, Optional, Union
from .agent import MonoAgent
from .memory import MonoMemory

class MonoOrchestrator:
    def __init__(self, memory_db: str = "mono_memory.db"):
        self.memory = MonoMemory(db_path=memory_db)
        self.agents: Dict[str, MonoAgent] = {}

    def add_agent(self, agent: MonoAgent):
        self.agents[agent.agent_id] = agent
        return self

    def run_sequential(self, initial_input: str, agent_order: List[str]) -> str:
        """Agent-in-the-loop: Sequential handoff."""
        current_input = initial_input
        for agent_id in agent_order:
            if agent_id not in self.agents:
                raise ValueError(f"Agent {agent_id} not found")
            
            print(f"--- Handing off to {agent_id} ---")
            current_input = self.agents[agent_id].run(current_input)
            
        return current_input

    def run_with_hitl(self, agent_id: str, initial_input: str, validation_node: str = "human"):
        """Human-in-the-loop: Agent runs, then waits for human validation."""
        agent = self.agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")

        result = agent.run(initial_input)
        
        # Simple HITL check
        print(f"\n[Agent {agent_id} Result]: {result}")
        feedback = agent.ask_human("Do you approve this result? (yes/no/feedback)")
        
        if feedback.lower() == "yes":
            return result
        else:
            # Re-run with feedback
            return agent.run(f"User feedback: {feedback}. Please adjust accordingly.")
