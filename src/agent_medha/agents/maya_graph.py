"""
Maya LangGraph Agent

LangGraph-based implementation of Maya for integration with agentMedha supervisor.
Provides structured email handling with memory-powered intelligence.
"""

import os
from typing import Literal, TypedDict, Annotated, List, Optional
import operator

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import create_react_agent

from agent_medha.agents.maya import get_maya, EmailPriority, EmailCategory
from agent_medha.memory.store import get_memory_store
from agent_medha.memory.base import MemoryDomain
from agent_medha.workers.email import (
    list_email_accounts, read_emails, get_email_details, 
    send_email, search_emails
)


class MayaState(TypedDict):
    """State for Maya's graph."""
    messages: Annotated[List[BaseMessage], operator.add]
    next_step: str
    context: dict
    email_context: Optional[dict]
    triaged_emails: Optional[List[dict]]
    draft_response: Optional[str]
    session_id: Optional[str]


# Initialize components
maya = get_maya()
memory_store = get_memory_store()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    google_api_key=os.getenv("GEMINI_API_KEY")
)


# System prompts
MAYA_SYSTEM_PROMPT = """You are Maya, an intelligent email assistant for agentMedha.

Your capabilities:
- Read, search, and manage emails across multiple Gmail accounts
- Triage emails by priority and importance
- Draft professional responses
- Learn user preferences and patterns
- Summarize email content

User preferences and context from memory:
{memory_context}

Current email context:
{email_context}

Be helpful, concise, and proactive in managing the user's inbox."""


def _get_memory_context() -> str:
    """Get relevant context from memory."""
    # Get recent preferences
    preferences = memory_store.get_preferences(domain=MemoryDomain.EMAIL)
    pref_text = "\n".join([f"- {p.content}" for p in preferences[:5]])
    
    # Get recent interactions
    recent = memory_store.recall_recent(agent_id="maya", hours=24, limit=5)
    recent_text = "\n".join([f"- {r.content[:100]}" for r in recent])
    
    return f"""Preferences:
{pref_text}

Recent activity:
{recent_text}"""


# ==================== GRAPH NODES ====================

def understand_intent_node(state: MayaState) -> dict:
    """Understand what the user wants to do with email."""
    messages = state["messages"]
    last_message = messages[-1]
    
    if not isinstance(last_message, HumanMessage):
        return {"next_step": "respond"}
    
    content = last_message.content.lower()
    
    # Intent detection
    if any(kw in content for kw in ["triage", "prioritize", "important", "urgent", "what's urgent"]):
        return {"next_step": "triage"}
    
    if any(kw in content for kw in ["draft", "write", "compose", "reply", "respond to"]):
        return {"next_step": "draft"}
    
    if any(kw in content for kw in ["summarize", "summary", "digest", "overview"]):
        return {"next_step": "summarize"}
    
    if any(kw in content for kw in ["read", "check", "show", "list", "unread"]):
        return {"next_step": "read"}
    
    if any(kw in content for kw in ["search", "find", "look for"]):
        return {"next_step": "search"}
    
    if any(kw in content for kw in ["send", "sending"]):
        return {"next_step": "send"}
    
    # Default to general response
    return {"next_step": "respond"}


