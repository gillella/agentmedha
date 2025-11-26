import os
from typing import Literal

# Force removal of ADC if present to avoid conflicts
if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
    del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import create_react_agent

from agent_medha.state import AgentState
from agent_medha.memory_manager import MemoryManager

# Initialize Memory
memory = MemoryManager()

from agent_medha.workers.social_media import SocialMediaManager

# Initialize Workers
social_manager = SocialMediaManager()
social_tools = social_manager.get_tools()

# Create Social Media Agent Node
# We use a ReAct agent for the worker to allow it to use tools autonomously
social_agent = create_react_agent(
    model=ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", google_api_key=os.getenv("GEMINI_API_KEY")),
    tools=social_tools
)

def social_media_node(state: AgentState):
    """
    Executes the social media worker agent.
    """
    # We need to pass the last message to the worker
    result = social_agent.invoke(state)
    # The result from create_react_agent is the final state, we want to return the messages
    return {"messages": result["messages"]}

# --- Memory Retrieval Node ---
def retrieve_node(state: AgentState):
    """Retrieves relevant context from memory."""
    messages = state["messages"]
    last_message = messages[-1]
    
    if isinstance(last_message, HumanMessage):
        query = last_message.content
        # Search for relevant episodic and semantic memories
        # We search broadly for now, but scoped to 'supervisor' or 'global'
        context_docs = memory.search_memory(
            query, 
            agent_id="supervisor",
            limit=5
        )
        return {"context": context_docs}
    
    return {"context": []}

# --- Supervisor Node ---
def supervisor_node(state: AgentState):
    """
    The supervisor node decides which worker to call next or if the task is finished.
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    if isinstance(last_message, HumanMessage):
        content = last_message.content.lower()
        
        # Routing Logic
        if "post" in content or "tweet" in content or "twitter" in content or " x " in content or "draft" in content or "research" in content:
            return {"next_step": "social_media"}
            
        if "bye" in content:
            return {"next_step": "FINISH"}
    
    return {"next_step": "respond"}

# --- Response Node ---
def response_node(state: AgentState):
    """
    Generates a response using the Gemini model, augmented with context.
    """
    context = state.get("context", [])
    context_str = "\n".join([f"- {doc.page_content}" for doc in context])
    
    system_prompt = "You are agentMedha, a helpful personal assistant."
    if context_str:
        system_prompt += f"\n\nHere is some relevant context from your memory:\n{context_str}"
    
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    response = model.invoke(messages)
    return {"messages": [response]}

# --- Memory Save Node ---
def save_node(state: AgentState):
    """Saves the latest interaction to memory."""
    messages = state["messages"]
    # We expect the last two messages to be User -> Agent
    if len(messages) >= 2:
        last_msg = messages[-1]
        second_last_msg = messages[-2]
        
        if isinstance(second_last_msg, HumanMessage):
            # Save the user's input as Episodic Memory
            memory.add_memory(
                second_last_msg.content, 
                memory_type="episodic",
                agent_id="supervisor",
                metadata={"role": "user"}
            )
            
    return {}

# --- Graph Construction ---
def create_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("responder", response_node)
    workflow.add_node("social_media", social_media_node)
    workflow.add_node("save", save_node)

    # Start -> Retrieve -> Supervisor
    workflow.add_edge(START, "retrieve")
    workflow.add_edge("retrieve", "supervisor")
    
    # Conditional edge based on supervisor's decision
    workflow.add_conditional_edges(
        "supervisor",
        lambda x: x["next_step"],
        {
            "respond": "responder",
            "social_media": "social_media",
            "FINISH": END
        }
    )
    
    # Responder -> Save -> End
    workflow.add_edge("responder", "save")
    
    # Social Media -> Save -> End
    workflow.add_edge("social_media", "save")
    
    workflow.add_edge("save", END)

    return workflow.compile()
