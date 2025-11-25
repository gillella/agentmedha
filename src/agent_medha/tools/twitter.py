import os
import tweepy
from langchain_core.tools import tool

class TwitterTools:
    def __init__(self):
        self.api_key = os.getenv("TWITTER_API_KEY")
        self.api_secret = os.getenv("TWITTER_API_SECRET")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        
        self.client = None
        if self.api_key and self.api_secret and self.access_token and self.access_token_secret:
            try:
                self.client = tweepy.Client(
                    consumer_key=self.api_key,
                    consumer_secret=self.api_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_token_secret
                )
                print("Twitter Client Initialized Successfully")
            except Exception as e:
                print(f"Error initializing Twitter Client: {e}")
        else:
            print("Twitter Credentials missing. Running in MOCK MODE.")

    def post_tweet(self, text: str) -> str:
        """
        Posts a tweet to X (Twitter).
        
        Args:
            text: The content of the tweet.
            
        Returns:
            A success message or error description.
        """
        if self.client:
            try:
                response = self.client.create_tweet(text=text)
                return f"Successfully posted to X: {text} (ID: {response.data['id']})"
            except Exception as e:
                return f"Error posting to X: {str(e)}"
        else:
            # Mock Mode
            print(f"\n[MOCK TWITTER] Posting tweet: {text}\n")
            return f"Successfully posted to X (MOCK): {text}"

# Initialize global instance
twitter_tools_instance = TwitterTools()

@tool
def post_tweet(text: str) -> str:
    """
    Posts a tweet to X (Twitter). Use this tool when the user asks to post something to social media or X.
    """
    return twitter_tools_instance.post_tweet(text)
