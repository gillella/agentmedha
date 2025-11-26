"""
Twitter/X API Service for agentMedha Social Media Manager

Uses Twitter API v2 with OAuth 1.0a for posting and OAuth 2.0 for reading.
"""

import os
import json
import httpx
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass
import base64
import hashlib
import hmac
import time
import urllib.parse
import secrets


@dataclass
class TwitterCredentials:
    """Twitter API credentials"""
    api_key: str
    api_secret: str
    access_token: str
    access_token_secret: str
    bearer_token: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> "TwitterCredentials":
        """Load credentials from environment variables"""
        return cls(
            api_key=os.getenv("TWITTER_API_KEY", ""),
            api_secret=os.getenv("TWITTER_API_SECRET", ""),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN", ""),
            access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET", ""),
            bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
        )


@dataclass
class Tweet:
    """Tweet data model"""
    id: str
    text: str
    author_id: str
    created_at: str
    public_metrics: Optional[Dict[str, int]] = None
    media: Optional[List[Dict]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "author_id": self.author_id,
            "created_at": self.created_at,
            "metrics": self.public_metrics,
            "media": self.media
        }


class TwitterService:
    """
    Twitter API Service
    
    Handles authentication and API calls for:
    - Posting tweets (with/without media)
    - Reading tweets and timeline
    - User profile info
    - Analytics/metrics
    """
    
    BASE_URL = "https://api.twitter.com"
    API_V2 = f"{BASE_URL}/2"
    UPLOAD_URL = "https://upload.twitter.com/1.1"
    
    def __init__(self, credentials: Optional[TwitterCredentials] = None):
        self.credentials = credentials or TwitterCredentials.from_env()
        self._validate_credentials()
        
    def _validate_credentials(self):
        """Validate that required credentials are present"""
        if not self.credentials.api_key or not self.credentials.api_secret:
            raise ValueError("Twitter API key and secret are required")
        if not self.credentials.access_token or not self.credentials.access_token_secret:
            raise ValueError("Twitter access token and secret are required")
    
    def _generate_oauth_signature(
        self, 
        method: str, 
        url: str, 
        params: Dict[str, str],
        oauth_params: Dict[str, str]
    ) -> str:
        """Generate OAuth 1.0a signature"""
        # Combine all parameters
        all_params = {**params, **oauth_params}
        
        # Sort and encode parameters
        sorted_params = sorted(all_params.items())
        param_string = "&".join(
            f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(str(v), safe='')}"
            for k, v in sorted_params
        )
        
        # Create signature base string
        base_string = "&".join([
            method.upper(),
            urllib.parse.quote(url, safe=""),
            urllib.parse.quote(param_string, safe="")
        ])
        
        # Create signing key
        signing_key = "&".join([
            urllib.parse.quote(self.credentials.api_secret, safe=""),
            urllib.parse.quote(self.credentials.access_token_secret, safe="")
        ])
        
        # Generate signature
        signature = hmac.new(
            signing_key.encode(),
            base_string.encode(),
            hashlib.sha1
        ).digest()
        
        return base64.b64encode(signature).decode()
    
    def _get_oauth_header(
        self, 
        method: str, 
        url: str, 
        params: Optional[Dict[str, str]] = None
    ) -> str:
        """Generate OAuth 1.0a Authorization header"""
        params = params or {}
        
        oauth_params = {
            "oauth_consumer_key": self.credentials.api_key,
            "oauth_token": self.credentials.access_token,
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_nonce": secrets.token_hex(16),
            "oauth_version": "1.0"
        }
        
        # Generate signature
        oauth_params["oauth_signature"] = self._generate_oauth_signature(
            method, url, params, oauth_params
        )
        
        # Build Authorization header
        oauth_header = "OAuth " + ", ".join(
            f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(v, safe="")}"'
            for k, v in sorted(oauth_params.items())
        )
        
        return oauth_header
    
    async def get_me(self) -> Dict[str, Any]:
        """Get authenticated user's profile"""
        url = f"{self.API_V2}/users/me"
        params = {"user.fields": "id,name,username,profile_image_url,description,public_metrics"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers={"Authorization": self._get_oauth_header("GET", url, params)}
            )
            response.raise_for_status()
            return response.json()
    
    async def post_tweet(
        self, 
        text: str, 
        media_ids: Optional[List[str]] = None,
        reply_to: Optional[str] = None,
        quote_tweet_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Post a new tweet
        
        Args:
            text: Tweet text (max 280 chars)
            media_ids: List of media IDs to attach
            reply_to: Tweet ID to reply to
            quote_tweet_id: Tweet ID to quote
            
        Returns:
            Created tweet data
        """
        url = f"{self.API_V2}/tweets"
        
        payload: Dict[str, Any] = {"text": text}
        
        if media_ids:
            payload["media"] = {"media_ids": media_ids}
            
        if reply_to:
            payload["reply"] = {"in_reply_to_tweet_id": reply_to}
            
        if quote_tweet_id:
            payload["quote_tweet_id"] = quote_tweet_id
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers={
                    "Authorization": self._get_oauth_header("POST", url),
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def delete_tweet(self, tweet_id: str) -> bool:
        """Delete a tweet"""
        url = f"{self.API_V2}/tweets/{tweet_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                url,
                headers={"Authorization": self._get_oauth_header("DELETE", url)}
            )
            response.raise_for_status()
            return response.json().get("data", {}).get("deleted", False)
    
    async def get_timeline(
        self, 
        max_results: int = 10,
        pagination_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get user's home timeline"""
        # First get user ID
        me = await self.get_me()
        user_id = me["data"]["id"]
        
        url = f"{self.API_V2}/users/{user_id}/tweets"
        params = {
            "max_results": str(max_results),
            "tweet.fields": "created_at,public_metrics,attachments",
            "expansions": "attachments.media_keys",
            "media.fields": "url,preview_image_url,type"
        }
        
        if pagination_token:
            params["pagination_token"] = pagination_token
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers={"Authorization": self._get_oauth_header("GET", url, params)}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """Get a specific tweet by ID"""
        url = f"{self.API_V2}/tweets/{tweet_id}"
        params = {
            "tweet.fields": "created_at,public_metrics,attachments,author_id",
            "expansions": "attachments.media_keys,author_id",
            "media.fields": "url,preview_image_url,type",
            "user.fields": "name,username,profile_image_url"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers={"Authorization": self._get_oauth_header("GET", url, params)}
            )
            response.raise_for_status()
            return response.json()
    
    async def upload_media(self, media_data: bytes, media_type: str = "image/png") -> str:
        """
        Upload media for attachment to tweets
        
        Args:
            media_data: Raw bytes of the media file
            media_type: MIME type of the media
            
        Returns:
            media_id string to use in tweet
        """
        url = f"{self.UPLOAD_URL}/media/upload.json"
        
        # For images, use simple upload
        # For videos/gifs, chunked upload is needed (not implemented here)
        media_base64 = base64.b64encode(media_data).decode()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                data={"media_data": media_base64},
                headers={"Authorization": self._get_oauth_header("POST", url)}
            )
            response.raise_for_status()
            return response.json()["media_id_string"]
    
    async def search_tweets(
        self, 
        query: str, 
        max_results: int = 10
    ) -> Dict[str, Any]:
        """Search for tweets"""
        url = f"{self.API_V2}/tweets/search/recent"
        params = {
            "query": query,
            "max_results": str(max_results),
            "tweet.fields": "created_at,public_metrics,author_id",
            "expansions": "author_id",
            "user.fields": "name,username,profile_image_url"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers={"Authorization": self._get_oauth_header("GET", url, params)}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_user_metrics(self) -> Dict[str, Any]:
        """Get user's profile metrics (followers, following, etc.)"""
        me = await self.get_me()
        return {
            "user": me["data"],
            "metrics": me["data"].get("public_metrics", {})
        }
    
    async def like_tweet(self, tweet_id: str) -> bool:
        """Like a tweet"""
        me = await self.get_me()
        user_id = me["data"]["id"]
        
        url = f"{self.API_V2}/users/{user_id}/likes"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={"tweet_id": tweet_id},
                headers={
                    "Authorization": self._get_oauth_header("POST", url),
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            return response.json().get("data", {}).get("liked", False)
    
    async def retweet(self, tweet_id: str) -> bool:
        """Retweet a tweet"""
        me = await self.get_me()
        user_id = me["data"]["id"]
        
        url = f"{self.API_V2}/users/{user_id}/retweets"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={"tweet_id": tweet_id},
                headers={
                    "Authorization": self._get_oauth_header("POST", url),
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            return response.json().get("data", {}).get("retweeted", False)


# Singleton instance
_twitter_service: Optional[TwitterService] = None


def get_twitter_service() -> TwitterService:
    """Get or create Twitter service singleton"""
    global _twitter_service
    if _twitter_service is None:
        _twitter_service = TwitterService()
    return _twitter_service

