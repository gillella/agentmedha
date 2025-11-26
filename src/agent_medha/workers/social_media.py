import os
import google.generativeai as genai
from langchain_core.tools import tool
import base64

# Import the post_tweet tool from twitter tools
from agent_medha.tools.twitter import post_tweet

# Configure GenAI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@tool
def generate_image(prompt: str) -> str:
    """
    Generates an image based on the prompt using the Nano Banana Pro model.
    Returns a base64 encoded string of the image.
    """
    try:
        print(f"DEBUG: generate_image called with prompt: {prompt}")
        model = genai.GenerativeModel("models/nano-banana-pro-preview")
        response = model.generate_content(prompt)
        
        if response.parts:
            for part in response.parts:
                if hasattr(part, 'inline_data'):
                    print("DEBUG: Image generated successfully")
                    # Return base64 string directly for frontend to display
                    # inline_data.data is bytes
                    b64_data = base64.b64encode(part.inline_data.data).decode('utf-8')
                    mime_type = part.inline_data.mime_type or "image/png"
                    return f"data:{mime_type};base64,{b64_data}"
        
        print("DEBUG: No image parts in response")
        return "Error: No image generated in response."
    except Exception as e:
        print(f"DEBUG: Error in generate_image: {e}")
        return f"Error generating image: {str(e)}"

@tool
def research_topic(topic: str) -> str:
    """
    Researches a topic to provide context for a social media post.
    Currently uses internal knowledge but simulates a research step.
    """
    # In a real implementation, this would use a Search tool (e.g., Tavily, DuckDuckGo)
    # For now, we'll ask the LLM to simulate research notes
    model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
    prompt = f"Research the following topic for a social media post. Provide 3 key interesting facts or angles: {topic}"
    response = model.generate_content(prompt)
    return response.text

@tool
def draft_post(topic: str, research_notes: str) -> str:
    """
    Drafts a social media post based on the topic and research notes.
    """
    model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
    prompt = f"""
    Draft a viral, engaging Twitter/X post about '{topic}'.
    Use these research notes:
    {research_notes}
    
    Keep it under 280 characters. Include hashtags.
    """
    response = model.generate_content(prompt)
    return response.text

class SocialMediaManager:
    def get_tools(self):
        return [generate_image, research_topic, draft_post, post_tweet]
