"""
Session Manager Service

Manages conversation sessions and messages.
Provides session lifecycle management, context tracking, and persistence.
"""
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import structlog

from app.models.session import (
    ConversationSession,
    ConversationMessage,
    SessionStatus,
    MessageRole,
    MessageType
)
from app.models.user import User
from app.services.cache import cache

logger = structlog.get_logger(__name__)


class SessionManager:
    """
    Manages conversation sessions and messages.
    
    Features:
    - Create and manage sessions
    - Add messages to sessions
    - Track session context and state
    - Session expiration and cleanup
    - Redis caching for active sessions
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cache_ttl = 3600  # 1 hour cache
    
    async def create_session(
        self,
        user_id: int,
        title: Optional[str] = None,
        data_source_id: Optional[int] = None,
        expires_in_hours: int = 24
    ) -> ConversationSession:
        """
        Create a new conversation session.
        
        Args:
            user_id: User ID
            title: Optional session title
            data_source_id: Optional data source ID
            expires_in_hours: Session expiration time in hours
            
        Returns:
            Created session
        """
        session = ConversationSession(
            user_id=user_id,
            title=title,
            data_source_id=data_source_id,
            status=SessionStatus.ACTIVE,
            context={},
            metadata={},
            started_at=datetime.utcnow(),
            last_activity_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours)
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        # Cache the session
        await self._cache_session(session)
        
        logger.info(
            "session.created",
            session_id=session.id,
            user_id=user_id,
            data_source_id=data_source_id
        )
        
        return session
    
    async def get_session(
        self,
        session_id: int,
        user_id: Optional[int] = None,
        load_messages: bool = True
    ) -> Optional[ConversationSession]:
        """
        Get session by ID.
        
        Args:
            session_id: Session ID
            user_id: Optional user ID for access control
            load_messages: Whether to load messages
            
        Returns:
            Session or None
        """
        # Try cache first
        cache_key = f"session:v1:{session_id}"
        cached = await cache.get(cache_key)
        
        if cached and not load_messages:
            return cached
        
        # Load from database
        query = select(ConversationSession).where(
            ConversationSession.id == session_id
        )
        
        if user_id:
            query = query.where(ConversationSession.user_id == user_id)
        
        if load_messages:
            query = query.options(selectinload(ConversationSession.messages))
        
        result = await self.db.execute(query)
        session = result.scalar_one_or_none()
        
        if session:
            # Check if expired
            if session.is_expired and session.status == SessionStatus.ACTIVE:
                session.status = SessionStatus.EXPIRED
                await self.db.commit()
                await self.db.refresh(session)
            
            # Update cache
            await self._cache_session(session)
        
        return session
    
    async def get_user_sessions(
        self,
        user_id: int,
        status: Optional[SessionStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ConversationSession]:
        """
        Get user's sessions.
        
        Args:
            user_id: User ID
            status: Optional status filter
            limit: Max sessions to return
            offset: Pagination offset
            
        Returns:
            List of sessions
        """
        query = select(ConversationSession).where(
            ConversationSession.user_id == user_id
        )
        
        if status:
            query = query.where(ConversationSession.status == status)
        
        query = query.order_by(ConversationSession.last_activity_at.desc())
        query = query.limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        sessions = result.scalars().all()
        
        return list(sessions)
    
    async def add_message(
        self,
        session_id: int,
        role: MessageRole,
        content: str,
        message_type: MessageType = MessageType.USER_MESSAGE,
        sql_query: Optional[str] = None,
        sql_explanation: Optional[str] = None,
        results: Optional[List[Dict[str, Any]]] = None,
        visualization_config: Optional[Dict[str, Any]] = None,
        context_stats: Optional[Dict[str, Any]] = None,
        suggested_actions: Optional[List[str]] = None,
        error_message: Optional[str] = None,
        error_code: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConversationMessage:
        """
        Add message to session.
        
        Args:
            session_id: Session ID
            role: Message role (user/assistant/system)
            content: Message content
            message_type: Type of message
            sql_query: Optional SQL query
            sql_explanation: Optional SQL explanation
            results: Optional query results
            visualization_config: Optional viz config
            context_stats: Optional context stats
            suggested_actions: Optional follow-up suggestions
            error_message: Optional error message
            error_code: Optional error code
            metadata: Optional metadata
            
        Returns:
            Created message
        """
        message = ConversationMessage(
            session_id=session_id,
            role=role,
            message_type=message_type,
            content=content,
            sql_query=sql_query,
            sql_explanation=sql_explanation,
            results=results[:100] if results else None,  # Limit stored results
            result_count=len(results) if results else None,
            visualization_config=visualization_config,
            context_stats=context_stats,
            suggested_actions=suggested_actions,
            error_message=error_message,
            error_code=error_code,
            metadata=metadata or {},
            created_at=datetime.utcnow()
        )
        
        self.db.add(message)
        
        # Update session last activity
        session = await self.get_session(session_id, load_messages=False)
        if session:
            session.last_activity_at = datetime.utcnow()
            
            # Auto-generate title from first user message
            if not session.title and role == MessageRole.USER and len(content) > 0:
                session.title = content[:100] + ("..." if len(content) > 100 else "")
        
        await self.db.commit()
        await self.db.refresh(message)
        
        # Invalidate session cache
        await self._invalidate_session_cache(session_id)
        
        logger.info(
            "message.added",
            session_id=session_id,
            message_id=message.id,
            role=role.value,
            type=message_type.value
        )
        
        return message
    
    async def update_session_context(
        self,
        session_id: int,
        context_updates: Dict[str, Any]
    ) -> bool:
        """
        Update session context.
        
        Args:
            session_id: Session ID
            context_updates: Context updates
            
        Returns:
            Success status
        """
        session = await self.get_session(session_id, load_messages=False)
        if not session:
            return False
        
        session.update_context(context_updates)
        session.last_activity_at = datetime.utcnow()
        
        await self.db.commit()
        await self._invalidate_session_cache(session_id)
        
        logger.info(
            "session.context_updated",
            session_id=session_id,
            updates=list(context_updates.keys())
        )
        
        return True
    
    async def set_data_source(
        self,
        session_id: int,
        data_source_id: int
    ) -> bool:
        """
        Set data source for session.
        
        Args:
            session_id: Session ID
            data_source_id: Data source ID
            
        Returns:
            Success status
        """
        session = await self.get_session(session_id, load_messages=False)
        if not session:
            return False
        
        session.data_source_id = data_source_id
        session.last_activity_at = datetime.utcnow()
        
        await self.db.commit()
        await self._invalidate_session_cache(session_id)
        
        logger.info(
            "session.data_source_set",
            session_id=session_id,
            data_source_id=data_source_id
        )
        
        return True
    
    async def end_session(
        self,
        session_id: int,
        status: SessionStatus = SessionStatus.COMPLETED
    ) -> bool:
        """
        End a session.
        
        Args:
            session_id: Session ID
            status: Final status
            
        Returns:
            Success status
        """
        session = await self.get_session(session_id, load_messages=False)
        if not session:
            return False
        
        session.status = status
        session.ended_at = datetime.utcnow()
        
        await self.db.commit()
        await self._invalidate_session_cache(session_id)
        
        logger.info(
            "session.ended",
            session_id=session_id,
            status=status.value,
            duration_seconds=session.duration_seconds
        )
        
        return True
    
    async def get_session_history(
        self,
        session_id: int,
        limit: Optional[int] = None
    ) -> List[ConversationMessage]:
        """
        Get session message history.
        
        Args:
            session_id: Session ID
            limit: Optional limit on messages
            
        Returns:
            List of messages
        """
        query = select(ConversationMessage).where(
            ConversationMessage.session_id == session_id
        ).order_by(ConversationMessage.created_at.asc())
        
        if limit:
            query = query.limit(limit)
        
        result = await self.db.execute(query)
        messages = result.scalars().all()
        
        return list(messages)
    
    async def get_context_from_history(
        self,
        session_id: int,
        last_n_messages: int = 5
    ) -> Dict[str, Any]:
        """
        Extract context from recent message history.
        
        Args:
            session_id: Session ID
            last_n_messages: Number of recent messages to analyze
            
        Returns:
            Context dict with tables, columns, filters, etc.
        """
        messages = await self.get_session_history(session_id, limit=last_n_messages)
        
        context = {
            "tables_used": set(),
            "columns_referenced": set(),
            "filters_applied": [],
            "last_sql_query": None,
            "conversation_summary": []
        }
        
        for msg in messages:
            # Extract from SQL queries
            if msg.sql_query:
                context["last_sql_query"] = msg.sql_query
                # Simple extraction (could be enhanced with SQL parsing)
                sql_lower = msg.sql_query.lower()
                if "from" in sql_lower:
                    # Extract table names (basic approach)
                    parts = sql_lower.split("from")[1].split("where")[0].split("join")
                    for part in parts:
                        table = part.strip().split()[0].strip()
                        if table:
                            context["tables_used"].add(table)
            
            # Add to conversation summary
            context["conversation_summary"].append({
                "role": msg.role.value,
                "content": msg.content[:200],  # Truncate
                "type": msg.message_type.value
            })
        
        # Convert sets to lists for JSON serialization
        context["tables_used"] = list(context["tables_used"])
        context["columns_referenced"] = list(context["columns_referenced"])
        
        return context
    
    async def cleanup_expired_sessions(self, batch_size: int = 100) -> int:
        """
        Clean up expired sessions.
        
        Args:
            batch_size: Number of sessions to clean per batch
            
        Returns:
            Number of sessions cleaned
        """
        query = select(ConversationSession).where(
            and_(
                ConversationSession.expires_at <= datetime.utcnow(),
                ConversationSession.status == SessionStatus.ACTIVE
            )
        ).limit(batch_size)
        
        result = await self.db.execute(query)
        expired_sessions = result.scalars().all()
        
        count = 0
        for session in expired_sessions:
            session.status = SessionStatus.EXPIRED
            session.ended_at = datetime.utcnow()
            count += 1
        
        if count > 0:
            await self.db.commit()
            logger.info("sessions.cleaned_up", count=count)
        
        return count
    
    # Cache helpers
    
    async def _cache_session(self, session: ConversationSession) -> None:
        """Cache session in Redis"""
        cache_key = f"session:v1:{session.id}"
        await cache.set(cache_key, session, ttl=self.cache_ttl)
    
    async def _invalidate_session_cache(self, session_id: int) -> None:
        """Invalidate session cache"""
        cache_key = f"session:v1:{session_id}"
        await cache.delete(cache_key)


def get_session_manager(db: AsyncSession) -> SessionManager:
    """Factory function to create SessionManager"""
    return SessionManager(db)

