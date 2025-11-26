"""
Legacy MemoryManager - Backwards compatible wrapper for the new memory system.

This module provides backwards compatibility with existing code while
using the new comprehensive memory architecture under the hood.

For new code, use the memory submodule directly:
    from agent_medha.memory import SharedMemoryStore, get_memory_store
"""

import os
# Force removal of ADC if present to avoid conflicts
if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
    del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

from typing import List, Dict, Any, Optional
from langchain_core.documents import Document

# Import the new memory system
from agent_medha.memory.store import get_memory_store, SharedMemoryStore
from agent_medha.memory.base import MemoryType, MemoryScope, MemoryDomain


class MemoryManager:
    """
    Legacy MemoryManager providing backwards compatibility.
    
    This wraps the new SharedMemoryStore to maintain API compatibility
    with existing code while using the new comprehensive memory system.
    
    For new code, prefer using SharedMemoryStore directly:
        from agent_medha.memory import get_memory_store
        store = get_memory_store()
    """
    
    def __init__(self, collection_name: str = "agent_medha_memory"):
        self.collection_name = collection_name
        self._store = get_memory_store()
    
    def add_memory(
        self, 
        text: str, 
        memory_type: str = "episodic", 
        agent_id: str = "global", 
        metadata: Dict[str, Any] = None
    ):
        """
        Adds a memory to the vector store.
        
        Args:
            text: The memory content.
            memory_type: 'episodic', 'semantic', or 'procedural'.
            agent_id: The ID of the agent owning this memory ('global' for shared).
            metadata: Additional metadata.
        """
        # Map to new memory system
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
        elif memory_type == "procedural":
            # For procedural, store as a simple pattern
            from agent_medha.memory.procedural import Procedure
            proc = Procedure(
                id=f"legacy_{hash(text)}",
                name="Legacy Procedure",
                description=text,
                trigger_pattern=text,
                agent_id=agent_id if agent_id != "global" else "supervisor",
            )
            self._store.add_procedure(proc, agent_id=agent_id)
    
    def search_memory(
        self, 
        query: str, 
        memory_type: str = None, 
        agent_id: str = None, 
        limit: int = 5
    ) -> List[Document]:
        """
        Searches for relevant memories with filtering.
        
        Args:
            query: The search query.
            memory_type: Filter by memory type (optional).
            agent_id: Filter by agent ID (optional). If None, searches global + all.
            limit: Number of results.
        """
        # Use unified recall for comprehensive search
        agent = agent_id if agent_id else "supervisor"
        
        # Determine which memory types to search
        memory_types = None
        if memory_type:
            if memory_type == "episodic":
                memory_types = [MemoryType.EPISODIC]
            elif memory_type == "semantic":
                memory_types = [MemoryType.SEMANTIC]
            elif memory_type == "procedural":
                memory_types = [MemoryType.PROCEDURAL]
        
        results = self._store.recall(
            query=query,
            agent_id=agent,
            memory_types=memory_types,
            limit=limit
        )
        
        # Convert to Documents for backwards compatibility
        documents = []
        
        for mem_type, records in results.items():
            for record in records:
                if hasattr(record, 'to_dict'):
                    data = record.to_dict()
                    documents.append(Document(
                        page_content=data.get("content", data.get("description", "")),
                        metadata=data
                    ))
                elif hasattr(record, 'content'):
                    documents.append(Document(
                        page_content=record.content,
                        metadata={"memory_type": mem_type}
                    ))
        
        return documents[:limit]
    
    def clear_memory(self):
        """Clears all memories (useful for testing)."""
        # Note: This is a no-op in the new system to prevent accidental data loss
        # For testing, use individual memory system clear methods
        pass
    
    # ==================== NEW API ====================
    
    @property
    def store(self) -> SharedMemoryStore:
        """Access the underlying SharedMemoryStore for new features."""
        return self._store
