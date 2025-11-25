"""
Working Memory - Short-term, session-scoped memory.

Working memory holds:
- Current conversation context
- Active task state
- Scratchpad for reasoning
- Temporary data being processed

This memory is:
- Fast (in-memory or Redis)
- Session-scoped (cleared when conversation ends)
- Limited capacity (bounded size)
"""

import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import OrderedDict
from dataclasses import dataclass, field
import threading

from .base import MemoryRecord, MemoryType, MemoryScope, MemoryDomain


@dataclass
class WorkingMemorySlot:
    """A single slot in working memory."""
    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    access_count: int = 0
    
    def is_expired(self) -> bool:
        """Check if this slot has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at


class WorkingMemory:
    """
    Short-term working memory for active sessions.
    
    Features:
    - In-memory storage (fast access)
    - Session isolation
    - TTL support for automatic expiration
    - Bounded capacity with LRU eviction
    - Scratchpad for reasoning
    """
    
    MAX_SLOTS_PER_SESSION = 100
    DEFAULT_TTL_MINUTES = 60
    
    def __init__(self):
        self._sessions: Dict[str, OrderedDict[str, WorkingMemorySlot]] = {}
        self._session_metadata: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def get_or_create_session(self, session_id: str, agent_id: str = "supervisor") -> str:
        """Get existing session or create new one."""
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = OrderedDict()
                self._session_metadata[session_id] = {
                    "agent_id": agent_id,
                    "created_at": datetime.now().isoformat(),
                    "last_accessed": datetime.now().isoformat(),
                }
            return session_id
    
    def set(
        self, 
        session_id: str, 
        key: str, 
        value: Any,
        ttl_minutes: Optional[int] = None
    ) -> None:
        """
        Store a value in working memory.
        
        Args:
            session_id: The session identifier
            key: The key to store under
            value: The value to store
            ttl_minutes: Optional TTL in minutes
        """
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = OrderedDict()
                self._session_metadata[session_id] = {
                    "created_at": datetime.now().isoformat(),
                    "last_accessed": datetime.now().isoformat(),
                }
            
            expires_at = None
            if ttl_minutes:
                expires_at = datetime.now() + timedelta(minutes=ttl_minutes)
            
            # Check capacity and evict LRU if needed
            if len(self._sessions[session_id]) >= self.MAX_SLOTS_PER_SESSION:
                # Remove oldest item
                self._sessions[session_id].popitem(last=False)
            
            slot = WorkingMemorySlot(
                key=key,
                value=value,
                expires_at=expires_at
            )
            self._sessions[session_id][key] = slot
            self._sessions[session_id].move_to_end(key)
    
    def get(self, session_id: str, key: str, default: Any = None) -> Any:
        """
        Retrieve a value from working memory.
        
        Args:
            session_id: The session identifier
            key: The key to retrieve
            default: Default value if not found
            
        Returns:
            The stored value or default
        """
        with self._lock:
            if session_id not in self._sessions:
                return default
            
            if key not in self._sessions[session_id]:
                return default
            
            slot = self._sessions[session_id][key]
            
            # Check expiration
            if slot.is_expired():
                del self._sessions[session_id][key]
                return default
            
            # Update access tracking
            slot.access_count += 1
            self._sessions[session_id].move_to_end(key)
            
            return slot.value
    
    def delete(self, session_id: str, key: str) -> bool:
        """Delete a key from working memory."""
        with self._lock:
            if session_id in self._sessions and key in self._sessions[session_id]:
                del self._sessions[session_id][key]
                return True
            return False
    
    def get_all(self, session_id: str) -> Dict[str, Any]:
        """Get all non-expired values in a session."""
        with self._lock:
            if session_id not in self._sessions:
                return {}
            
            result = {}
            expired_keys = []
            
            for key, slot in self._sessions[session_id].items():
                if slot.is_expired():
                    expired_keys.append(key)
                else:
                    result[key] = slot.value
            
            # Clean up expired
            for key in expired_keys:
                del self._sessions[session_id][key]
            
            return result
    
    def clear_session(self, session_id: str) -> None:
        """Clear all data for a session."""
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
            if session_id in self._session_metadata:
                del self._session_metadata[session_id]
    
    # ==================== SCRATCHPAD ====================
    
    def set_scratchpad(self, session_id: str, content: str) -> None:
        """Set the reasoning scratchpad for a session."""
        self.set(session_id, "_scratchpad", content)
    
    def append_scratchpad(self, session_id: str, content: str) -> None:
        """Append to the reasoning scratchpad."""
        current = self.get(session_id, "_scratchpad", "")
        self.set(session_id, "_scratchpad", current + "\n" + content)
    
    def get_scratchpad(self, session_id: str) -> str:
        """Get the reasoning scratchpad."""
        return self.get(session_id, "_scratchpad", "")
    
    def clear_scratchpad(self, session_id: str) -> None:
        """Clear the reasoning scratchpad."""
        self.delete(session_id, "_scratchpad")
    
    # ==================== CONVERSATION CONTEXT ====================
    
    def set_context(self, session_id: str, context: Dict[str, Any]) -> None:
        """Set conversation context."""
        self.set(session_id, "_context", context)
    
    def update_context(self, session_id: str, updates: Dict[str, Any]) -> None:
        """Update conversation context."""
        current = self.get(session_id, "_context", {})
        current.update(updates)
        self.set(session_id, "_context", current)
    
    def get_context(self, session_id: str) -> Dict[str, Any]:
        """Get conversation context."""
        return self.get(session_id, "_context", {})
    
    # ==================== TASK STATE ====================
    
    def set_current_task(self, session_id: str, task: Dict[str, Any]) -> None:
        """Set the current task being processed."""
        self.set(session_id, "_current_task", {
            **task,
            "started_at": datetime.now().isoformat()
        })
    
    def get_current_task(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get the current task."""
        return self.get(session_id, "_current_task")
    
    def complete_task(self, session_id: str, result: Any = None) -> None:
        """Mark current task as complete."""
        task = self.get(session_id, "_current_task")
        if task:
            task["completed_at"] = datetime.now().isoformat()
            task["result"] = result
            
            # Move to completed tasks list
            completed = self.get(session_id, "_completed_tasks", [])
            completed.append(task)
            self.set(session_id, "_completed_tasks", completed[-10:])  # Keep last 10
            
            self.delete(session_id, "_current_task")
    
    # ==================== ENTITY TRACKING ====================
    
    def track_entity(self, session_id: str, entity_type: str, entity_id: str, data: Dict[str, Any]) -> None:
        """Track an entity mentioned in conversation."""
        entities = self.get(session_id, "_entities", {})
        if entity_type not in entities:
            entities[entity_type] = {}
        entities[entity_type][entity_id] = {
            **data,
            "last_mentioned": datetime.now().isoformat()
        }
        self.set(session_id, "_entities", entities)
    
    def get_entities(self, session_id: str, entity_type: Optional[str] = None) -> Dict[str, Any]:
        """Get tracked entities."""
        entities = self.get(session_id, "_entities", {})
        if entity_type:
            return entities.get(entity_type, {})
        return entities
    
    # ==================== STATISTICS ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get working memory statistics."""
        with self._lock:
            total_slots = sum(len(s) for s in self._sessions.values())
            return {
                "active_sessions": len(self._sessions),
                "total_slots": total_slots,
                "sessions": {
                    sid: {
                        "slots": len(slots),
                        **self._session_metadata.get(sid, {})
                    }
                    for sid, slots in self._sessions.items()
                }
            }
    
    def cleanup_expired(self) -> int:
        """Remove all expired slots across all sessions."""
        removed = 0
        with self._lock:
            for session_id in list(self._sessions.keys()):
                expired_keys = [
                    k for k, v in self._sessions[session_id].items() 
                    if v.is_expired()
                ]
                for key in expired_keys:
                    del self._sessions[session_id][key]
                    removed += 1
        return removed


# Global working memory instance
_working_memory: Optional[WorkingMemory] = None


def get_working_memory() -> WorkingMemory:
    """Get the global working memory instance."""
    global _working_memory
    if _working_memory is None:
        _working_memory = WorkingMemory()
    return _working_memory

