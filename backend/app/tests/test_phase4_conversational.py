"""
Tests for Phase 4: Conversational Analytics System

Tests session management, query orchestration, and multi-turn conversations.
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import (
    ConversationSession,
    ConversationMessage,
    SessionStatus,
    MessageRole,
    MessageType
)
from app.models.user import User
from app.services.session_manager import SessionManager
from app.services.cache import cache


pytestmark = pytest.mark.asyncio


class TestSessionManager:
    """Test SessionManager service"""
    
    async def test_create_session(self, db: AsyncSession, test_user: User):
        """Test session creation"""
        manager = SessionManager(db)
        
        session = await manager.create_session(
            user_id=test_user.id,
            title="Test Session"
        )
        
        assert session.id is not None
        assert session.user_id == test_user.id
        assert session.title == "Test Session"
        assert session.status == SessionStatus.ACTIVE
        assert session.is_active is True
        assert session.is_expired is False
    
    async def test_add_message(self, db: AsyncSession, test_user: User):
        """Test adding messages to session"""
        manager = SessionManager(db)
        
        # Create session
        session = await manager.create_session(user_id=test_user.id)
        
        # Add user message
        user_msg = await manager.add_message(
            session_id=session.id,
            role=MessageRole.USER,
            content="Show me sales data",
            message_type=MessageType.USER_MESSAGE
        )
        
        assert user_msg.id is not None
        assert user_msg.session_id == session.id
        assert user_msg.role == MessageRole.USER
        assert user_msg.content == "Show me sales data"
        
        # Add assistant message with results
        assistant_msg = await manager.add_message(
            session_id=session.id,
            role=MessageRole.ASSISTANT,
            content="Here are the results",
            message_type=MessageType.QUERY_RESULT,
            sql_query="SELECT * FROM sales",
            results=[{"id": 1, "amount": 100}],
            visualization_config={"type": "table"}
        )
        
        assert assistant_msg.sql_query == "SELECT * FROM sales"
        assert assistant_msg.results is not None
        assert len(assistant_msg.results) == 1
        assert assistant_msg.visualization_config["type"] == "table"
    
    async def test_auto_title_generation(self, db: AsyncSession, test_user: User):
        """Test automatic title generation from first message"""
        manager = SessionManager(db)
        
        session = await manager.create_session(user_id=test_user.id)
        assert session.title is None
        
        # Add first user message
        await manager.add_message(
            session_id=session.id,
            role=MessageRole.USER,
            content="Show me total revenue for this year",
            message_type=MessageType.USER_MESSAGE
        )
        
        # Reload session
        session = await manager.get_session(session.id, load_messages=False)
        assert session.title == "Show me total revenue for this year"
    
    async def test_update_context(self, db: AsyncSession, test_user: User):
        """Test session context updates"""
        manager = SessionManager(db)
        
        session = await manager.create_session(user_id=test_user.id)
        
        # Update context
        success = await manager.update_session_context(
            session.id,
            {"tables_used": ["sales", "customers"], "last_filter": "region='US'"}
        )
        
        assert success is True
        
        # Reload and verify
        session = await manager.get_session(session.id, load_messages=False)
        assert session.context["tables_used"] == ["sales", "customers"]
        assert session.context["last_filter"] == "region='US'"
    
    async def test_set_data_source(self, db: AsyncSession, test_user: User):
        """Test setting data source for session"""
        manager = SessionManager(db)
        
        session = await manager.create_session(user_id=test_user.id)
        assert session.data_source_id is None
        
        # Set data source
        success = await manager.set_data_source(session.id, 123)
        assert success is True
        
        # Reload and verify
        session = await manager.get_session(session.id, load_messages=False)
        assert session.data_source_id == 123
    
    async def test_end_session(self, db: AsyncSession, test_user: User):
        """Test ending a session"""
        manager = SessionManager(db)
        
        session = await manager.create_session(user_id=test_user.id)
        assert session.status == SessionStatus.ACTIVE
        
        # End session
        success = await manager.end_session(session.id, SessionStatus.COMPLETED)
        assert success is True
        
        # Reload and verify
        session = await manager.get_session(session.id, load_messages=False)
        assert session.status == SessionStatus.COMPLETED
        assert session.ended_at is not None
    
    async def test_get_session_history(self, db: AsyncSession, test_user: User):
        """Test retrieving session message history"""
        manager = SessionManager(db)
        
        session = await manager.create_session(user_id=test_user.id)
        
        # Add multiple messages
        await manager.add_message(
            session.id, MessageRole.USER, "Message 1", MessageType.USER_MESSAGE
        )
        await manager.add_message(
            session.id, MessageRole.ASSISTANT, "Response 1", MessageType.INFO
        )
        await manager.add_message(
            session.id, MessageRole.USER, "Message 2", MessageType.USER_MESSAGE
        )
        
        # Get history
        history = await manager.get_session_history(session.id)
        assert len(history) == 3
        assert history[0].content == "Message 1"
        assert history[1].content == "Response 1"
        assert history[2].content == "Message 2"
    
    async def test_get_context_from_history(self, db: AsyncSession, test_user: User):
        """Test extracting context from conversation history"""
        manager = SessionManager(db)
        
        session = await manager.create_session(user_id=test_user.id)
        
        # Add messages with SQL
        await manager.add_message(
            session.id,
            MessageRole.ASSISTANT,
            "Here are sales",
            MessageType.QUERY_RESULT,
            sql_query="SELECT * FROM sales WHERE region='US'"
        )
        
        # Extract context
        context = await manager.get_context_from_history(session.id)
        
        assert "tables_used" in context
        assert "sales" in context["tables_used"]
        assert context["last_sql_query"] is not None
        assert "conversation_summary" in context
    
    async def test_session_expiration(self, db: AsyncSession, test_user: User):
        """Test session expiration"""
        manager = SessionManager(db)
        
        # Create session with short expiration
        session = ConversationSession(
            user_id=test_user.id,
            status=SessionStatus.ACTIVE,
            expires_at=datetime.utcnow() - timedelta(hours=1)  # Expired
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        
        # Get session (should mark as expired)
        session = await manager.get_session(session.id, load_messages=False)
        assert session.status == SessionStatus.EXPIRED


class TestConversationMessage:
    """Test ConversationMessage model"""
    
    async def test_message_properties(self, db: AsyncSession, test_user: User):
        """Test message properties"""
        manager = SessionManager(db)
        
        session = await manager.create_session(user_id=test_user.id)
        
        # User message
        user_msg = await manager.add_message(
            session.id,
            MessageRole.USER,
            "Test",
            MessageType.USER_MESSAGE
        )
        assert user_msg.is_user_message is True
        assert user_msg.is_assistant_message is False
        assert user_msg.has_results is False
        
        # Assistant message with results
        assistant_msg = await manager.add_message(
            session.id,
            MessageRole.ASSISTANT,
            "Results",
            MessageType.QUERY_RESULT,
            results=[{"id": 1}],
            visualization_config={"type": "bar_chart"}
        )
        assert assistant_msg.is_user_message is False
        assert assistant_msg.is_assistant_message is True
        assert assistant_msg.has_results is True
        assert assistant_msg.has_visualization is True
    
    async def test_message_metadata(self, db: AsyncSession, test_user: User):
        """Test message metadata"""
        manager = SessionManager(db)
        
        session = await manager.create_session(user_id=test_user.id)
        
        msg = await manager.add_message(
            session.id,
            MessageRole.ASSISTANT,
            "Test",
            MessageType.INFO,
            metadata={"custom_field": "value"}
        )
        
        assert msg.get_metadata_value("custom_field") == "value"
        assert msg.get_metadata_value("nonexistent", "default") == "default"
        
        # Update metadata
        msg.set_metadata_value("new_field", "new_value")
        await db.commit()
        
        assert msg.get_metadata_value("new_field") == "new_value"


class TestMultiTurnConversation:
    """Test multi-turn conversation scenarios"""
    
    async def test_discovery_then_query_flow(self, db: AsyncSession, test_user: User):
        """Test complete discovery → query flow"""
        manager = SessionManager(db)
        
        # Create session
        session = await manager.create_session(user_id=test_user.id)
        
        # Step 1: User asks for data
        await manager.add_message(
            session.id,
            MessageRole.USER,
            "Show me sales data",
            MessageType.USER_MESSAGE
        )
        
        # Step 2: Assistant shows discovery results
        await manager.add_message(
            session.id,
            MessageRole.ASSISTANT,
            "Found 2 databases",
            MessageType.DISCOVERY,
            metadata={"discovery_results": [{"id": 1, "name": "sales_db"}]}
        )
        
        # Step 3: User selects data source
        await manager.set_data_source(session.id, 1)
        await manager.add_message(
            session.id,
            MessageRole.USER,
            "Selected Sales Database",
            MessageType.USER_MESSAGE
        )
        
        # Step 4: User asks query
        await manager.add_message(
            session.id,
            MessageRole.USER,
            "What's the total revenue?",
            MessageType.USER_MESSAGE
        )
        
        # Step 5: Assistant returns results
        await manager.add_message(
            session.id,
            MessageRole.ASSISTANT,
            "Total revenue is $1.5M",
            MessageType.QUERY_RESULT,
            sql_query="SELECT SUM(revenue) FROM sales",
            results=[{"total_revenue": 1500000}]
        )
        
        # Verify conversation flow
        history = await manager.get_session_history(session.id)
        assert len(history) == 5
        assert history[0].content == "Show me sales data"
        assert history[1].message_type == MessageType.DISCOVERY
        assert history[4].message_type == MessageType.QUERY_RESULT
    
    async def test_follow_up_query(self, db: AsyncSession, test_user: User):
        """Test follow-up query with context"""
        manager = SessionManager(db)
        
        session = await manager.create_session(user_id=test_user.id)
        await manager.set_data_source(session.id, 1)
        
        # First query
        await manager.add_message(
            session.id,
            MessageRole.USER,
            "Show me sales by region",
            MessageType.USER_MESSAGE
        )
        await manager.add_message(
            session.id,
            MessageRole.ASSISTANT,
            "Sales by region",
            MessageType.QUERY_RESULT,
            sql_query="SELECT region, SUM(amount) FROM sales GROUP BY region"
        )
        
        # Update context
        await manager.update_session_context(
            session.id,
            {"tables_used": ["sales"], "last_groupby": "region"}
        )
        
        # Follow-up query
        await manager.add_message(
            session.id,
            MessageRole.USER,
            "Now show me top 5",
            MessageType.USER_MESSAGE
        )
        
        # Get context from history
        context = await manager.get_context_from_history(session.id)
        assert "sales" in context["tables_used"]
        assert context["last_sql_query"] is not None
    
    async def test_error_handling(self, db: AsyncSession, test_user: User):
        """Test error message handling"""
        manager = SessionManager(db)
        
        session = await manager.create_session(user_id=test_user.id)
        
        # Add error message
        await manager.add_message(
            session.id,
            MessageRole.ASSISTANT,
            "Query failed: Invalid SQL",
            MessageType.ERROR,
            sql_query="SELECT * FROM nonexistent",
            error_message="Table 'nonexistent' does not exist",
            error_code="TABLE_NOT_FOUND"
        )
        
        history = await manager.get_session_history(session.id)
        error_msg = history[0]
        
        assert error_msg.message_type == MessageType.ERROR
        assert error_msg.error_message is not None
        assert error_msg.error_code == "TABLE_NOT_FOUND"


@pytest.fixture
async def test_user(db: AsyncSession) -> User:
    """Create test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed",
        role="analyst"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

