"""
Seed Semantic Layer

Populate the semantic layer with initial:
- Business metrics
- Glossary terms  
- Business rules
- Generate embeddings

Run with: python -m app.scripts.seed_semantic_layer
"""
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.core.config import settings
from app.models.semantic_layer import Metric, BusinessGlossary, BusinessRule
from app.services.embedding import EmbeddingService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


SAMPLE_METRICS = [
    {
        "name": "revenue",
        "display_name": "Total Revenue",
        "description": "Total revenue from completed orders",
        "sql_definition": "SUM(orders.total_amount)",
        "data_sources": {"tables": ["orders"], "columns": ["total_amount"]},
        "aggregation": "sum",
        "format": "currency",
        "filters": {"status": "completed", "paid": True},
        "owner": "CFO",
        "certified": True,
        "tags": ["financial", "kpi"],
        "typical_questions": [
            "What is our total revenue?",
            "Show me revenue this quarter",
            "What was revenue last month?",
            "Revenue by region"
        ],
        "related_metrics": ["arr", "mrr", "profit"]
    },
    {
        "name": "arr",
        "display_name": "Annual Recurring Revenue",
        "description": "Annualized recurring revenue from active subscriptions",
        "sql_definition": "SUM(subscriptions.monthly_amount * 12)",
        "data_sources": {"tables": ["subscriptions"], "columns": ["monthly_amount"]},
        "aggregation": "sum",
        "format": "currency",
        "filters": {"status": "active"},
        "owner": "CFO",
        "certified": True,
        "tags": ["financial", "kpi", "saas"],
        "typical_questions": [
            "What is our ARR?",
            "Show ARR by customer segment",
            "How has ARR changed over time?",
            "ARR growth rate"
        ],
        "related_metrics": ["revenue", "mrr", "churn"]
    },
    {
        "name": "mrr",
        "display_name": "Monthly Recurring Revenue",
        "description": "Monthly recurring revenue from active subscriptions",
        "sql_definition": "SUM(subscriptions.monthly_amount)",
        "data_sources": {"tables": ["subscriptions"], "columns": ["monthly_amount"]},
        "aggregation": "sum",
        "format": "currency",
        "filters": {"status": "active"},
        "owner": "CFO",
        "certified": True,
        "tags": ["financial", "kpi", "saas"],
        "typical_questions": [
            "What is our MRR?",
            "Show MRR trend",
            "MRR by plan type",
            "New MRR this month"
        ],
        "related_metrics": ["arr", "churn", "expansion_mrr"]
    },
    {
        "name": "customer_count",
        "display_name": "Active Customer Count",
        "description": "Number of active customers",
        "sql_definition": "COUNT(DISTINCT customers.id)",
        "data_sources": {"tables": ["customers"], "columns": ["id", "status"]},
        "aggregation": "count",
        "format": "number",
        "filters": {"status": "active"},
        "owner": "COO",
        "certified": True,
        "tags": ["customer", "kpi"],
        "typical_questions": [
            "How many customers do we have?",
            "Customer count by segment",
            "New customers this month",
            "Active customers"
        ],
        "related_metrics": ["churn_rate", "ltv"]
    },
    {
        "name": "churn_rate",
        "display_name": "Monthly Churn Rate",
        "description": "Percentage of customers who cancelled in the month",
        "sql_definition": "(COUNT(CASE WHEN cancelled_at IS NOT NULL THEN 1 END) * 100.0 / COUNT(*))",
        "data_sources": {"tables": ["customers"], "columns": ["cancelled_at"]},
        "aggregation": "calculated",
        "format": "percentage",
        "owner": "COO",
        "certified": True,
        "tags": ["customer", "kpi", "saas"],
        "typical_questions": [
            "What is our churn rate?",
            "Churn rate trend",
            "Churn by customer segment",
            "Monthly churn"
        ],
        "related_metrics": ["customer_count", "arr", "retention_rate"]
    }
]

SAMPLE_GLOSSARY = [
    {
        "term": "ARR",
        "definition": "Annual Recurring Revenue - predictable revenue from subscriptions normalized to a one-year period",
        "category": "financial",
        "synonyms": ["annual_recurring_revenue"],
        "related_terms": ["MRR", "revenue"],
        "examples": ["ARR = MRR × 12"]
    },
    {
        "term": "MRR",
        "definition": "Monthly Recurring Revenue - predictable revenue from subscriptions in a given month",
        "category": "financial",
        "synonyms": ["monthly_recurring_revenue"],
        "related_terms": ["ARR", "revenue"],
        "examples": ["MRR = sum of all subscription amounts for active customers"]
    },
    {
        "term": "churn",
        "definition": "Customer who cancelled their subscription or stopped using the service",
        "category": "saas_metrics",
        "synonyms": ["attrition", "customer_loss"],
        "related_terms": ["retention", "churn_rate"],
        "examples": ["Monthly churn rate = (churned customers / total customers) × 100"]
    },
    {
        "term": "LTV",
        "definition": "Lifetime Value - predicted revenue from a customer over their entire relationship",
        "category": "financial",
        "synonyms": ["lifetime_value", "CLV", "customer_lifetime_value"],
        "related_terms": ["CAC", "revenue"],
        "examples": ["LTV = ARPU / churn_rate"]
    },
    {
        "term": "CAC",
        "definition": "Customer Acquisition Cost - average cost to acquire a new customer",
        "category": "financial",
        "synonyms": ["customer_acquisition_cost"],
        "related_terms": ["LTV", "marketing_spend"],
        "examples": ["CAC = total marketing spend / new customers"]
    },
    {
        "term": "active_customer",
        "definition": "Customer with an active subscription or who has made a purchase in the last 90 days",
        "category": "customer",
        "synonyms": ["active_user"],
        "related_terms": ["churn", "retention"],
        "examples": ["status = 'active' OR last_purchase_date > NOW() - INTERVAL '90 days'"]
    }
]

