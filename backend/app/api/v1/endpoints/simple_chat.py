"""
Simple Chat Endpoint
Just OpenAI integration without data sources or complex agents.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
import structlog
from openai import OpenAI
from app.core.config import settings

logger = structlog.get_logger()

router = APIRouter()

# Initialize OpenAI client
client = OpenAI(api_key=settings.openai_api_key)


class Message(BaseModel):
    """Chat message"""
    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat request"""
    message: str = Field(..., description="User message")
    conversation_history: List[Message] = Field(default=[], description="Previous messages")


class ChatResponse(BaseModel):
    """Chat response"""
    response: str = Field(..., description="AI response")
    model: str = Field(..., description="Model used")
    tokens_used: Optional[int] = Field(None, description="Tokens used in this request")


@router.post("/chat", response_model=ChatResponse)
async def simple_chat(request: ChatRequest):
    """
    Simple chat endpoint - just talks to OpenAI.
    
    No data sources, no agents, no complexity.
    Just a friendly AI assistant.
    """
    try:
        logger.info("simple_chat.request", message=request.message[:100])
        
        # Build messages for OpenAI
        messages = [
            {
                "role": "system",
                "content": "You are AgentMedha, a helpful AI assistant. Be friendly, concise, and helpful."
            }
        ]
        
        # Add conversation history
        for msg in request.conversation_history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": request.message
        })
        
        # Call OpenAI
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        # Extract response
        assistant_message = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else None
        
        logger.info(
            "simple_chat.success",
            response_length=len(assistant_message),
            tokens_used=tokens_used
        )
        
        return ChatResponse(
            response=assistant_message,
            model=response.model,
            tokens_used=tokens_used
        )
        
    except Exception as e:
        logger.error("simple_chat.error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat error: {str(e)}"
        )


@router.get("/health")
async def chat_health():
    """Check if OpenAI is configured"""
    has_api_key = bool(settings.openai_api_key and settings.openai_api_key != "your-openai-api-key-here")
    
    return {
        "status": "healthy" if has_api_key else "not_configured",
        "openai_configured": has_api_key,
        "model": settings.openai_model
    }

