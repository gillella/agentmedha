"""
Base types and utilities for the memory system.
"""

import os
import uuid
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_google_genai import GoogleGenerativeAIEmbeddings


class MemoryType(str, Enum):
    """Types of memory in the system."""
    WORKING = "working"      # Short-term, session-scoped
    EPISODIC = "episodic"    # Experiences, interactions
    SEMANTIC = "semantic"    # Facts, knowledge, entities
    PROCEDURAL = "procedural"  # Patterns, rules, workflows


class MemoryScope(str, Enum):
    """Access scope for memories - who can access them."""
    GLOBAL = "global"        # All agents can read/write
    DOMAIN = "domain"        # Agents in same domain (email, social, finance)
    PRIVATE = "private"      # Only the specific agent


class MemoryDomain(str, Enum):
    """Domains for scoped memory access."""
    EMAIL = "email"
    SOCIAL = "social"
    FINANCE = "finance"
    HOME = "home"
    PET = "pet"
    GENERAL = "general"


@dataclass
class MemoryRecord:
    """A single memory record with full metadata."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    memory_type: MemoryType = MemoryType.EPISODIC
    scope: MemoryScope = MemoryScope.GLOBAL
    domain: MemoryDomain = MemoryDomain.GENERAL
    agent_id: str = "supervisor"
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    
    # Importance and decay
    importance: float = 0.5  # 0.0 to 1.0
    access_count: int = 0
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Related entities
    entities: List[str] = field(default_factory=list)
    
    # For episodic memories
    session_id: Optional[str] = None
    
    # For procedural memories
    trigger_pattern: Optional[str] = None
    action_sequence: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "scope": self.scope.value,
            "domain": self.domain.value,
            "agent_id": self.agent_id,
            "created_at": self.created_at.isoformat(),
            "accessed_at": self.accessed_at.isoformat(),
            "importance": self.importance,
            "access_count": self.access_count,
            "entities": self.entities,
            "session_id": self.session_id,
            "trigger_pattern": self.trigger_pattern,
            "action_sequence": self.action_sequence,
            **self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryRecord":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            content=data.get("content", data.get("text", "")),
            memory_type=MemoryType(data.get("memory_type", "episodic")),
            scope=MemoryScope(data.get("scope", "global")),
            domain=MemoryDomain(data.get("domain", "general")),
            agent_id=data.get("agent_id", "supervisor"),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            accessed_at=datetime.fromisoformat(data["accessed_at"]) if "accessed_at" in data else datetime.now(),
            importance=data.get("importance", 0.5),
            access_count=data.get("access_count", 0),
            metadata={k: v for k, v in data.items() if k not in [
                "id", "content", "text", "memory_type", "scope", "domain", 
                "agent_id", "created_at", "accessed_at", "importance", 
                "access_count", "entities", "session_id", "trigger_pattern", "action_sequence"
            ]},
            entities=data.get("entities", []),
            session_id=data.get("session_id"),
            trigger_pattern=data.get("trigger_pattern"),
            action_sequence=data.get("action_sequence"),
        )


class BaseMemory(ABC):
    """Abstract base class for all memory types."""
    
    def __init__(self, collection_name: str = "agent_medha_memory"):
        self.collection_name = collection_name
        
        # Initialize Qdrant Client
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        qdrant_api_key = os.getenv("QDRANT_API_KEY", None)
        self.client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        
        # Initialize Embeddings
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
        
        # Ensure collection exists
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Creates the collection if it doesn't exist."""
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            print(f"Creating collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=768,  # Dimension for text-embedding-004
                    distance=models.Distance.COSINE
                )
            )
    
    def _embed(self, text: str) -> List[float]:
        """Generate embedding for text."""
        return self.embeddings.embed_query(text)
    
    def _build_filter(
        self, 
        memory_type: Optional[MemoryType] = None,
        scope: Optional[MemoryScope] = None,
        domain: Optional[MemoryDomain] = None,
        agent_id: Optional[str] = None,
        include_global: bool = True
    ) -> Optional[models.Filter]:
        """Build Qdrant filter based on criteria."""
        must_filters = []
        should_filters = []
        
        if memory_type:
            must_filters.append(
                models.FieldCondition(
                    key="memory_type", 
                    match=models.MatchValue(value=memory_type.value)
                )
            )
        
        if scope:
            must_filters.append(
                models.FieldCondition(
                    key="scope", 
                    match=models.MatchValue(value=scope.value)
                )
            )
        
        if domain:
            must_filters.append(
                models.FieldCondition(
                    key="domain", 
                    match=models.MatchValue(value=domain.value)
                )
            )
        
        if agent_id:
            if include_global:
                # Search for agent's private + global memories
                should_filters.append(
                    models.FieldCondition(
                        key="agent_id", 
                        match=models.MatchValue(value=agent_id)
                    )
                )
                should_filters.append(
                    models.FieldCondition(
                        key="scope", 
                        match=models.MatchValue(value=MemoryScope.GLOBAL.value)
                    )
                )
            else:
                must_filters.append(
                    models.FieldCondition(
                        key="agent_id", 
                        match=models.MatchValue(value=agent_id)
                    )
                )
        
        if not must_filters and not should_filters:
            return None
            
        return models.Filter(
            must=must_filters if must_filters else None,
            should=should_filters if should_filters else None
        )
    
    @abstractmethod
    def add(self, record: MemoryRecord) -> str:
        """Add a memory record."""
        pass
    
    @abstractmethod
    def search(self, query: str, limit: int = 5, **filters) -> List[MemoryRecord]:
        """Search for relevant memories."""
        pass
    
    @abstractmethod
    def get(self, memory_id: str) -> Optional[MemoryRecord]:
        """Get a specific memory by ID."""
        pass
    
    @abstractmethod
    def update(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update a memory record."""
        pass
    
    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """Delete a memory record."""
        pass