SAMPLE_RULES = [
    {
        "rule_type": "fiscal_calendar",
        "name": "Fiscal Year Definition",
        "definition": {
            "fiscal_year_start": "November 1",
            "fiscal_year_end": "October 31",
            "quarters": {
                "Q1": {"start": "11-01", "end": "01-31", "months": ["November", "December", "January"]},
                "Q2": {"start": "02-01", "end": "04-30", "months": ["February", "March", "April"]},
                "Q3": {"start": "05-01", "end": "07-31", "months": ["May", "June", "July"]},
                "Q4": {"start": "08-01", "end": "10-31", "months": ["August", "September", "October"]}
            }
        },
        "applies_to": ["all"],
        "active": True
    },
    {
        "rule_type": "data_retention",
        "name": "Query Log Retention",
        "definition": {
            "retention_days": 90,
            "archive_after_days": 30,
            "description": "Query logs retained for 90 days, archived after 30 days"
        },
        "applies_to": ["query_logs"],
        "active": True
    },
    {
        "rule_type": "aggregation",
        "name": "Revenue Recognition",
        "definition": {
            "rule": "Revenue is recognized when payment is received and order is completed",
            "conditions": ["payment_status = 'paid'", "order_status = 'completed'"],
            "effective_date_field": "payment_date"
        },
        "applies_to": ["orders", "revenue"],
        "active": True
    }
]


async def seed_metrics(db: Session, embedding_service: EmbeddingService):
    """Seed business metrics"""
    logger.info("Seeding metrics...")
    
    embedding_items = []
    
    for data in SAMPLE_METRICS:
        # Check if exists
        existing = db.query(Metric).filter(Metric.name == data["name"]).first()
        if existing:
            logger.info(f"Metric '{data['name']}' already exists, skipping")
            continue
        
        # Create metric
        metric = Metric(**data)
        db.add(metric)
        db.flush()  # Get ID
        
        # Prepare embedding
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
        
        logger.info(f"Created metric: {metric.name}")
    
    db.commit()
    
    # Create embeddings in batch
    if embedding_items:
        logger.info(f"Creating {len(embedding_items)} embeddings...")
        await embedding_service.store_embeddings_batch(db, embedding_items)
    
    logger.info(f"✅ Seeded {len(embedding_items)} metrics")


async def seed_glossary(db: Session, embedding_service: EmbeddingService):
    """Seed business glossary"""
    logger.info("Seeding glossary...")
    
    embedding_items = []
    
    for data in SAMPLE_GLOSSARY:
        # Check if exists
        existing = db.query(BusinessGlossary).filter(
            BusinessGlossary.term == data["term"]
        ).first()
        if existing:
            logger.info(f"Term '{data['term']}' already exists, skipping")
            continue
        
        # Create term
        term = BusinessGlossary(**data)
        db.add(term)
        db.flush()
        
        # Prepare embedding
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
        
        logger.info(f"Created glossary term: {term.term}")
    
    db.commit()
    
    # Create embeddings
    if embedding_items:
        logger.info(f"Creating {len(embedding_items)} embeddings...")
        await embedding_service.store_embeddings_batch(db, embedding_items)
    
    logger.info(f"✅ Seeded {len(embedding_items)} glossary terms")


def seed_rules(db: Session):
    """Seed business rules"""
    logger.info("Seeding business rules...")
    
    count = 0
    for data in SAMPLE_RULES:
        # Check if exists
        existing = db.query(BusinessRule).filter(
            BusinessRule.rule_type == data["rule_type"],
            BusinessRule.name == data["name"]
        ).first()
        if existing:
            logger.info(f"Rule '{data['name']}' already exists, skipping")
            continue
        
        # Create rule
        rule = BusinessRule(**data)
        db.add(rule)
        count += 1
        
        logger.info(f"Created rule: {rule.name}")
    
    db.commit()
    logger.info(f"✅ Seeded {count} business rules")


async def main():
    """Main seeding function"""
    logger.info("=" * 60)
    logger.info("SEEDING SEMANTIC LAYER")
    logger.info("=" * 60)
    
    # Create sync engine and session for seeding
    # Convert async URL to sync URL
    sync_db_url = settings.database_url.replace('+asyncpg', '')
    engine = create_engine(sync_db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    embedding_service = EmbeddingService()
    
    try:
        # Seed metrics
        await seed_metrics(db, embedding_service)
        
        # Seed glossary
        await seed_glossary(db, embedding_service)
        
        # Seed rules (no embeddings needed)
        seed_rules(db)
        
        logger.info("=" * 60)
        logger.info("✅ SEMANTIC LAYER SEEDED SUCCESSFULLY!")
        logger.info("=" * 60)
        
        # Print summary
        metrics_count = db.query(Metric).count()
        glossary_count = db.query(BusinessGlossary).count()
        rules_count = db.query(BusinessRule).count()
        
        logger.info(f"\nSummary:")
        logger.info(f"  - Metrics: {metrics_count}")
        logger.info(f"  - Glossary terms: {glossary_count}")
        logger.info(f"  - Business rules: {rules_count}")
        
    except Exception as e:
        logger.error(f"❌ Error seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())


