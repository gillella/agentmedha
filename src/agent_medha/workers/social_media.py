import os
import google.generativeai as genai
from langchain_core.tools import tool
import base64

import tweepy

# Configure GenAI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Configure Twitter
twitter_client = None
try:
    twitter_client = tweepy.Client(
        consumer_key=os.getenv("TWITTER_API_KEY"),
        consumer_secret=os.getenv("TWITTER_API_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    )
    print("DEBUG: Twitter Client Initialized")
except Exception as e:
    print(f"WARNING: Failed to initialize Twitter Client: {e}")

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
def draft_post(topic: str, research_notes: str, platform: str = "twitter") -> str:
    """
    Drafts a social media post based on the topic and research notes.
    Platform can be 'twitter', 'linkedin', or 'instagram'.
    """
    model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
    
    platform_instructions = {
        "twitter": "Keep it under 280 characters. Include hashtags. Focus on punchy, viral content.",
        "linkedin": "Professional tone. Can be longer (up to 3000 chars). Focus on industry insights and professional value. Use bullet points if needed.",
        "instagram": "Visual-first caption. Engaging and personal. Use many relevant hashtags. Include a 'Link in bio' call to action if relevant."
    }
    
    instruction = platform_instructions.get(platform.lower(), platform_instructions["twitter"])
    
    prompt = f"""
    Draft a engaging {platform} post about '{topic}'.
    Use these research notes:
    {research_notes}
    
    Platform Instructions:
    {instruction}
    """
    response = model.generate_content(prompt)
    return response.text

@tool
def post_tweet(content: str) -> str:
    """
    Posts a tweet to Twitter/X.
    """
    if not twitter_client:
        return "Error: Twitter client not initialized. Check credentials."
    
    try:
        print(f"DEBUG: Posting tweet: {content}")
        response = twitter_client.create_tweet(text=content)
        return f"Tweet posted successfully! ID: {response.data['id']}"
    except Exception as e:
        print(f"DEBUG: Error posting tweet: {e}")
        return f"Error posting tweet: {str(e)}"

@tool
def post_linkedin(content: str) -> str:
    """
    Posts a message to LinkedIn.
    """
    # Mock implementation
    print(f"DEBUG: Mock Posting to LinkedIn: {content}")
    return "Successfully posted to LinkedIn (Mocked)"

@tool
def post_instagram(content: str, image_url: str = None) -> str:
    """
    Posts a message and optional image to Instagram.
    """
    # Mock implementation
    print(f"DEBUG: Mock Posting to Instagram: {content} | Image: {image_url}")
    return "Successfully posted to Instagram (Mocked)"

@tool
def generate_video(prompt: str) -> str:
    """
    Generates a video based on the prompt using the Veo3 model.
    Returns a URL to the generated video.
    """
    # Mock implementation for Veo3
    print(f"DEBUG: generate_video called with prompt: {prompt}")
    # Return a placeholder video URL or a message indicating it's a mock
    return "https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"

class SocialMediaManager:
    def get_tools(self):
        return [generate_image, research_topic, draft_post, post_tweet, post_linkedin, post_instagram, generate_video]