def triage_node(state: MayaState) -> dict:
    """Triage inbox and return prioritized results."""
    try:
        triaged = maya.triage_inbox(
            account_id="primary",
            query="is:unread",
            max_results=20,
            deep_analyze_count=5
        )
        
        # Format results
        urgent = [e for e in triaged if e.priority == EmailPriority.URGENT]
        high = [e for e in triaged if e.priority == EmailPriority.HIGH]
        needs_response = [e for e in triaged if e.requires_response]
        
        response = f"""📊 **Inbox Triage Complete**

**Summary:**
- Total unread: {len(triaged)}
- 🔴 Urgent: {len(urgent)}
- 🟠 High Priority: {len(high)}
- ✉️ Needs Response: {len(needs_response)}

"""
        
        if urgent:
            response += "**🔴 Urgent Emails:**\n"
            for e in urgent[:5]:
                response += f"- **{e.subject}** from {e.sender}\n"
                if e.summary:
                    response += f"  {e.summary}\n"
        
        if high:
            response += "\n**🟠 High Priority:**\n"
            for e in high[:5]:
                response += f"- {e.subject} from {e.sender}\n"
        
        if needs_response:
            response += "\n**✉️ Awaiting Your Response:**\n"
            for e in needs_response[:5]:
                response += f"- {e.subject} from {e.sender}\n"
        
        return {
            "messages": [AIMessage(content=response)],
            "triaged_emails": [e.to_dict() for e in triaged],
            "next_step": "done"
        }
    except Exception as e:
        return {
            "messages": [AIMessage(content=f"Error triaging inbox: {str(e)}")],
            "next_step": "done"
        }


def draft_node(state: MayaState) -> dict:
    """Draft a response to an email."""
    messages = state["messages"]
    last_message = messages[-1].content
    
    # Extract email identifier from message
    email_context = state.get("email_context", {})
    
    try:
        # If we have specific email context
        if email_context:
            draft = maya.draft_response(
                email_context,
                tone="professional",
                max_length="medium"
            )
        else:
            # Use LLM to understand what to draft
            prompt = f"""The user wants to draft an email. Based on their request:
"{last_message}"

Generate a helpful email draft. If you need more context, ask clarifying questions."""
            
            response = llm.invoke([HumanMessage(content=prompt)])
            draft = response.content
        
        return {
            "messages": [AIMessage(content=f"📝 **Draft Response:**\n\n{draft}\n\n*Would you like me to modify this draft or send it?*")],
            "draft_response": draft,
            "next_step": "done"
        }
    except Exception as e:
        return {
            "messages": [AIMessage(content=f"Error creating draft: {str(e)}")],
            "next_step": "done"
        }


def summarize_node(state: MayaState) -> dict:
    """Summarize emails or generate daily digest."""
    try:
        digest = maya.daily_digest()
        
        response = f"""📋 **Email Summary**

**Overall Stats:**
- 📬 Total Unread: {digest['total_unread']}
- 🔴 Urgent: {digest['urgent_count']}
- 🟠 High Priority: {digest['high_priority_count']}
- ✉️ Needs Response: {digest['needs_response_count']}
- 📰 Newsletters: {digest['newsletter_count']}

**Summary:**
{digest['summary']}
"""
        
        return {
            "messages": [AIMessage(content=response)],
            "next_step": "done"
        }
    except Exception as e:
        return {
            "messages": [AIMessage(content=f"Error generating summary: {str(e)}")],
            "next_step": "done"
        }


def read_node(state: MayaState) -> dict:
    """Read and display emails."""
    messages = state["messages"]
    last_message = messages[-1].content
    
    # Determine query based on user request
    query = "is:unread"
    if "all" in last_message.lower():
        query = ""
    elif "starred" in last_message.lower():
        query = "is:starred"
    elif "sent" in last_message.lower():
        query = "in:sent"
    
    result = read_emails.invoke({"query": query, "max_results": 10})
    
    return {
        "messages": [AIMessage(content=result)],
        "next_step": "done"
    }


def search_node(state: MayaState) -> dict:
    """Search emails."""
    messages = state["messages"]
    last_message = messages[-1].content
    
    # Extract search query
    # Simple extraction - could be more sophisticated
    search_terms = last_message.lower()
    for prefix in ["search for", "find", "look for", "search"]:
        if prefix in search_terms:
            search_terms = search_terms.split(prefix, 1)[1].strip()
            break
    
    result = search_emails.invoke({"query": search_terms, "max_results": 10})
    
    return {
        "messages": [AIMessage(content=result)],
        "next_step": "done"
    }


