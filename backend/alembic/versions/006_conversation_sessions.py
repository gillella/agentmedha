"""Add conversation sessions and messages tables (fixed)

Revision ID: 006_fixed
Revises: 005
Create Date: 2025-11-04 15:08:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create conversation_sessions table (using String for status instead of ENUM)
    op.create_table(
        'conversation_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('data_source_id', sa.Integer(), nullable=True),
        sa.Column('context', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('started_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_activity_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['data_source_id'], ['database_connections.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_conversation_sessions_id', 'conversation_sessions', ['id'])
    op.create_index('ix_conversation_sessions_user_id', 'conversation_sessions', ['user_id'])
    op.create_index('ix_conversation_sessions_status', 'conversation_sessions', ['status'])
    
    # Create conversation_messages table (using String for role/type instead of ENUM)
    op.create_table(
        'conversation_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='user'),
        sa.Column('message_type', sa.String(length=50), nullable=False, server_default='user_message'),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('sql_query', sa.Text(), nullable=True),
        sa.Column('sql_explanation', sa.Text(), nullable=True),
        sa.Column('results', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('result_count', sa.Integer(), nullable=True),
        sa.Column('visualization_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('context_stats', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('suggested_actions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_code', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['session_id'], ['conversation_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_conversation_messages_id', 'conversation_messages', ['id'])
    op.create_index('ix_conversation_messages_session_id', 'conversation_messages', ['session_id'])
    op.create_index('ix_conversation_messages_created_at', 'conversation_messages', ['created_at'])


def downgrade() -> None:
    # Drop tables
    op.drop_index('ix_conversation_messages_created_at', table_name='conversation_messages')
    op.drop_index('ix_conversation_messages_session_id', table_name='conversation_messages')
    op.drop_index('ix_conversation_messages_id', table_name='conversation_messages')
    op.drop_table('conversation_messages')
    
    op.drop_index('ix_conversation_sessions_status', table_name='conversation_sessions')
    op.drop_index('ix_conversation_sessions_user_id', table_name='conversation_sessions')
    op.drop_index('ix_conversation_sessions_id', table_name='conversation_sessions')
    op.drop_table('conversation_sessions')

