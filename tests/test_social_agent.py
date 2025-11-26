import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from agent_medha.workers.social_media import SocialMediaWorker
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def test_social_agent():
    print("Initializing Worker...")
    worker = SocialMediaWorker()
    tools = worker.get_tools()
    print(f"Tools: {[t.name for t in tools]}")
    
    print("Initializing Agent...")
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", google_api_key=os.getenv("GEMINI_API_KEY"))
    agent = create_react_agent(model, tools)
    
    print("Invoking Agent with Draft Request...")
    response = agent.invoke({"messages": [HumanMessage(content="Research and draft a tweet about Cyberpunk City")]})
    print("Response Messages:")
    for m in response["messages"]:
        print(f"{m.type}: {m.content}")
        
    print("\nInvoking Agent with Image Request...")
    response = agent.invoke({"messages": [HumanMessage(content="Generate an image for a tweet about Cyberpunk City")]})
    print("Response Messages:")
    for m in response["messages"]:
        print(f"{m.type}: {m.content}")

if __name__ == "__main__":
    test_social_agent()
