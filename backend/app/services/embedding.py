"""Embedding Service

Generates and manages vector embeddings for semantic search.
Uses sentence-transformers for high-quality embeddings.
"""
from typing import List, Dict, Optional
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating and managing embeddings
    
    Uses all-MiniLM-L6-v2 model:
    - 384 dimensions
    - Fast inference (2-3ms per text)
    - Good quality for semantic search
    - Small model size (~80MB)
    """
    
    def __init__(self):
        """Initialize embedding model"""
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.dimension = 384
            logger.info(f"Embedding model loaded: {self.dimension} dimensions")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats (384 dimensions)
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return [0.0] * self.dimension
        
        try:
            # Generate embedding
            embedding = self.model.encode(
                text,
                convert_to_tensor=False,
                show_progress_bar=False
            )
            
            # Convert to list
            if isinstance(embedding, np.ndarray):
                embedding = embedding.tolist()
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (more efficient)
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings
        """
        if not texts:
            return []
        
        try:
            embeddings = self.model.encode(
                texts,
                convert_to_tensor=False,
                show_progress_bar=False,
                batch_size=32
            )
            
            # Convert to list of lists
            if isinstance(embeddings, np.ndarray):
                embeddings = embeddings.tolist()
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise
    
    async def store_embedding(
        self,
        db: Session,
        namespace: str,
        object_id: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Store embedding in database
        
        Args:
            db: Database session
            namespace: Namespace (e.g., 'metrics', 'queries', 'tables')
            object_id: Unique identifier for the object
            content: Text content to embed
            metadata: Optional metadata as JSON
        """
        try:
            # Generate embedding
            embedding = self.generate_embedding(content)
            
            # Convert list to PostgreSQL vector format
            embedding_str = '[' + ','.join(map(str, embedding)) + ']'
            
            # Upsert query
            query = text("""
                INSERT INTO embeddings (namespace, object_id, content, embedding, embedding_metadata)
                VALUES (:namespace, :object_id, :content, CAST(:embedding_vec AS vector), :embedding_metadata)
                ON CONFLICT (namespace, object_id) 
                DO UPDATE SET 
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding,
                    embedding_metadata = EXCLUDED.embedding_metadata,
                    created_at = NOW()
            """)
            
            db.execute(query, {
                "namespace": namespace,
                "object_id": object_id,
                "content": content,
                "embedding_vec": embedding_str,
                "embedding_metadata": json.dumps(metadata or {})
            })
            db.commit()
            
            logger.info(f"Stored embedding: {namespace}/{object_id}")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error storing embedding: {e}")
            raise
    
    async def store_embeddings_batch(
        self,
        db: Session,
        items: List[Dict]
    ) -> None:
        """
        Store multiple embeddings efficiently
        
        Args:
            db: Database session
            items: List of dicts with keys: namespace, object_id, content, metadata
        """
        if not items:
            return
        
        try:
            # Generate all embeddings in batch
            contents = [item['content'] for item in items]
            embeddings = self.generate_embeddings_batch(contents)
            
            # Prepare insert data
            for item, embedding in zip(items, embeddings):
                embedding_str = '[' + ','.join(map(str, embedding)) + ']'
                
                query = text("""
                    INSERT INTO embeddings (namespace, object_id, content, embedding, embedding_metadata)
                    VALUES (:namespace, :object_id, :content, CAST(:embedding_vec AS vector), :embedding_metadata)
                    ON CONFLICT (namespace, object_id) 
                    DO UPDATE SET 
                        content = EXCLUDED.content,
                        embedding = EXCLUDED.embedding,
                        embedding_metadata = EXCLUDED.embedding_metadata,
                        created_at = NOW()
                """)
                
                db.execute(query, {
                    "namespace": item['namespace'],
                    "object_id": item['object_id'],
                    "content": item['content'],
                    "embedding_vec": embedding_str,
                    "embedding_metadata": json.dumps(item.get('metadata', {}))
                })
            
            db.commit()
            logger.info(f"Stored {len(items)} embeddings in batch")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error storing batch embeddings: {e}")
            raise
    
    async def similarity_search(
        self,
        db: Session,
        query: str,
        namespace: str,
        top_k: int = 5,
        threshold: float = 0.5
    ) -> List[Dict]:
        """
        Find similar items using cosine similarity
        
        Args:
            db: Database session
            query: Query text
            namespace: Namespace to search in
            top_k: Number of results to return
            threshold: Minimum similarity score (0-1)
            
        Returns:
            List of dicts with keys: object_id, content, metadata, similarity
        """
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
            
            # Cosine similarity search
            # 1 - (a <=> b) gives cosine similarity (1 = identical, 0 = orthogonal)
            sql = text("""
                SELECT 
                    object_id,
                    content,
                    embedding_metadata as metadata,
                    1 - (embedding <=> CAST(:query_embedding AS vector)) as similarity
                FROM embeddings
                WHERE namespace = :namespace
                    AND 1 - (embedding <=> CAST(:query_embedding AS vector)) > :threshold
                ORDER BY embedding <=> CAST(:query_embedding AS vector)
                LIMIT :top_k
            """)
            
            result = db.execute(sql, {
                "query_embedding": embedding_str,
                "namespace": namespace,
                "threshold": threshold,
                "top_k": top_k
            })
            
            results = [
                {
                    "object_id": row.object_id,
                    "content": row.content,
                    "metadata": row.embedding_metadata,
                    "similarity": float(row.similarity)
                }
                for row in result
            ]
            
            logger.info(
                f"Similarity search: {namespace}, "
                f"found {len(results)} results above {threshold}"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            raise
    
    async def delete_embeddings(
        self,
        db: Session,
        namespace: str,
        object_ids: Optional[List[str]] = None
    ) -> int:
        """
        Delete embeddings
        
        Args:
            db: Database session
            namespace: Namespace to delete from
            object_ids: Optional list of specific object IDs to delete
            
        Returns:
            Number of embeddings deleted
        """
        try:
            if object_ids:
                query = text("""
                    DELETE FROM embeddings
                    WHERE namespace = :namespace
                        AND object_id = ANY(:object_ids)
                """)
                result = db.execute(query, {
                    "namespace": namespace,
                    "object_ids": object_ids
                })
            else:
                query = text("""
                    DELETE FROM embeddings
                    WHERE namespace = :namespace
                """)
                result = db.execute(query, {"namespace": namespace})
            
            db.commit()
            deleted_count = result.rowcount
            
            logger.info(f"Deleted {deleted_count} embeddings from {namespace}")
            return deleted_count
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting embeddings: {e}")
            raise


# Singleton instance
@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    """Get singleton embedding service instance"""
    return EmbeddingService()


