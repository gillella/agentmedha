from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from langchain_core.messages import HumanMessage, AIMessage

from agent_medha.graph import create_graph
from agent_medha.services.twitter import get_twitter_service, TwitterService

app = FastAPI(title="agentMedha API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


# ============================================
# Twitter/X API Endpoints
# ============================================

class TweetRequest(BaseModel):
    text: str
    media_ids: Optional[List[str]] = None
    reply_to: Optional[str] = None
    quote_tweet_id: Optional[str] = None

class TweetResponse(BaseModel):
    success: bool
    tweet_id: Optional[str] = None
    error: Optional[str] = None

@app.get("/api/twitter/me")
async def twitter_get_me():
    """Get authenticated Twitter user's profile"""
    try:
        twitter = get_twitter_service()
        result = await twitter.get_me()
        return {"success": True, "data": result.get("data")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/twitter/timeline")
async def twitter_get_timeline(max_results: int = 10, pagination_token: Optional[str] = None):
    """Get user's recent tweets"""
    try:
        twitter = get_twitter_service()
        result = await twitter.get_timeline(max_results=max_results, pagination_token=pagination_token)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/twitter/tweet", response_model=TweetResponse)
async def twitter_post_tweet(request: TweetRequest):
    """Post a new tweet"""
    try:
        twitter = get_twitter_service()
        result = await twitter.post_tweet(
            text=request.text,
            media_ids=request.media_ids,
            reply_to=request.reply_to,
            quote_tweet_id=request.quote_tweet_id
        )
        tweet_data = result.get("data", {})
        return TweetResponse(
            success=True,
            tweet_id=tweet_data.get("id")
        )
    except Exception as e:
        return TweetResponse(success=False, error=str(e))

@app.delete("/api/twitter/tweet/{tweet_id}")
async def twitter_delete_tweet(tweet_id: str):
    """Delete a tweet"""
    try:
        twitter = get_twitter_service()
        deleted = await twitter.delete_tweet(tweet_id)
        return {"success": deleted, "tweet_id": tweet_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/twitter/tweet/{tweet_id}")
async def twitter_get_tweet(tweet_id: str):
    """Get a specific tweet by ID"""
    try:
        twitter = get_twitter_service()
        result = await twitter.get_tweet(tweet_id)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/twitter/media")
async def twitter_upload_media(file: UploadFile = File(...)):
    """Upload media for attachment to tweets"""
    try:
        twitter = get_twitter_service()
        contents = await file.read()
        media_id = await twitter.upload_media(contents, file.content_type or "image/png")
        return {"success": True, "media_id": media_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/twitter/search")
async def twitter_search(query: str, max_results: int = 10):
    """Search for tweets"""
    try:
        twitter = get_twitter_service()
        result = await twitter.search_tweets(query=query, max_results=max_results)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/twitter/metrics")
async def twitter_get_metrics():
    """Get user's profile metrics"""
    try:
        twitter = get_twitter_service()
        result = await twitter.get_user_metrics()
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/twitter/like/{tweet_id}")
async def twitter_like_tweet(tweet_id: str):
    """Like a tweet"""
    try:
        twitter = get_twitter_service()
        liked = await twitter.like_tweet(tweet_id)
        return {"success": liked, "tweet_id": tweet_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/twitter/retweet/{tweet_id}")
async def twitter_retweet(tweet_id: str):
    """Retweet a tweet"""
    try:
        twitter = get_twitter_service()
        retweeted = await twitter.retweet(tweet_id)
        return {"success": retweeted, "tweet_id": tweet_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
