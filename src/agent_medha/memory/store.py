"""
SharedMemoryStore - Unified memory access with multi-tenant control.

The SharedMemoryStore provides a single interface to all memory types
with intelligent access control for multi-agent environments.

Access Levels:
- GLOBAL: All agents can read/write
- DOMAIN: Agents in same domain (email, social, finance)
- PRIVATE: Only the specific agent

Features:
- Unified API across all memory types
- Automatic access control enforcement
- Memory consolidation (working → episodic → semantic)
- Cross-domain knowledge sharing
- Agent registration and management
"""

import os
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import threading

from .base import MemoryRecord, MemoryType, MemoryScope, MemoryDomain
from .working import WorkingMemory, get_working_memory
from .episodic import EpisodicMemory, get_episodic_memory
from .semantic import SemanticMemory, get_semantic_memory, EntityProfile
from .procedural import ProceduralMemory, get_procedural_memory, Procedure


@dataclass
class AgentRegistration:
    """Registration info for an agent in the memory system."""
    agent_id: str
    name: str
    domain: MemoryDomain
    capabilities: List[str] = field(default_factory=list)
    registered_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)


class SharedMemoryStore:
    """
    Unified memory store with multi-tenant access control.
    
    Provides a single interface for all agents to access:
    - Working memory (session-scoped)
    - Episodic memory (experiences)
    - Semantic memory (facts, entities)
    - Procedural memory (patterns, rules)
    
    With automatic access control based on:
    - Agent identity
    - Memory scope (global, domain, private)
    - Domain membership
    """
    
    def __init__(self):
        # Memory systems
        self.working = get_working_memory()
        self.episodic = get_episodic_memory()
        self.semantic = get_semantic_memory()
        self.procedural = get_procedural_memory()
        
        # Agent registry
        self._agents: Dict[str, AgentRegistration] = {}
        self._lock = threading.Lock()
        
        # Default agents
        self._register_default_agents()
    
    def _register_default_agents(self):
        """Register the default system agents."""
        default_agents = [
            AgentRegistration(
                agent_id="supervisor",
                name="agentMedha Supervisor",
                domain=MemoryDomain.GENERAL,
                capabilities=["orchestration", "routing", "planning"]
            ),
            AgentRegistration(
                agent_id="maya",
                name="Maya - Email Agent",
                domain=MemoryDomain.EMAIL,
                capabilities=["email_read", "email_write", "email_analyze", "email_triage"]
            ),
            AgentRegistration(
                agent_id="social",
                name="Social Media Agent",
                domain=MemoryDomain.SOCIAL,
                capabilities=["post_draft", "post_publish", "engagement_analyze"]
            ),
            AgentRegistration(
                agent_id="finance",
                name="Finance Agent",
                domain=MemoryDomain.FINANCE,
                capabilities=["transaction_analyze", "budget_track", "spending_insight"]
            ),
            AgentRegistration(
                agent_id="home",
                name="Home Security Agent",
                domain=MemoryDomain.HOME,
                capabilities=["device_control", "status_monitor", "alert_manage"]
            ),
            AgentRegistration(
                agent_id="pet",
                name="Pet Care Agent",
                domain=MemoryDomain.PET,
                capabilities=["pet_monitor", "health_track", "care_schedule"]
            ),
        ]
        
        for agent in default_agents:
            self._agents[agent.agent_id] = agent
    
    # ==================== AGENT MANAGEMENT ====================
    
    def register_agent(self, registration: AgentRegistration) -> str:
        """Register a new agent in the memory system."""
        with self._lock:
            self._agents[registration.agent_id] = registration
        return registration.agent_id
    
    def get_agent(self, agent_id: str) -> Optional[AgentRegistration]:
        """Get agent registration info."""
        return self._agents.get(agent_id)
    
    def list_agents(self, domain: Optional[MemoryDomain] = None) -> List[AgentRegistration]:
        """List registered agents, optionally filtered by domain."""
        if domain:
            return [a for a in self._agents.values() if a.domain == domain]
        return list(self._agents.values())
    
    def update_agent_activity(self, agent_id: str) -> None:
        """Update last active timestamp for an agent."""
        if agent_id in self._agents:
            self._agents[agent_id].last_active = datetime.now()
    
    def _get_agent_domain(self, agent_id: str) -> MemoryDomain:
        """Get the domain for an agent."""
        agent = self._agents.get(agent_id)
        return agent.domain if agent else MemoryDomain.GENERAL
    
    def _can_access(
        self, 
        agent_id: str, 
        record_scope: MemoryScope,
        record_domain: MemoryDomain,
        record_agent: str
    ) -> bool:
        """
        Check if an agent can access a memory record.
        
        Rules:
        - GLOBAL scope: All agents can access
        - DOMAIN scope: Only agents in same domain
        - PRIVATE scope: Only the owning agent
        """
        if record_scope == MemoryScope.GLOBAL:
            return True
        
        if record_scope == MemoryScope.DOMAIN:
            agent_domain = self._get_agent_domain(agent_id)
            return agent_domain == record_domain or agent_domain == MemoryDomain.GENERAL
        
        if record_scope == MemoryScope.PRIVATE:
            return agent_id == record_agent
        
        return False
    
    # ==================== WORKING MEMORY ====================
    
    def session_set(
        self, 
        session_id: str, 
        key: str, 
        value: Any,
        agent_id: str = "supervisor",
        ttl_minutes: Optional[int] = None
    ) -> None:
        """Set a value in working memory for a session."""
        self.update_agent_activity(agent_id)
        self.working.set(session_id, key, value, ttl_minutes)
    
    def session_get(
        self, 
        session_id: str, 
        key: str,
        agent_id: str = "supervisor",
        default: Any = None
    ) -> Any:
        """Get a value from working memory."""
        self.update_agent_activity(agent_id)
        return self.working.get(session_id, key, default)
    
    def session_context(
        self, 
        session_id: str,
        agent_id: str = "supervisor"
    ) -> Dict[str, Any]:
        """Get the full context for a session."""
        return self.working.get_context(session_id)
    
    def session_scratchpad(
        self, 
        session_id: str,
        content: Optional[str] = None,
        append: bool = False
    ) -> str:
        """Get or set the reasoning scratchpad."""
        if content is not None:
            if append:
                self.working.append_scratchpad(session_id, content)
            else:
                self.working.set_scratchpad(session_id, content)
        return self.working.get_scratchpad(session_id)
    
    def session_task(
        self, 
        session_id: str,
        task: Optional[Dict[str, Any]] = None,
        complete: bool = False,
        result: Any = None
    ) -> Optional[Dict[str, Any]]:
        """Get, set, or complete the current task."""
        if task is not None:
            self.working.set_current_task(session_id, task)
        elif complete:
            self.working.complete_task(session_id, result)
        return self.working.get_current_task(session_id)
    
    def end_session(self, session_id: str) -> None:
        """End a session and clear its working memory."""
        self.working.clear_session(session_id)
    
    # ==================== EPISODIC MEMORY ====================
    
    def remember_interaction(
        self,
        content: str,
        agent_id: str = "supervisor",
        session_id: Optional[str] = None,
        domain: Optional[MemoryDomain] = None,
        scope: MemoryScope = MemoryScope.GLOBAL,
        importance: float = 0.5,
        entities: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Store an interaction in episodic memory.
        
        Args:
            content: The interaction content
            agent_id: The agent recording this
            session_id: Optional session identifier
            domain: Domain (auto-detected from agent if not specified)
            scope: Access scope
            importance: Importance score
            entities: Related entities
            metadata: Additional metadata
            
        Returns:
            Memory ID
        """
        self.update_agent_activity(agent_id)
        
        if domain is None:
            domain = self._get_agent_domain(agent_id)
        
        return self.episodic.add_interaction(
            content=content,
            agent_id=agent_id,
            domain=domain,
            scope=scope,
            session_id=session_id,
            importance=importance,
            entities=entities,
            metadata=metadata
        )
    
    def recall_episodes(
        self,
        query: str,
        agent_id: str = "supervisor",
        limit: int = 5,
        domain: Optional[MemoryDomain] = None,
        since: Optional[datetime] = None,
        min_importance: float = 0.0
    ) -> List[MemoryRecord]:
        """
        Recall relevant episodic memories.
        
        Automatically filters based on agent access rights.
        """
        self.update_agent_activity(agent_id)
        
        return self.episodic.search(
            query=query,
            limit=limit,
            agent_id=agent_id,
            domain=domain,
            since=since,
            min_importance=min_importance,
            include_global=True
        )
    
    def recall_recent(
        self,
        agent_id: str = "supervisor",
        hours: int = 24,
        limit: int = 10,
        domain: Optional[MemoryDomain] = None
    ) -> List[MemoryRecord]:
        """Recall recent memories."""
        return self.episodic.get_recent(
            agent_id=agent_id,
            domain=domain,
            hours=hours,
            limit=limit
        )
    
    # ==================== SEMANTIC MEMORY ====================
    
    def learn_fact(
        self,
        fact: str,
        agent_id: str = "supervisor",
        category: str = "general",
        confidence: float = 1.0,
        domain: Optional[MemoryDomain] = None,
        scope: MemoryScope = MemoryScope.GLOBAL,
        source: Optional[str] = None,
        entities: List[str] = None
    ) -> str:
        """
        Store a learned fact in semantic memory.
        
        Args:
            fact: The fact content
            agent_id: Agent that learned this
            category: Category of fact
            confidence: How confident we are
            domain: Which domain this applies to
            scope: Who can access this
            source: Where we learned this
            entities: Related entities
            
        Returns:
            Fact ID
        """
        self.update_agent_activity(agent_id)
        
        if domain is None:
            domain = self._get_agent_domain(agent_id)
        
        return self.semantic.add_fact(
            fact=fact,
            category=category,
            confidence=confidence,
            agent_id=agent_id,
            domain=domain,
            scope=scope,
            source=source,
            entities=entities
        )
    
    def learn_preference(
        self,
        preference: str,
        category: str = "general",
        confidence: float = 0.8,
        agent_id: str = "supervisor",
        domain: Optional[MemoryDomain] = None
    ) -> str:
        """Store a learned user preference."""
        if domain is None:
            domain = self._get_agent_domain(agent_id)
        
        return self.semantic.add_preference(
            preference=preference,
            category=category,
            confidence=confidence,
            agent_id=agent_id,
            domain=domain
        )
    
    def recall_facts(
        self,
        query: str,
        agent_id: str = "supervisor",
        limit: int = 5,
        domain: Optional[MemoryDomain] = None,
        category: Optional[str] = None,
        min_confidence: float = 0.0
    ) -> List[MemoryRecord]:
        """Recall relevant facts from semantic memory."""
        self.update_agent_activity(agent_id)
        
        return self.semantic.search(
            query=query,
            limit=limit,
            agent_id=agent_id,
            domain=domain,
            category=category,
            min_confidence=min_confidence,
            include_global=True
        )
    
    def get_preferences(
        self,
        domain: Optional[MemoryDomain] = None,
        category: Optional[str] = None
    ) -> List[MemoryRecord]:
        """Get all stored preferences."""
        return self.semantic.get_preferences(domain=domain, category=category)
    
    # ==================== ENTITY MANAGEMENT ====================
    
    def create_entity(
        self,
        entity_id: str,
        entity_type: str,
        name: str,
        attributes: Dict[str, Any] = None,
        agent_id: str = "supervisor"
    ) -> str:
        """Create or update an entity profile."""
        self.update_agent_activity(agent_id)
        
        profile = EntityProfile(
            entity_id=entity_id,
            entity_type=entity_type,
            name=name,
            attributes=attributes or {}
        )
        
        return self.semantic.add_entity(profile)
    
    def get_entity(self, entity_id: str) -> Optional[EntityProfile]:
        """Get an entity profile."""
        return self.semantic.get_entity(entity_id)
    
    def search_entities(
        self,
        query: str,
        entity_type: Optional[str] = None,
        limit: int = 5
    ) -> List[EntityProfile]:
        """Search for entities."""
        return self.semantic.search_entities(query, entity_type, limit)
    
    def add_contact(
        self,
        email: str,
        name: Optional[str] = None,
        attributes: Dict[str, Any] = None,
        agent_id: str = "maya"
    ) -> str:
        """Add a contact to the knowledge base."""
        self.update_agent_activity(agent_id)
        return self.semantic.add_contact(email, name, attributes)
    
    def get_contact(self, email: str) -> Optional[EntityProfile]:
        """Get a contact profile."""
        return self.semantic.get_contact(email)
    
    def relate_entities(
        self,
        from_entity: str,
        relationship: str,
        to_entity: str,
        agent_id: str = "supervisor"
    ) -> bool:
        """Create a relationship between entities."""
        self.update_agent_activity(agent_id)
        return self.semantic.add_relationship(from_entity, relationship, to_entity)
    
    # ==================== PROCEDURAL MEMORY ====================
    
    def add_procedure(
        self,
        procedure: Procedure,
        agent_id: str = "supervisor"
    ) -> str:
        """Add a procedure/pattern to memory."""
        self.update_agent_activity(agent_id)
        return self.procedural.add_procedure(procedure)
    
    def create_email_pattern(
        self,
        pattern_name: str,
        description: str,
        trigger_pattern: str,
        trigger_keywords: List[str],
        response_template: str,
        conditions: Dict[str, Any] = None,
        agent_id: str = "maya"
    ) -> str:
        """Create an email response pattern."""
        self.update_agent_activity(agent_id)
        return self.procedural.create_email_pattern(
            pattern_name=pattern_name,
            description=description,
            trigger_pattern=trigger_pattern,
            trigger_keywords=trigger_keywords,
            response_template=response_template,
            conditions=conditions,
            agent_id=agent_id
        )
    
    def create_workflow(
        self,
        workflow_name: str,
        description: str,
        trigger_pattern: str,
        steps: List[Dict[str, Any]],
        domain: MemoryDomain = MemoryDomain.GENERAL,
        agent_id: str = "supervisor"
    ) -> str:
        """Create a workflow procedure."""
        self.update_agent_activity(agent_id)
        return self.procedural.create_workflow(
            workflow_name=workflow_name,
            description=description,
            trigger_pattern=trigger_pattern,
            steps=steps,
            domain=domain,
            agent_id=agent_id
        )
    
    def find_procedures(
        self,
        context: str,
        agent_id: str = "supervisor",
        domain: Optional[MemoryDomain] = None
    ) -> List[Procedure]:
        """Find procedures matching the current context."""
        self.update_agent_activity(agent_id)
        
        if domain is None:
            domain = self._get_agent_domain(agent_id)
        
        return self.procedural.find_matching_procedures(
            context=context,
            domain=domain,
            agent_id=agent_id
        )
    
    def record_procedure_outcome(
        self,
        procedure_id: str,
        success: bool,
        agent_id: str = "supervisor"
    ) -> bool:
        """Record the outcome of using a procedure."""
        self.update_agent_activity(agent_id)
        
        if success:
            return self.procedural.record_success(procedure_id)
        else:
            return self.procedural.record_failure(procedure_id)
    
    def get_email_patterns(
        self,
        agent_id: str = "maya",
        min_confidence: float = 0.3
    ) -> List[Procedure]:
        """Get all email patterns."""
        return self.procedural.get_email_patterns(agent_id, min_confidence)
    
    # ==================== MEMORY CONSOLIDATION ====================
    
    def consolidate_session(
        self,
        session_id: str,
        agent_id: str = "supervisor"
    ) -> Dict[str, Any]:
        """
        Consolidate working memory from a session into long-term memory.
        
        This:
        1. Summarizes the session interaction
        2. Extracts facts learned
        3. Identifies entities mentioned
        4. Stores in episodic memory
        
        Returns:
            Summary of what was consolidated
        """
        self.update_agent_activity(agent_id)
        
        # Get all working memory for session
        session_data = self.working.get_all(session_id)
        context = self.working.get_context(session_id)
        scratchpad = self.working.get_scratchpad(session_id)
        completed_tasks = self.working.get(session_id, "_completed_tasks", [])
        entities = self.working.get_entities(session_id)
        
        result = {
            "session_id": session_id,
            "consolidated_at": datetime.now().isoformat(),
            "memories_created": [],
            "entities_tracked": [],
            "facts_learned": []
        }
        
        # Store session summary as episodic memory
        if context or scratchpad:
            summary = f"Session {session_id} context: {context}. Scratchpad: {scratchpad}"
            memory_id = self.remember_interaction(
                content=summary,
                agent_id=agent_id,
                session_id=session_id,
                importance=0.6,
                metadata={"type": "session_summary"}
            )
            result["memories_created"].append(memory_id)
        
        # Store completed tasks
        for task in completed_tasks:
            memory_id = self.remember_interaction(
                content=f"Completed task: {task.get('description', str(task))}",
                agent_id=agent_id,
                session_id=session_id,
                importance=0.7,
                metadata={"type": "task_completion", "task": task}
            )
            result["memories_created"].append(memory_id)
        
        # Store entities
        for entity_type, entity_data in entities.items():
            for entity_id, data in entity_data.items():
                self.semantic.increment_mention(f"{entity_type}_{entity_id}")
                result["entities_tracked"].append(f"{entity_type}:{entity_id}")
        
        return result
    
    def maintenance(self) -> Dict[str, Any]:
        """
        Run maintenance tasks:
        - Clean up expired working memory
        - Apply decay to episodic memories
        - Clean up low-confidence procedures
        
        Returns:
            Summary of maintenance performed
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "working_memory_cleaned": 0,
            "episodic_decayed": 0,
        }
        
        # Clean expired working memory
        result["working_memory_cleaned"] = self.working.cleanup_expired()
        
        # Apply episodic decay
        result["episodic_decayed"] = self.episodic.apply_decay()
        
        return result
    
    # ==================== UNIFIED SEARCH ====================
    
    def recall(
        self,
        query: str,
        agent_id: str = "supervisor",
        memory_types: List[MemoryType] = None,
        limit: int = 10,
        domain: Optional[MemoryDomain] = None
    ) -> Dict[str, List[Any]]:
        """
        Unified search across all memory types.
        
        Args:
            query: Search query
            agent_id: Requesting agent
            memory_types: Which memory types to search (default: all)
            limit: Maximum results per type
            domain: Domain filter
            
        Returns:
            Dictionary with results from each memory type
        """
        self.update_agent_activity(agent_id)
        
        if memory_types is None:
            memory_types = [MemoryType.EPISODIC, MemoryType.SEMANTIC, MemoryType.PROCEDURAL]
        
        if domain is None:
            domain = self._get_agent_domain(agent_id)
        
        results = {}
        
        if MemoryType.EPISODIC in memory_types:
            results["episodic"] = self.episodic.search(
                query=query,
                limit=limit,
                agent_id=agent_id,
                domain=domain,
                include_global=True
            )
        
        if MemoryType.SEMANTIC in memory_types:
            results["semantic"] = self.semantic.search(
                query=query,
                limit=limit,
                agent_id=agent_id,
                domain=domain,
                include_global=True
            )
        
        if MemoryType.PROCEDURAL in memory_types:
            results["procedural"] = self.procedural.search(
                query=query,
                limit=limit,
                agent_id=agent_id,
                domain=domain,
                include_global=True
            )
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the memory system."""
        return {
            "working_memory": self.working.get_stats(),
            "registered_agents": len(self._agents),
            "agents": [
                {
                    "id": a.agent_id,
                    "name": a.name,
                    "domain": a.domain.value,
                    "last_active": a.last_active.isoformat()
                }
                for a in self._agents.values()
            ]
        }


# Global shared memory store instance
_shared_store: Optional[SharedMemoryStore] = None


def get_memory_store() -> SharedMemoryStore:
    """Get the global shared memory store instance."""
    global _shared_store
    if _shared_store is None:
        _shared_store = SharedMemoryStore()
    return _shared_store

