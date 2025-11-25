from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from langchain_core.messages import HumanMessage, AIMessage

from agent_medha.graph import create_graph

app = FastAPI(title="agentMedha API")

# Initialize graph
graph = create_graph()

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