def send_node(state: MayaState) -> dict:
    """Handle email sending (with confirmation)."""
    draft = state.get("draft_response")
    
    if draft:
        response = f"""✉️ Ready to send your email.

**Draft:**
{draft[:500]}...

⚠️ Please confirm by saying "send it" or provide more details (recipient, subject)."""
    else:
        response = "To send an email, please provide:\n- Recipient email address\n- Subject\n- Your message\n\nOr ask me to draft a response to a specific email."
    
    return {
        "messages": [AIMessage(content=response)],
        "next_step": "done"
    }


def respond_node(state: MayaState) -> dict:
    """General response using LLM with memory context."""
    messages = state["messages"]
    memory_context = _get_memory_context()
    email_context = state.get("email_context", {})
    
    system_message = MAYA_SYSTEM_PROMPT.format(
        memory_context=memory_context,
        email_context=str(email_context) if email_context else "No specific email context"
    )
    
    all_messages = [SystemMessage(content=system_message)] + messages
    response = llm.invoke(all_messages)
    
    # Save interaction to memory
    if isinstance(messages[-1], HumanMessage):
        memory_store.remember_interaction(
            content=f"User: {messages[-1].content[:200]}",
            agent_id="maya",
            importance=0.5,
            metadata={"type": "user_query"}
        )
    
    return {
        "messages": [response],
        "next_step": "done"
    }


def save_memory_node(state: MayaState) -> dict:
    """Save interaction to memory."""
    messages = state["messages"]
    
    # Find user query and assistant response
    if len(messages) >= 2:
        for i in range(len(messages) - 1, -1, -1):
            if isinstance(messages[i], AIMessage) and i > 0:
                if isinstance(messages[i-1], HumanMessage):
                    memory_store.remember_interaction(
                        content=f"Maya responded to: {messages[i-1].content[:100]}",
                        agent_id="maya",
                        session_id=state.get("session_id"),
                        importance=0.4,
                        metadata={"type": "interaction"}
                    )
                    break
    
    return {}


# ==================== GRAPH CONSTRUCTION ====================

def create_maya_graph():
    """Create Maya's LangGraph workflow."""
    workflow = StateGraph(MayaState)
    
    # Add nodes
    workflow.add_node("understand", understand_intent_node)
    workflow.add_node("triage", triage_node)
    workflow.add_node("draft", draft_node)
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("read", read_node)
    workflow.add_node("search", search_node)
    workflow.add_node("send", send_node)
    workflow.add_node("respond", respond_node)
    workflow.add_node("save_memory", save_memory_node)
    
    # Add edges
    workflow.add_edge(START, "understand")
    
    # Conditional routing based on intent
    workflow.add_conditional_edges(
        "understand",
        lambda x: x["next_step"],
        {
            "triage": "triage",
            "draft": "draft",
            "summarize": "summarize",
            "read": "read",
            "search": "search",
            "send": "send",
            "respond": "respond",
        }
    )
    
    # All paths lead to save_memory then END
    for node in ["triage", "draft", "summarize", "read", "search", "send", "respond"]:
        workflow.add_edge(node, "save_memory")
    
    workflow.add_edge("save_memory", END)
    
    return workflow.compile()


# Create Maya's graph
maya_graph = create_maya_graph()


def invoke_maya(message: str, session_id: str = None, email_context: dict = None) -> str:
    """
    Invoke Maya with a message.
    
    Args:
        message: User's message
        session_id: Optional session identifier
        email_context: Optional email context (for replies, etc.)
        
    Returns:
        Maya's response
    """
    initial_state = {
        "messages": [HumanMessage(content=message)],
        "next_step": "",
        "context": {},
        "email_context": email_context,
        "triaged_emails": None,
        "draft_response": None,
        "session_id": session_id,
    }
    
    result = maya_graph.invoke(initial_state)
    
    # Extract final response
    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage):
            return msg.content
    
    return "I couldn't process that request. Could you try again?"

