"""Add semantic layer tables

Revision ID: 003
Revises: 
Create Date: 2025-11-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Business Metrics table
    op.create_table(
        'metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('display_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('sql_definition', sa.Text, nullable=False),
        sa.Column('data_sources', postgresql.JSONB),
        sa.Column('aggregation', sa.String(50)),
        sa.Column('format', sa.String(50)),
        sa.Column('filters', postgresql.JSONB),
        sa.Column('owner', sa.String(255)),
        sa.Column('certified', sa.Boolean, server_default='false'),
        sa.Column('certification_date', sa.TIMESTAMP(timezone=True)),
        sa.Column('tags', postgresql.ARRAY(sa.Text)),
        sa.Column('typical_questions', postgresql.ARRAY(sa.Text)),
        sa.Column('related_metrics', postgresql.ARRAY(sa.Text)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('created_by', sa.Integer, sa.ForeignKey('users.id')),
    )
    op.create_index('idx_metrics_name', 'metrics', ['name'])
    op.create_index('idx_metrics_tags', 'metrics', ['tags'], postgresql_using='gin')
    op.create_index('idx_metrics_certified', 'metrics', ['certified'])

    # Business Glossary table
    op.create_table(
        'business_glossary',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('term', sa.String(255), nullable=False, unique=True),
        sa.Column('definition', sa.Text, nullable=False),
        sa.Column('category', sa.String(100)),
        sa.Column('synonyms', postgresql.ARRAY(sa.Text)),
        sa.Column('related_terms', postgresql.ARRAY(sa.Text)),
        sa.Column('examples', postgresql.ARRAY(sa.Text)),
        sa.Column('owner', sa.String(255)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('idx_glossary_term', 'business_glossary', ['term'])
    op.create_index('idx_glossary_category', 'business_glossary', ['category'])

    # Business Rules table
    op.create_table(
        'business_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('rule_type', sa.String(100), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('definition', postgresql.JSONB, nullable=False),
        sa.Column('applies_to', postgresql.ARRAY(sa.Text)),
        sa.Column('active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('idx_rules_type', 'business_rules', ['rule_type'])
    op.create_index('idx_rules_active', 'business_rules', ['active'])

    # Data Lineage table
    op.create_table(
        'data_lineage',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('source_table', sa.String(255), nullable=False),
        sa.Column('source_database', sa.String(255), nullable=False),
        sa.Column('target_table', sa.String(255), nullable=False),
        sa.Column('target_database', sa.String(255), nullable=False),
        sa.Column('relationship_type', sa.String(50)),
        sa.Column('transformation_logic', sa.Text),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('idx_lineage_source', 'data_lineage', ['source_database', 'source_table'])
    op.create_index('idx_lineage_target', 'data_lineage', ['target_database', 'target_table'])

    # Context Cache table
    op.create_table(
        'context_cache',
        sa.Column('cache_key', sa.String(255), primary_key=True),
        sa.Column('context_type', sa.String(50), nullable=False),
        sa.Column('content', postgresql.JSONB, nullable=False),
        sa.Column('relevance_score', sa.Float),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('idx_cache_type', 'context_cache', ['context_type'])
    op.create_index('idx_cache_expires', 'context_cache', ['expires_at'])


def downgrade() -> None:
    op.drop_table('context_cache')
    op.drop_table('data_lineage')
    op.drop_table('business_rules')
    op.drop_table('business_glossary')
    op.drop_table('metrics')


