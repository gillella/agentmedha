"""
agentMedha Shared Memory System

A comprehensive memory architecture supporting:
- Working Memory: Short-term, session-scoped context
- Episodic Memory: Time-stamped experiences and interactions
- Semantic Memory: Facts, knowledge, entities, and relationships
- Procedural Memory: Learned patterns, rules, and workflows

Multi-tenant with three access levels:
- GLOBAL: All agents can read/write
- DOMAIN: Agents in same domain (email, social, finance, etc.)
- PRIVATE: Agent-specific memories
"""

from .base import MemoryScope, MemoryType, MemoryRecord, MemoryDomain
from .working import WorkingMemory
from .episodic import EpisodicMemory
from .semantic import SemanticMemory
from .procedural import ProceduralMemory
from .store import SharedMemoryStore, get_memory_store


# Legacy MemoryManager for backwards compatibility
class MemoryManager:
    """
    Legacy MemoryManager providing backwards compatibility.
    For new code, use SharedMemoryStore directly via get_memory_store().
    """
    
    def __init__(self, collection_name: str = "agent_medha_memory"):
        self.collection_name = collection_name
        self._store = get_memory_store()
    
    def add_memory(self, text: str, memory_type: str = "episodic", 
                   agent_id: str = "global", metadata: dict = None):
        """Adds a memory to the store."""
        if memory_type == "episodic":
            self._store.remember_interaction(
                content=text,
                agent_id=agent_id if agent_id != "global" else "supervisor",
                scope=MemoryScope.GLOBAL if agent_id == "global" else MemoryScope.PRIVATE,
                metadata=metadata
            )
        elif memory_type == "semantic":
            self._store.learn_fact(
                fact=text,
                agent_id=agent_id if agent_id != "global" else "supervisor",
                scope=MemoryScope.GLOBAL if agent_id == "global" else MemoryScope.PRIVATE
            )
    
    def search_memory(self, query: str, memory_type: str = None, 
                      agent_id: str = None, limit: int = 5):
        """Searches for relevant memories."""
        agent = agent_id if agent_id else "supervisor"
        memory_types = None
        if memory_type:
            type_map = {"episodic": MemoryType.EPISODIC, "semantic": MemoryType.SEMANTIC}
            if memory_type in type_map:
                memory_types = [type_map[memory_type]]
        
        return self._store.recall(query=query, agent_id=agent, 
                                  memory_types=memory_types, limit=limit)
    
    @property
    def store(self) -> SharedMemoryStore:
        """Access the underlying SharedMemoryStore."""
        return self._store


__all__ = [
    "MemoryScope",
    "MemoryType", 
    "MemoryRecord",
    "MemoryDomain",
    "MemoryManager",
    "WorkingMemory",
    "EpisodicMemory",
    "SemanticMemory",
    "ProceduralMemory",
    "SharedMemoryStore",
    "get_memory_store",
]
