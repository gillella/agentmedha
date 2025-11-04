"""Add pgvector extension and embeddings table

Revision ID: 004
Revises: 003
Create Date: 2025-11-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Embeddings table (without embedding column first)
    op.create_table(
        'embeddings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('namespace', sa.String(100), nullable=False),
        sa.Column('object_id', sa.String(255), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('embedding_metadata', postgresql.JSONB),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.UniqueConstraint('namespace', 'object_id', name='uq_namespace_object')
    )
    
    # Add vector column using raw SQL
    op.execute('ALTER TABLE embeddings ADD COLUMN embedding vector(384)')

    # Create vector index for similarity search
    # Using ivfflat index for fast approximate nearest neighbor search
    op.execute("""
        CREATE INDEX idx_embeddings_vector 
        ON embeddings 
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
    """)

    op.create_index('idx_embeddings_namespace', 'embeddings', ['namespace'])
    op.create_index('idx_embeddings_object_id', 'embeddings', ['object_id'])


def downgrade() -> None:
    op.drop_table('embeddings')
    op.execute('DROP EXTENSION IF EXISTS vector')


