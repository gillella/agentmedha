"""
Episodic Memory - Time-stamped experiences and interactions.

Episodic memory stores:
- Past interactions and decisions
- "What happened when..." queries  
- User's interaction history
- Agent's action history
- Conversation summaries

Features:
- Time-based retrieval
- Importance scoring
- Memory decay (less important memories fade)
- Consolidation to semantic memory
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from qdrant_client.http import models

from .base import (
    BaseMemory, MemoryRecord, MemoryType, MemoryScope, 
    MemoryDomain
)


class EpisodicMemory(BaseMemory):
    """
    Long-term episodic memory for experiences and interactions.
    
    Features:
    - Vector-based semantic search
    - Time-based retrieval
    - Importance scoring and decay
    - Session grouping
    - Multi-tenant filtering
    """
    
    DECAY_RATE = 0.1  # Importance decays by 10% per access period
    MIN_IMPORTANCE = 0.1  # Minimum importance before deletion
    
    def __init__(self, collection_name: str = "agentmedha_episodic"):
        super().__init__(collection_name)
    
    def add(self, record: MemoryRecord) -> str:
        """
        Add an episodic memory.
        
        Args:
            record: The memory record to store
            
        Returns:
            The memory ID
        """
        # Ensure correct memory type
        record.memory_type = MemoryType.EPISODIC
        
        # Generate embedding
        vector = self._embed(record.content)
        
        # Upsert to Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=record.id,
                    vector=vector,
                    payload=record.to_dict()
                )
            ]
        )
        
        return record.id
    
    def add_interaction(
        self,
        content: str,
        agent_id: str = "supervisor",
        domain: MemoryDomain = MemoryDomain.GENERAL,
        scope: MemoryScope = MemoryScope.GLOBAL,
        session_id: Optional[str] = None,
        importance: float = 0.5,
        entities: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Convenience method to add an interaction to episodic memory.
        
        Args:
            content: The interaction content
            agent_id: The agent that created this memory
            domain: The domain (email, social, etc.)
            scope: Access scope (global, domain, private)
            session_id: Optional session identifier
            importance: Importance score (0.0 to 1.0)
            entities: Entities mentioned
            metadata: Additional metadata
            
        Returns:
            The memory ID
        """
        record = MemoryRecord(
            content=content,
            memory_type=MemoryType.EPISODIC,
            scope=scope,
            domain=domain,
            agent_id=agent_id,
            importance=importance,
            session_id=session_id,
            entities=entities or [],
            metadata=metadata or {}
        )
        return self.add(record)
    
    def search(
        self, 
        query: str, 
        limit: int = 5,
        agent_id: Optional[str] = None,
        domain: Optional[MemoryDomain] = None,
        scope: Optional[MemoryScope] = None,
        session_id: Optional[str] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        min_importance: float = 0.0,
        include_global: bool = True
    ) -> List[MemoryRecord]:
        """
        Search episodic memories with various filters.
        
        Args:
            query: The search query
            limit: Maximum number of results
            agent_id: Filter by agent
            domain: Filter by domain
            scope: Filter by scope
            session_id: Filter by session
            since: Only memories after this time
            until: Only memories before this time
            min_importance: Minimum importance score
            include_global: Include global memories in results
            
        Returns:
            List of matching memory records
        """
        vector = self._embed(query)
        
        # Build filters
        must_filters = [
            models.FieldCondition(
                key="memory_type",
                match=models.MatchValue(value=MemoryType.EPISODIC.value)
            )
        ]
        
        should_filters = []
        
        if domain:
            must_filters.append(
                models.FieldCondition(
                    key="domain",
                    match=models.MatchValue(value=domain.value)
                )
            )
        
        if scope:
            must_filters.append(
                models.FieldCondition(
                    key="scope",
                    match=models.MatchValue(value=scope.value)
                )
            )
        
        if session_id:
            must_filters.append(
                models.FieldCondition(
                    key="session_id",
                    match=models.MatchValue(value=session_id)
                )
            )
        
        if since:
            must_filters.append(
                models.FieldCondition(
                    key="created_at",
                    range=models.Range(gte=since.timestamp())
                )
            )
        
        if until:
            must_filters.append(
                models.FieldCondition(
                    key="created_at",
                    range=models.Range(lte=until.timestamp())
                )
            )
        
        if min_importance > 0:
            must_filters.append(
                models.FieldCondition(
                    key="importance",
                    range=models.Range(gte=min_importance)
                )
            )
        
        # Handle agent filtering with global inclusion
        if agent_id:
            if include_global:
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
        
        filter_obj = models.Filter(
            must=must_filters if must_filters else None,
            should=should_filters if should_filters else None
        )
        
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=vector,
            limit=limit,
            query_filter=filter_obj
        ).points
        
        # Update access tracking and apply decay
        records = []
        for res in results:
            record = MemoryRecord.from_dict(res.payload)
            record.access_count += 1
            record.accessed_at = datetime.now()
            
            # Update in database
            self._update_access(record.id, record.access_count, record.accessed_at)
            
            records.append(record)
        
        return records
    
    def search_by_time(
        self,
        since: datetime,
        until: Optional[datetime] = None,
        agent_id: Optional[str] = None,
        domain: Optional[MemoryDomain] = None,
        limit: int = 20
    ) -> List[MemoryRecord]:
        """
        Search memories by time range.
        
        Args:
            since: Start of time range
            until: End of time range (defaults to now)
            agent_id: Filter by agent
            domain: Filter by domain
            limit: Maximum results
            
        Returns:
            List of memory records in time range
        """
        if until is None:
            until = datetime.now()
        
        must_filters = [
            models.FieldCondition(
                key="memory_type",
                match=models.MatchValue(value=MemoryType.EPISODIC.value)
            ),
            models.FieldCondition(
                key="created_at",
                range=models.Range(gte=since.timestamp(), lte=until.timestamp())
            )
        ]
        
        if agent_id:
            must_filters.append(
                models.FieldCondition(
                    key="agent_id",
                    match=models.MatchValue(value=agent_id)
                )
            )
        
        if domain:
            must_filters.append(
                models.FieldCondition(
                    key="domain",
                    match=models.MatchValue(value=domain.value)
                )
            )
        
        filter_obj = models.Filter(must=must_filters)
        
        # Scroll through results (no vector search, just filter)
        results = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=filter_obj,
            limit=limit
            # Note: order_by requires a payload index - skipping for now
        )[0]
        
        return [MemoryRecord.from_dict(r.payload) for r in results]
    
    def get(self, memory_id: str) -> Optional[MemoryRecord]:
        """Get a specific episodic memory by ID."""
        try:
            results = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[memory_id]
            )
            if results:
                return MemoryRecord.from_dict(results[0].payload)
            return None
        except Exception:
            return None
    
    def update(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update an episodic memory."""
        try:
            self.client.set_payload(
                collection_name=self.collection_name,
                payload=updates,
                points=[memory_id]
            )
            return True
        except Exception:
            return False
    
    def _update_access(self, memory_id: str, access_count: int, accessed_at: datetime) -> None:
        """Update access tracking for a memory."""
        self.update(memory_id, {
            "access_count": access_count,
            "accessed_at": accessed_at.isoformat()
        })
    
    def delete(self, memory_id: str) -> bool:
        """Delete an episodic memory."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(points=[memory_id])
            )
            return True
        except Exception:
            return False
    
    def apply_decay(self, days_since_last_access: int = 30) -> int:
        """
        Apply importance decay to memories not accessed recently.
        
        Args:
            days_since_last_access: Decay memories not accessed in this many days
            
        Returns:
            Number of memories affected
        """
        cutoff = datetime.now() - timedelta(days=days_since_last_access)
        
        # Find memories not accessed recently
        filter_obj = models.Filter(
            must=[
                models.FieldCondition(
                    key="memory_type",
                    match=models.MatchValue(value=MemoryType.EPISODIC.value)
                ),
                models.FieldCondition(
                    key="accessed_at",
                    range=models.Range(lte=cutoff.timestamp())
                )
            ]
        )
        
        results = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=filter_obj,
            limit=1000
        )[0]
        
        affected = 0
        to_delete = []
        
        for res in results:
            current_importance = res.payload.get("importance", 0.5)
            new_importance = current_importance * (1 - self.DECAY_RATE)
            
            if new_importance < self.MIN_IMPORTANCE:
                to_delete.append(res.id)
            else:
                self.update(res.id, {"importance": new_importance})
                affected += 1
        
        # Delete memories that have decayed below threshold
        if to_delete:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(points=to_delete)
            )
            affected += len(to_delete)
        
        return affected
    
    def get_recent(
        self,
        agent_id: Optional[str] = None,
        domain: Optional[MemoryDomain] = None,
        hours: int = 24,
        limit: int = 10
    ) -> List[MemoryRecord]:
        """
        Get recent memories.
        
        Args:
            agent_id: Filter by agent
            domain: Filter by domain
            hours: How many hours back to look
            limit: Maximum results
            
        Returns:
            List of recent memory records
        """
        since = datetime.now() - timedelta(hours=hours)
        return self.search_by_time(
            since=since,
            agent_id=agent_id,
            domain=domain,
            limit=limit
        )
    
    def summarize_session(self, session_id: str) -> Optional[str]:
        """
        Get all memories from a session for summarization.
        
        Args:
            session_id: The session to summarize
            
        Returns:
            Combined content from all session memories
        """
        filter_obj = models.Filter(
            must=[
                models.FieldCondition(
                    key="memory_type",
                    match=models.MatchValue(value=MemoryType.EPISODIC.value)
                ),
                models.FieldCondition(
                    key="session_id",
                    match=models.MatchValue(value=session_id)
                )
            ]
        )
        
        results = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=filter_obj,
            limit=100
        )[0]
        
        if not results:
            return None
        
        # Sort by timestamp and combine
        records = sorted(
            [MemoryRecord.from_dict(r.payload) for r in results],
            key=lambda r: r.created_at
        )
        
        return "\n---\n".join([r.content for r in records])


# Global episodic memory instance
_episodic_memory: Optional[EpisodicMemory] = None


def get_episodic_memory() -> EpisodicMemory:
    """Get the global episodic memory instance."""
    global _episodic_memory
    if _episodic_memory is None:
        _episodic_memory = EpisodicMemory()
    return _episodic_memory

