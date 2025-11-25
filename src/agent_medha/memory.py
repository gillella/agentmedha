import os
# Force removal of ADC if present to avoid conflicts
if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
    del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

class MemoryManager:
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

    def add_memory(self, text: str, memory_type: str = "episodic", agent_id: str = "global", metadata: Dict[str, Any] = None):
        """
        Adds a memory to the vector store.
        
        Args:
            text: The memory content.
            memory_type: 'episodic', 'semantic', or 'procedural'.
            agent_id: The ID of the agent owning this memory ('global' for shared).
            metadata: Additional metadata.
        """
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "timestamp": datetime.now().isoformat(),
            "memory_type": memory_type,
            "agent_id": agent_id
        })
        
        # Generate embedding
        vector = self.embeddings.embed_query(text)
        
        # Upsert to Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={"text": text, **metadata}
                )
            ]
        )

    def search_memory(self, query: str, memory_type: str = None, agent_id: str = None, limit: int = 5) -> List[Document]:
        """
        Searches for relevant memories with filtering.
        
        Args:
            query: The search query.
            memory_type: Filter by memory type (optional).
            agent_id: Filter by agent ID (optional). If None, searches global + all.
            limit: Number of results.
        """
        vector = self.embeddings.embed_query(query)
        
        # Build filter
        must_filters = []
        if memory_type:
            must_filters.append(models.FieldCondition(key="memory_type", match=models.MatchValue(value=memory_type)))
        
        should_filters = []
        if agent_id:
            # If agent_id is provided, search for that agent's memory OR global memory
            should_filters.append(models.FieldCondition(key="agent_id", match=models.MatchValue(value=agent_id)))
            should_filters.append(models.FieldCondition(key="agent_id", match=models.MatchValue(value="global")))
        
        filter_obj = None
        if must_filters or should_filters:
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
        
        documents = []
        for res in results:
            documents.append(Document(
                page_content=res.payload.get("text", ""),
                metadata=res.payload
            ))
        
        return documents

    def clear_memory(self):
        """Clears all memories (useful for testing)."""
        self.client.delete_collection(self.collection_name)
        self._ensure_collection()
