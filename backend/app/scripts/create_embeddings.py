"""
Create embeddings for existing semantic layer data

This script creates embeddings for existing metrics and glossary terms
that don't have embeddings yet.

Run with: python -m app.scripts.create_embeddings
"""
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.core.config import settings
from app.models.semantic_layer import Metric, BusinessGlossary
from app.services.embedding import EmbeddingService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_embeddings_for_metrics(db: Session, embedding_service: EmbeddingService):
    """Create embeddings for all metrics"""
    logger.info("Creating embeddings for metrics...")
    
    metrics = db.query(Metric).all()
    logger.info(f"Found {len(metrics)} metrics")
    
    embedding_items = []
    for metric in metrics:
        content = f"{metric.display_name}. {metric.description}. "
        content += f"Typical questions: {' '.join(metric.typical_questions or [])}"
        
        embedding_items.append({
            "namespace": "metrics",
            "object_id": str(metric.id),
            "content": content,
            "metadata": {
                "metric_name": metric.name,
                "certified": metric.certified,
                "owner": metric.owner
            }
        })
    
    if embedding_items:
        logger.info(f"Creating {len(embedding_items)} metric embeddings...")
        await embedding_service.store_embeddings_batch(db, embedding_items)
        logger.info(f"✅ Created {len(embedding_items)} metric embeddings")
    else:
        logger.info("No metrics to process")


async def create_embeddings_for_glossary(db: Session, embedding_service: EmbeddingService):
    """Create embeddings for all glossary terms"""
    logger.info("Creating embeddings for glossary terms...")
    
    terms = db.query(BusinessGlossary).all()
    logger.info(f"Found {len(terms)} glossary terms")
    
    embedding_items = []
    for term in terms:
        content = f"{term.term}: {term.definition}. "
        if term.examples:
            content += f"Examples: {' '.join(term.examples)}"
        
        embedding_items.append({
            "namespace": "glossary",
            "object_id": str(term.id),
            "content": content,
            "metadata": {
                "term": term.term,
                "category": term.category
            }
        })
    
    if embedding_items:
        logger.info(f"Creating {len(embedding_items)} glossary embeddings...")
        await embedding_service.store_embeddings_batch(db, embedding_items)
        logger.info(f"✅ Created {len(embedding_items)} glossary embeddings")
    else:
        logger.info("No glossary terms to process")


async def main():
    """Main function"""
    logger.info("=" * 60)
    logger.info("CREATING EMBEDDINGS FOR EXISTING DATA")
    logger.info("=" * 60)
    
    # Create sync engine and session
    sync_db_url = settings.database_url.replace('+asyncpg', '')
    engine = create_engine(sync_db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    embedding_service = EmbeddingService()
    
    try:
        # Create embeddings
        await create_embeddings_for_metrics(db, embedding_service)
        await create_embeddings_for_glossary(db, embedding_service)
        
        logger.info("=" * 60)
        logger.info("✅ EMBEDDINGS CREATED SUCCESSFULLY!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Error creating embeddings: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())


