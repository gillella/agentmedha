"""
Semantic Memory - Facts, knowledge, entities, and relationships.

Semantic memory stores:
- Facts and general knowledge
- User preferences learned over time
- Entity profiles (contacts, accounts, topics)
- Relationships between entities
- Extracted knowledge from episodic memories

Features:
- Entity-centric storage
- Knowledge graph capabilities
- Preference tracking
- Relationship mapping
"""

import os
import uuid
import hashlib
from typing import Dict, Any, Optional, List, Set
from datetime import datetime
from qdrant_client.http import models

from .base import (
    BaseMemory, MemoryRecord, MemoryType, MemoryScope, 
    MemoryDomain
)


def _make_uuid(name: str) -> str:
    """Generate a deterministic UUID from a string name."""
    return str(uuid.UUID(hashlib.md5(name.encode()).hexdigest()))


class EntityProfile:
    """Profile for a semantic entity (person, topic, account, etc.)"""
    
    def __init__(
        self,
        entity_id: str,
        entity_type: str,  # "person", "topic", "account", "preference", etc.
        name: str,
        attributes: Dict[str, Any] = None,
        relationships: Dict[str, List[str]] = None,  # {"works_with": ["entity2"], "related_to": [...]}
    ):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.name = name
        self.attributes = attributes or {}
        self.relationships = relationships or {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.mention_count = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "name": self.name,
            "attributes": self.attributes,
            "relationships": self.relationships,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "mention_count": self.mention_count,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EntityProfile":
        profile = cls(
            entity_id=data["entity_id"],
            entity_type=data["entity_type"],
            name=data["name"],
            attributes=data.get("attributes", {}),
            relationships=data.get("relationships", {}),
        )
        profile.created_at = datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now()
        profile.updated_at = datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now()
        profile.mention_count = data.get("mention_count", 0)
        return profile


class SemanticMemory(BaseMemory):
    """
    Long-term semantic memory for facts, knowledge, and entities.
    
    Features:
    - Entity profiles with attributes
    - Relationship tracking between entities
    - Preference learning and storage
    - Fact verification and updating
    - Knowledge consolidation from episodes
    """
    
    def __init__(self, collection_name: str = "agentmedha_semantic"):
        super().__init__(collection_name)
        self._entity_collection = f"{collection_name}_entities"
        self._ensure_entity_collection()
    
    def _ensure_entity_collection(self):
        """Ensure entity collection exists."""
        try:
            self.client.get_collection(self._entity_collection)
        except Exception:
            print(f"Creating collection: {self._entity_collection}")
            self.client.create_collection(
                collection_name=self._entity_collection,
                vectors_config=models.VectorParams(
                    size=768,
                    distance=models.Distance.COSINE
                )
            )
    
    # ==================== FACT STORAGE ====================
    
    def add(self, record: MemoryRecord) -> str:
        """Add a semantic memory (fact/knowledge)."""
        record.memory_type = MemoryType.SEMANTIC
        
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
    
    def add_fact(
        self,
        fact: str,
        category: str = "general",
        confidence: float = 1.0,
        agent_id: str = "supervisor",
        domain: MemoryDomain = MemoryDomain.GENERAL,
        scope: MemoryScope = MemoryScope.GLOBAL,
        source: Optional[str] = None,
        entities: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Store a fact in semantic memory.
        
        Args:
            fact: The fact content
            category: Category of fact (preference, contact, topic, etc.)
            confidence: Confidence score (0.0 to 1.0)
            agent_id: Agent storing this fact
            domain: Domain (email, social, etc.)
            scope: Access scope
            source: Where this fact came from
            entities: Related entities
            metadata: Additional metadata
            
        Returns:
            The fact ID
        """
        record = MemoryRecord(
            content=fact,
            memory_type=MemoryType.SEMANTIC,
            scope=scope,
            domain=domain,
            agent_id=agent_id,
            importance=confidence,
            entities=entities or [],
            metadata={
                "category": category,
                "confidence": confidence,
                "source": source,
                **(metadata or {})
            }
        )
        return self.add(record)
    
    def add_preference(
        self,
        preference: str,
        category: str = "general",
        confidence: float = 0.8,
        agent_id: str = "supervisor",
        domain: MemoryDomain = MemoryDomain.GENERAL,
    ) -> str:
        """
        Store a user preference.
        
        Args:
            preference: The preference (e.g., "User prefers dark mode")
            category: Category (ui, communication, scheduling, etc.)
            confidence: How confident we are about this preference
            agent_id: Which agent learned this
            domain: Which domain this applies to
            
        Returns:
            The preference ID
        """
        return self.add_fact(
            fact=preference,
            category=f"preference_{category}",
            confidence=confidence,
            agent_id=agent_id,
            domain=domain,
            scope=MemoryScope.GLOBAL,  # Preferences are usually global
            source="learned"
        )
    
    def search(
        self,
        query: str,
        limit: int = 5,
        agent_id: Optional[str] = None,
        domain: Optional[MemoryDomain] = None,
        scope: Optional[MemoryScope] = None,
        category: Optional[str] = None,
        min_confidence: float = 0.0,
        include_global: bool = True
    ) -> List[MemoryRecord]:
        """
        Search semantic memories.
        
        Args:
            query: Search query
            limit: Maximum results
            agent_id: Filter by agent
            domain: Filter by domain
            scope: Filter by scope
            category: Filter by category
            min_confidence: Minimum confidence score
            include_global: Include global memories
            
        Returns:
            List of matching memory records
        """
        vector = self._embed(query)
        
        must_filters = [
            models.FieldCondition(
                key="memory_type",
                match=models.MatchValue(value=MemoryType.SEMANTIC.value)
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
        
        if category:
            must_filters.append(
                models.FieldCondition(
                    key="category",
                    match=models.MatchValue(value=category)
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
        
        return [MemoryRecord.from_dict(r.payload) for r in results]
    
    def get_preferences(
        self,
        domain: Optional[MemoryDomain] = None,
        category: Optional[str] = None,
        limit: int = 20
    ) -> List[MemoryRecord]:
        """
        Get all stored preferences.
        
        Args:
            domain: Filter by domain
            category: Filter by category
            limit: Maximum results
            
        Returns:
            List of preference records
        """
        must_filters = [
            models.FieldCondition(
                key="memory_type",
                match=models.MatchValue(value=MemoryType.SEMANTIC.value)
            ),
            models.FieldCondition(
                key="category",
                match=models.MatchText(text="preference_")
            )
        ]
        
        if domain:
            must_filters.append(
                models.FieldCondition(
                    key="domain",
                    match=models.MatchValue(value=domain.value)
                )
            )
        
        if category:
            must_filters.append(
                models.FieldCondition(
                    key="category",
                    match=models.MatchValue(value=f"preference_{category}")
                )
            )
        
        filter_obj = models.Filter(must=must_filters)
        
        results = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=filter_obj,
            limit=limit
        )[0]
        
        return [MemoryRecord.from_dict(r.payload) for r in results]
    
    def get(self, memory_id: str) -> Optional[MemoryRecord]:
        """Get a specific semantic memory."""
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
        """Update a semantic memory."""
        try:
            self.client.set_payload(
                collection_name=self.collection_name,
                payload=updates,
                points=[memory_id]
            )
            return True
        except Exception:
            return False
    
    def delete(self, memory_id: str) -> bool:
        """Delete a semantic memory."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(points=[memory_id])
            )
            return True
        except Exception:
            return False
    
    # ==================== ENTITY MANAGEMENT ====================
    
    def add_entity(self, profile: EntityProfile) -> str:
        """
        Add or update an entity profile.
        
        Args:
            profile: The entity profile
            
        Returns:
            The entity ID
        """
        # Create searchable text from profile
        search_text = f"{profile.entity_type}: {profile.name}. " + \
                      " ".join([f"{k}: {v}" for k, v in profile.attributes.items()])
        
        vector = self._embed(search_text)
        
        self.client.upsert(
            collection_name=self._entity_collection,
            points=[
                models.PointStruct(
                    id=profile.entity_id,
                    vector=vector,
                    payload=profile.to_dict()
                )
            ]
        )
        
        return profile.entity_id
    
    def get_entity(self, entity_id: str) -> Optional[EntityProfile]:
        """Get an entity by ID."""
        try:
            results = self.client.retrieve(
                collection_name=self._entity_collection,
                ids=[entity_id]
            )
            if results:
                return EntityProfile.from_dict(results[0].payload)
            return None
        except Exception:
            return None
    
    def search_entities(
        self,
        query: str,
        entity_type: Optional[str] = None,
        limit: int = 5
    ) -> List[EntityProfile]:
        """
        Search for entities.
        
        Args:
            query: Search query
            entity_type: Filter by entity type
            limit: Maximum results
            
        Returns:
            List of matching entity profiles
        """
        vector = self._embed(query)
        
        filter_obj = None
        if entity_type:
            filter_obj = models.Filter(
                must=[
                    models.FieldCondition(
                        key="entity_type",
                        match=models.MatchValue(value=entity_type)
                    )
                ]
            )
        
        results = self.client.query_points(
            collection_name=self._entity_collection,
            query=vector,
            limit=limit,
            query_filter=filter_obj
        ).points
        
        return [EntityProfile.from_dict(r.payload) for r in results]
    
    def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update entity attributes.
        
        Args:
            entity_id: The entity to update
            updates: Attribute updates
            
        Returns:
            Success status
        """
        entity = self.get_entity(entity_id)
        if not entity:
            return False
        
        entity.attributes.update(updates)
        entity.updated_at = datetime.now()
        
        self.add_entity(entity)
        return True
    
    def add_relationship(
        self,
        from_entity: str,
        relationship: str,
        to_entity: str
    ) -> bool:
        """
        Add a relationship between entities.
        
        Args:
            from_entity: Source entity ID
            relationship: Relationship type (e.g., "works_with", "related_to")
            to_entity: Target entity ID
            
        Returns:
            Success status
        """
        entity = self.get_entity(from_entity)
        if not entity:
            return False
        
        if relationship not in entity.relationships:
            entity.relationships[relationship] = []
        
        if to_entity not in entity.relationships[relationship]:
            entity.relationships[relationship].append(to_entity)
        
        entity.updated_at = datetime.now()
        self.add_entity(entity)
        return True
    
    def get_related_entities(
        self,
        entity_id: str,
        relationship: Optional[str] = None
    ) -> List[EntityProfile]:
        """
        Get entities related to a given entity.
        
        Args:
            entity_id: The source entity
            relationship: Optional relationship type filter
            
        Returns:
            List of related entity profiles
        """
        entity = self.get_entity(entity_id)
        if not entity:
            return []
        
        related_ids: Set[str] = set()
        
        if relationship:
            related_ids.update(entity.relationships.get(relationship, []))
        else:
            for rels in entity.relationships.values():
                related_ids.update(rels)
        
        profiles = []
        for rid in related_ids:
            profile = self.get_entity(rid)
            if profile:
                profiles.append(profile)
        
        return profiles
    
    def increment_mention(self, entity_id: str) -> bool:
        """Increment mention count for an entity."""
        entity = self.get_entity(entity_id)
        if not entity:
            return False
        
        entity.mention_count += 1
        entity.updated_at = datetime.now()
        self.add_entity(entity)
        return True
    
    # ==================== CONTACT PROFILES ====================
    
    def add_contact(
        self,
        email: str,
        name: Optional[str] = None,
        attributes: Dict[str, Any] = None
    ) -> str:
        """
        Add a contact profile.
        
        Args:
            email: Contact email
            name: Contact name
            attributes: Additional attributes
            
        Returns:
            Contact entity ID
        """
        entity_id = _make_uuid(f"contact_{email}")
        
        profile = EntityProfile(
            entity_id=entity_id,
            entity_type="contact",
            name=name or email,
            attributes={
                "email": email,
                **(attributes or {})
            }
        )
        
        return self.add_entity(profile)
    
    def get_contact(self, email: str) -> Optional[EntityProfile]:
        """Get a contact by email."""
        entity_id = _make_uuid(f"contact_{email}")
        return self.get_entity(entity_id)
    
    def update_contact(self, email: str, updates: Dict[str, Any]) -> bool:
        """Update a contact's attributes."""
        entity_id = _make_uuid(f"contact_{email}")
        return self.update_entity(entity_id, updates)


# Global semantic memory instance
_semantic_memory: Optional[SemanticMemory] = None


def get_semantic_memory() -> SemanticMemory:
    """Get the global semantic memory instance."""
    global _semantic_memory
    if _semantic_memory is None:
        _semantic_memory = SemanticMemory()
    return _semantic_memory

