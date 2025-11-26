"""
Procedural Memory - Learned patterns, rules, and workflows.

Procedural memory stores:
- Learned action sequences ("When X happens, do Y")
- Email response patterns
- Automation workflows
- "How to" knowledge
- Conditional rules and triggers

Features:
- Pattern matching
- Rule execution
- Workflow templates
- Learning from user feedback
"""

import os
import json
import uuid
import hashlib
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from dataclasses import dataclass, field
from qdrant_client.http import models

from .base import (
    BaseMemory, MemoryRecord, MemoryType, MemoryScope, 
    MemoryDomain
)


@dataclass
class Procedure:
    """A learned procedure/rule that can be executed."""
    
    id: str
    name: str
    description: str
    
    # Trigger conditions
    trigger_pattern: str  # Natural language pattern that triggers this
    trigger_keywords: List[str] = field(default_factory=list)
    trigger_conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Action definition
    action_type: str = "sequence"  # "sequence", "template", "workflow"
    action_steps: List[Dict[str, Any]] = field(default_factory=list)
    action_template: Optional[str] = None
    
    # Metadata
    domain: str = "general"
    agent_id: str = "supervisor"
    scope: str = "global"
    
    # Learning & feedback
    success_count: int = 0
    failure_count: int = 0
    last_used: Optional[datetime] = None
    confidence: float = 0.5
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "trigger_pattern": self.trigger_pattern,
            "trigger_keywords": self.trigger_keywords,
            "trigger_conditions": self.trigger_conditions,
            "action_type": self.action_type,
            "action_steps": self.action_steps,
            "action_template": self.action_template,
            "domain": self.domain,
            "agent_id": self.agent_id,
            "scope": self.scope,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "memory_type": MemoryType.PROCEDURAL.value,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Procedure":
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            trigger_pattern=data["trigger_pattern"],
            trigger_keywords=data.get("trigger_keywords", []),
            trigger_conditions=data.get("trigger_conditions", {}),
            action_type=data.get("action_type", "sequence"),
            action_steps=data.get("action_steps", []),
            action_template=data.get("action_template"),
            domain=data.get("domain", "general"),
            agent_id=data.get("agent_id", "supervisor"),
            scope=data.get("scope", "global"),
            success_count=data.get("success_count", 0),
            failure_count=data.get("failure_count", 0),
            last_used=datetime.fromisoformat(data["last_used"]) if data.get("last_used") else None,
            confidence=data.get("confidence", 0.5),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now(),
        )
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.5
        return self.success_count / total


