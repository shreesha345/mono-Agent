import sqlite3
import json
import os
from typing import List, Dict, Any, Optional
from mem0 import Memory

class MonoMemory:
    def __init__(self, db_path: str = "mono_memory.db"):
        self.db_path = db_path
        self._init_db()
        # Initialize Mem0 for long-term fact memory (Local/Offline mode)
        # By default, Mem0 can use local storage for vectors if configured
        self.fact_memory = Memory()

    def _init_db(self):
        """Initialize SQLite for state and conversation persistence."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Table for agent state (HITL/Loops)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_state (
                    agent_id TEXT PRIMARY KEY,
                    current_node TEXT,
                    state_data TEXT,
                    is_paused INTEGER DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Table for conversation history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT,
                    role TEXT,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    # --- Conversation Memory (Short-term) ---
    def add_message(self, agent_id: str, role: str, content: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversation_history (agent_id, role, content) VALUES (?, ?, ?)",
                (agent_id, role, content)
            )
            conn.commit()

    def get_history(self, agent_id: str) -> List[Dict[str, str]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content FROM conversation_history WHERE agent_id = ? ORDER BY created_at ASC",
                (agent_id,)
            )
            return [{"role": r, "content": c} for r, c in cursor.fetchall()]

    def clear_history(self, agent_id: str):
        """Wipe the entire conversation history for a specific agent."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conversation_history WHERE agent_id = ?", (agent_id,))
            conn.commit()
        print(f"--- History cleared for agent: {agent_id} ---")

    # --- Fact Memory (Long-term) ---
    def store_fact(self, user_id: str, text: str):
        self.fact_memory.add(text, user_id=user_id)

    def search_facts(self, query: str, user_id: str):
        return self.fact_memory.search(query, user_id=user_id)

    # --- Loop/State Memory (HITL) ---
    def save_agent_state(self, agent_id: str, node: str, state: Dict[str, Any], is_paused: bool = False):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO agent_state (agent_id, current_node, state_data, is_paused)
                VALUES (?, ?, ?, ?)
            """, (agent_id, node, json.dumps(state), 1 if is_paused else 0))
            conn.commit()

    def load_agent_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT current_node, state_data, is_paused FROM agent_state WHERE agent_id = ?", (agent_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "current_node": row[0],
                    "state": json.loads(row[1]),
                    "is_paused": bool(row[2])
                }
            return None
