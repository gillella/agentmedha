from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from langchain_core.messages import HumanMessage, AIMessage

from agent_medha.graph import create_graph
from agent_medha.agents.maya import get_maya, EmailPriority
from agent_medha.agents.maya_graph import invoke_maya
from agent_medha.agents.email_pipeline import (
    get_email_pipeline, start_email_pipeline, stop_email_pipeline,
    PipelineConfig
)
from agent_medha.memory.store import get_memory_store

app = FastAPI(title="agentMedha API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
graph = create_graph()
maya = get_maya()
memory_store = get_memory_store()

class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str
    thread_id: str

class ConfigRequest(BaseModel):
    model_name: str
    api_keys: Dict[str, str]

@app.get("/")
async def root():
    return {"status": "ok", "message": "agentMedha is online"}

# from langfuse.decorators import observe, langfuse_context

# ... (imports)

@app.post("/chat", response_model=ChatResponse)
# @observe()
async def chat(request: ChatRequest):
    try:
        # For now, we are not using persistent checkpointers, so thread_id is just a placeholder
        # In the future, we will pass config={"configurable": {"thread_id": request.thread_id}}
        
        initial_state = {"messages": [HumanMessage(content=request.message)]}
        
        # Run the graph
        # We want to get the final response. 
        # Since our graph is simple (Supervisor -> Responder -> End), we can just invoke it.
        final_state = graph.invoke(initial_state)
        
        messages = final_state.get("messages", [])
        if not messages:
            return ChatResponse(response="No response generated.", thread_id=request.thread_id)
            
        last_msg = messages[-1]
        response_text = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
        
        return ChatResponse(response=response_text, thread_id=request.thread_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/config")
async def update_config(request: ConfigRequest):
    # This is a placeholder for updating configuration
    # In a real app, we might store this in a database or update env vars for the session
    print(f"Updating config: Model={request.model_name}")
    return {"status": "updated", "model": request.model_name}


# ==================== MAYA ENDPOINTS ====================

class MayaChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    email_context: Optional[Dict[str, Any]] = None


class MayaChatResponse(BaseModel):
    response: str
    session_id: Optional[str] = None


class TriageRequest(BaseModel):
    account_id: str = "primary"
    query: str = "is:unread"
    max_results: int = 50


class DraftRequest(BaseModel):
    email: Dict[str, Any]
    tone: str = "professional"
    max_length: str = "medium"
    additional_context: Optional[str] = None


class LearnPatternRequest(BaseModel):
    pattern_name: str
    trigger_description: str
    trigger_keywords: List[str]
    response_template: str
    conditions: Optional[Dict[str, Any]] = None


class MarkVIPRequest(BaseModel):
    email: str
    is_vip: bool = True
    reason: Optional[str] = None


class PipelineConfigRequest(BaseModel):
    check_interval_minutes: int = 15
    auto_draft_urgent: bool = True
    notify_urgent: bool = True
    enabled_accounts: List[str] = ["primary"]


@app.post("/api/maya/chat", response_model=MayaChatResponse)
async def maya_chat(request: MayaChatRequest):
    """Chat with Maya - your intelligent email assistant."""
    try:
        response = invoke_maya(
            message=request.message,
            session_id=request.session_id,
            email_context=request.email_context
        )
        return MayaChatResponse(response=response, session_id=request.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/maya/triage")
async def triage_inbox(request: TriageRequest):
    """Triage inbox and return prioritized emails."""
    try:
        triaged = maya.triage_inbox(
            account_id=request.account_id,
            query=request.query,
            max_results=request.max_results
        )
        
        return {
            "total": len(triaged),
            "urgent": len([e for e in triaged if e.priority == EmailPriority.URGENT]),
            "high": len([e for e in triaged if e.priority == EmailPriority.HIGH]),
            "needs_response": len([e for e in triaged if e.requires_response]),
            "emails": [e.to_dict() for e in triaged]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/maya/digest")
async def get_digest(account_id: str = "primary"):
    """Get daily email digest."""
    try:
        digest = maya.daily_digest(account_id)
        return digest
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/maya/draft")
async def draft_response(request: DraftRequest):
    """Draft a response to an email."""
    try:
        draft = maya.draft_response(
            email=request.email,
            tone=request.tone,
            max_length=request.max_length,
            additional_context=request.additional_context
        )
        return {"draft": draft}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/maya/summarize")
async def summarize_emails(emails: List[Dict[str, Any]], format: str = "bullet"):
    """Summarize a list of emails."""
    try:
        summary = maya.summarize_emails(emails, format=format)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== LEARNING ENDPOINTS ====================

@app.post("/api/maya/learn/pattern")
async def learn_pattern(request: LearnPatternRequest):
    """Teach Maya a new email response pattern."""
    try:
        pattern_id = maya.learn_response_pattern(
            pattern_name=request.pattern_name,
            trigger_description=request.trigger_description,
            trigger_keywords=request.trigger_keywords,
            response_template=request.response_template,
            conditions=request.conditions
        )
        return {"status": "learned", "pattern_id": pattern_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/maya/learn/vip")
async def mark_vip(request: MarkVIPRequest):
    """Mark a contact as VIP."""
    try:
        success = maya.mark_vip(
            email=request.email,
            is_vip=request.is_vip,
            reason=request.reason
        )
        return {"status": "updated" if success else "failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/maya/learn/preference")
async def learn_preference(preference: str, category: str = "general"):
    """Teach Maya a new preference."""
    try:
        pref_id = memory_store.learn_preference(
            preference=preference,
            category=category,
            agent_id="maya"
        )
        return {"status": "learned", "preference_id": pref_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/maya/patterns")
async def get_patterns():
    """Get all learned email patterns."""
    try:
        patterns = maya.memory.get_email_patterns()
        return {
            "patterns": [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "trigger_keywords": p.trigger_keywords,
                    "confidence": p.confidence,
                    "success_rate": p.success_rate,
                }
                for p in patterns
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== PIPELINE ENDPOINTS ====================

@app.post("/api/maya/pipeline/start")
async def start_pipeline(config: Optional[PipelineConfigRequest] = None):
    """Start the email processing pipeline."""
    try:
        pipeline_config = None
        if config:
            pipeline_config = PipelineConfig(
                check_interval_minutes=config.check_interval_minutes,
                auto_draft_urgent=config.auto_draft_urgent,
                notify_urgent=config.notify_urgent,
                enabled_accounts=config.enabled_accounts,
            )
        pipeline = start_email_pipeline(pipeline_config)
        return {"status": "started", "config": pipeline.config.__dict__}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/maya/pipeline/stop")
async def stop_pipeline():
    """Stop the email processing pipeline."""
    try:
        stop_email_pipeline()
        return {"status": "stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/maya/pipeline/status")
async def pipeline_status():
    """Get pipeline status and stats."""
    try:
        pipeline = get_email_pipeline()
        return pipeline.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/maya/inbox/health")
async def inbox_health():
    """Get inbox health metrics."""
    try:
        pipeline = get_email_pipeline()
        return pipeline.get_inbox_health()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== MEMORY ENDPOINTS ====================

@app.get("/api/memory/stats")
async def memory_stats():
    """Get memory system statistics."""
    try:
        return memory_store.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/memory/preferences")
async def get_preferences(domain: Optional[str] = None, category: Optional[str] = None):
    """Get stored preferences."""
    try:
        from agent_medha.memory.base import MemoryDomain
        domain_enum = MemoryDomain(domain) if domain else None
        prefs = memory_store.get_preferences(domain=domain_enum, category=category)
        return {
            "preferences": [
                {"content": p.content, "category": p.metadata.get("category")}
                for p in prefs
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