class ProceduralMemory(BaseMemory):
    """
    Long-term procedural memory for learned patterns and workflows.
    
    Features:
    - Pattern-based rule storage
    - Trigger matching
    - Action execution
    - Learning from feedback
    - Workflow templates
    """
    
    def __init__(self, collection_name: str = "agentmedha_procedural"):
        super().__init__(collection_name)
    
    def add(self, record: MemoryRecord) -> str:
        """Add a procedural memory record."""
        record.memory_type = MemoryType.PROCEDURAL
        
        vector = self._embed(record.content)
        
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
    
    def add_procedure(self, procedure: Procedure) -> str:
        """
        Add a procedure to memory.
        
        Args:
            procedure: The procedure to store
            
        Returns:
            The procedure ID
        """
        # Create searchable text
        search_text = f"{procedure.name}: {procedure.description}. " + \
                      f"Trigger: {procedure.trigger_pattern}. " + \
                      f"Keywords: {', '.join(procedure.trigger_keywords)}"
        
        vector = self._embed(search_text)
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=procedure.id,
                    vector=vector,
                    payload=procedure.to_dict()
                )
            ]
        )
        
        return procedure.id
    
    def create_email_pattern(
        self,
        pattern_name: str,
        description: str,
        trigger_pattern: str,
        trigger_keywords: List[str],
        response_template: str,
        conditions: Dict[str, Any] = None,
        agent_id: str = "maya",
    ) -> str:
        """
        Create an email response pattern.
        
        Args:
            pattern_name: Name of the pattern
            description: Description
            trigger_pattern: Natural language trigger
            trigger_keywords: Keywords that activate this pattern
            response_template: Template for response
            conditions: Additional conditions
            agent_id: Agent that owns this pattern
            
        Returns:
            Pattern ID
        """
        procedure = Procedure(
            id=str(uuid.UUID(hashlib.md5(f"email_pattern_{pattern_name}".encode()).hexdigest())),
            name=pattern_name,
            description=description,
            trigger_pattern=trigger_pattern,
            trigger_keywords=trigger_keywords,
            trigger_conditions=conditions or {},
            action_type="template",
            action_template=response_template,
            domain=MemoryDomain.EMAIL.value,
            agent_id=agent_id,
            scope=MemoryScope.PRIVATE.value,
        )
        
        return self.add_procedure(procedure)
    
    def create_workflow(
        self,
        workflow_name: str,
        description: str,
        trigger_pattern: str,
        steps: List[Dict[str, Any]],
        domain: MemoryDomain = MemoryDomain.GENERAL,
        agent_id: str = "supervisor",
    ) -> str:
        """
        Create a workflow procedure.
        
        Args:
            workflow_name: Name of the workflow
            description: Description
            trigger_pattern: When to trigger
            steps: List of action steps
            domain: Domain this applies to
            agent_id: Owning agent
            
        Returns:
            Workflow ID
        """
        procedure = Procedure(
            id=str(uuid.UUID(hashlib.md5(f"workflow_{workflow_name}".encode()).hexdigest())),
            name=workflow_name,
            description=description,
            trigger_pattern=trigger_pattern,
            action_type="workflow",
            action_steps=steps,
            domain=domain.value,
            agent_id=agent_id,
            scope=MemoryScope.DOMAIN.value,
        )
        
        return self.add_procedure(procedure)
    
    def search(
        self,
        query: str,
        limit: int = 5,
        agent_id: Optional[str] = None,
        domain: Optional[MemoryDomain] = None,
        min_confidence: float = 0.0,
        include_global: bool = True
    ) -> List[Procedure]:
        """
        Search for matching procedures.
        
        Args:
            query: Search query (matches against triggers and descriptions)
            limit: Maximum results
            agent_id: Filter by agent
            domain: Filter by domain
            min_confidence: Minimum confidence score
            include_global: Include global procedures
            
        Returns:
            List of matching procedures
        """
        vector = self._embed(query)
        
        must_filters = [
            models.FieldCondition(
                key="memory_type",
                match=models.MatchValue(value=MemoryType.PROCEDURAL.value)
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
        
        if min_confidence > 0:
            must_filters.append(
                models.FieldCondition(
                    key="confidence",
                    range=models.Range(gte=min_confidence)
                )
            )
        
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
        
        return [Procedure.from_dict(r.payload) for r in results]
    
    def find_matching_procedures(
        self,
        context: str,
        domain: Optional[MemoryDomain] = None,
        agent_id: Optional[str] = None,
    ) -> List[Procedure]:
        """
        Find procedures that match the given context.
        
        Uses both semantic search and keyword matching.
        
        Args:
            context: The current context/situation
            domain: Filter by domain
            agent_id: Filter by agent
            
        Returns:
            List of matching procedures, sorted by relevance
        """
        # Semantic search
        semantic_matches = self.search(
            query=context,
            limit=10,
            domain=domain,
            agent_id=agent_id,
            min_confidence=0.3
        )
        
        # Keyword matching boost
        context_lower = context.lower()
        scored_matches = []
        
        for proc in semantic_matches:
            score = proc.confidence
            
            # Boost for keyword matches
            keyword_matches = sum(
                1 for kw in proc.trigger_keywords 
                if kw.lower() in context_lower
            )
            score += keyword_matches * 0.1
            
            # Boost for recent success
            score += min(proc.success_rate * 0.2, 0.2)
            
            scored_matches.append((score, proc))
        
        # Sort by score
        scored_matches.sort(key=lambda x: x[0], reverse=True)
        
        return [proc for _, proc in scored_matches]
    
    def get(self, procedure_id: str) -> Optional[Procedure]:
        """Get a specific procedure."""
        try:
            results = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[procedure_id]
            )
            if results:
                return Procedure.from_dict(results[0].payload)
            return None
        except Exception:
            return None
    
    def update(self, procedure_id: str, updates: Dict[str, Any]) -> bool:
        """Update a procedure."""
        try:
            updates["updated_at"] = datetime.now().isoformat()
            self.client.set_payload(
                collection_name=self.collection_name,
                payload=updates,
                points=[procedure_id]
            )
            return True
        except Exception:
            return False
    
    def delete(self, procedure_id: str) -> bool:
        """Delete a procedure."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(points=[procedure_id])
            )
            return True
        except Exception:
            return False
    
    def record_success(self, procedure_id: str) -> bool:
        """Record a successful use of a procedure."""
        proc = self.get(procedure_id)
        if not proc:
            return False
        
        proc.success_count += 1
        proc.last_used = datetime.now()
        proc.confidence = min(proc.confidence + 0.05, 1.0)
        
        return self.update(procedure_id, {
            "success_count": proc.success_count,
            "last_used": proc.last_used.isoformat(),
            "confidence": proc.confidence
        })
    
    def record_failure(self, procedure_id: str) -> bool:
        """Record a failed use of a procedure."""
        proc = self.get(procedure_id)
        if not proc:
            return False
        
        proc.failure_count += 1
        proc.last_used = datetime.now()
        proc.confidence = max(proc.confidence - 0.1, 0.1)
        
        return self.update(procedure_id, {
            "failure_count": proc.failure_count,
            "last_used": proc.last_used.isoformat(),
            "confidence": proc.confidence
        })
    
    def get_email_patterns(
        self,
        agent_id: str = "maya",
        min_confidence: float = 0.3
    ) -> List[Procedure]:
        """Get all email response patterns."""
        filter_obj = models.Filter(
            must=[
                models.FieldCondition(
                    key="memory_type",
                    match=models.MatchValue(value=MemoryType.PROCEDURAL.value)
                ),
                models.FieldCondition(
                    key="domain",
                    match=models.MatchValue(value=MemoryDomain.EMAIL.value)
                ),
                models.FieldCondition(
                    key="action_type",
                    match=models.MatchValue(value="template")
                ),
                models.FieldCondition(
                    key="confidence",
                    range=models.Range(gte=min_confidence)
                )
            ]
        )
        
        results = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=filter_obj,
            limit=100
        )[0]
        
        return [Procedure.from_dict(r.payload) for r in results]
    
    def get_workflows(
        self,
        domain: Optional[MemoryDomain] = None,
        agent_id: Optional[str] = None
    ) -> List[Procedure]:
        """Get all workflows."""
        must_filters = [
            models.FieldCondition(
                key="memory_type",
                match=models.MatchValue(value=MemoryType.PROCEDURAL.value)
            ),
            models.FieldCondition(
                key="action_type",
                match=models.MatchValue(value="workflow")
            )
        ]
        
        if domain:
            must_filters.append(
                models.FieldCondition(
                    key="domain",
                    match=models.MatchValue(value=domain.value)
                )
            )
        
        if agent_id:
            must_filters.append(
                models.FieldCondition(
                    key="agent_id",
                    match=models.MatchValue(value=agent_id)
                )
            )
        
        filter_obj = models.Filter(must=must_filters)
        
        results = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=filter_obj,
            limit=100
        )[0]
        
        return [Procedure.from_dict(r.payload) for r in results]


# Global procedural memory instance
_procedural_memory: Optional[ProceduralMemory] = None


def get_procedural_memory() -> ProceduralMemory:
    """Get the global procedural memory instance."""
    global _procedural_memory
    if _procedural_memory is None:
        _procedural_memory = ProceduralMemory()
    return _procedural_memory

