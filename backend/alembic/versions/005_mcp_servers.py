"""Add MCP servers tables

Revision ID: 005
Revises: 004
Create Date: 2025-11-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # MCP Servers table
    op.create_table(
        'mcp_servers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('server_type', sa.String(100), nullable=False),
        
        # Connection Details
        sa.Column('config', postgresql.JSONB, nullable=False),
        
        # Status
        sa.Column('status', sa.String(50), server_default='inactive'),
        sa.Column('last_connected_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('error_message', sa.Text),
        
        # Metadata
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        
        # Organization (multi-tenant support)
        sa.Column('organization_id', postgresql.UUID(as_uuid=True)),
    )
    
    # Indexes
    op.create_index('idx_mcp_servers_type', 'mcp_servers', ['server_type'])
    op.create_index('idx_mcp_servers_status', 'mcp_servers', ['status'])
    op.create_index('idx_mcp_servers_org', 'mcp_servers', ['organization_id'])
    
    # Unique constraint
    op.execute("""
        CREATE UNIQUE INDEX uq_mcp_servers_name_org 
        ON mcp_servers (name, COALESCE(organization_id, '00000000-0000-0000-0000-000000000000'::uuid))
    """)
    
    # MCP Resources table
    op.create_table(
        'mcp_resources',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('server_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Resource Identity
        sa.Column('resource_uri', sa.String(500), nullable=False),
        sa.Column('resource_type', sa.String(100)),
        sa.Column('name', sa.String(255)),
        sa.Column('description', sa.Text),
        
        # Resource Metadata
        sa.Column('resource_metadata', postgresql.JSONB),
        
        # Caching
        sa.Column('last_synced_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        
        # Foreign key
        sa.ForeignKeyConstraint(['server_id'], ['mcp_servers.id'], ondelete='CASCADE'),
    )
    
    # Indexes
    op.create_index('idx_mcp_resources_server', 'mcp_resources', ['server_id'])
    op.create_index('idx_mcp_resources_type', 'mcp_resources', ['resource_type'])
    
    # Unique constraint
    op.create_unique_constraint('uq_mcp_resources_server_uri', 'mcp_resources', ['server_id', 'resource_uri'])
    
    # MCP Access Log table
    op.create_table(
        'mcp_access_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('server_id', postgresql.UUID(as_uuid=True)),
        sa.Column('user_id', postgresql.UUID(as_uuid=True)),
        
        # Operation Details
        sa.Column('operation', sa.String(100)),
        sa.Column('resource_uri', sa.String(500)),
        
        # Result
        sa.Column('status', sa.String(50)),
        sa.Column('duration_ms', sa.Integer),
        sa.Column('error_message', sa.Text),
        
        sa.Column('timestamp', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        
        # Foreign keys
        sa.ForeignKeyConstraint(['server_id'], ['mcp_servers.id'], ondelete='SET NULL'),
    )
    
    # Indexes for querying logs
    op.create_index('idx_mcp_log_server', 'mcp_access_log', ['server_id'])
    op.create_index('idx_mcp_log_user', 'mcp_access_log', ['user_id'])
    op.create_index('idx_mcp_log_timestamp', 'mcp_access_log', ['timestamp'])
    op.create_index('idx_mcp_log_status', 'mcp_access_log', ['status'])


def downgrade() -> None:
    op.drop_table('mcp_access_log')
    op.drop_table('mcp_resources')
    op.drop_table('mcp_servers')

