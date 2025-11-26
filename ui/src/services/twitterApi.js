/**
 * Twitter API Service for agentMedha Social Media Manager
 * 
 * Communicates with the FastAPI backend to interact with Twitter/X API
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Helper function for API calls
 */
async function fetchApi(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const response = await fetch(url, { ...defaultOptions, ...options });
    
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || 'API request failed');
    }
    
    return response.json();
}

export const twitterApi = {
    /**
     * Get authenticated user's profile
     */
    async getMe() {
        return fetchApi('/api/twitter/me');
    },
    
    /**
     * Get user's recent tweets (timeline)
     */
    async getTimeline(maxResults = 10, paginationToken = null) {
        let endpoint = `/api/twitter/timeline?max_results=${maxResults}`;
        if (paginationToken) {
            endpoint += `&pagination_token=${paginationToken}`;
        }
        return fetchApi(endpoint);
    },
    
    /**
     * Post a new tweet
     */
    async postTweet(text, options = {}) {
        return fetchApi('/api/twitter/tweet', {
            method: 'POST',
            body: JSON.stringify({
                text,
                media_ids: options.mediaIds || null,
                reply_to: options.replyTo || null,
                quote_tweet_id: options.quoteTweetId || null,
            }),
        });
    },
    
    /**
     * Delete a tweet
     */
    async deleteTweet(tweetId) {
        return fetchApi(`/api/twitter/tweet/${tweetId}`, {
            method: 'DELETE',
        });
    },
    
    /**
     * Get a specific tweet by ID
     */
    async getTweet(tweetId) {
        return fetchApi(`/api/twitter/tweet/${tweetId}`);
    },
    
    /**
     * Upload media for attachment to tweets
     */
    async uploadMedia(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_BASE}/api/twitter/media`, {
            method: 'POST',
            body: formData,
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(error.detail || 'Media upload failed');
        }
        
        return response.json();
    },
    
    /**
     * Search for tweets
     */
    async searchTweets(query, maxResults = 10) {
        return fetchApi(`/api/twitter/search?query=${encodeURIComponent(query)}&max_results=${maxResults}`);
    },
    
    /**
     * Get user's profile metrics
     */
    async getMetrics() {
        return fetchApi('/api/twitter/metrics');
    },
    
    /**
     * Like a tweet
     */
    async likeTweet(tweetId) {
        return fetchApi(`/api/twitter/like/${tweetId}`, {
            method: 'POST',
        });
    },
    
    /**
     * Retweet a tweet
     */
    async retweet(tweetId) {
        return fetchApi(`/api/twitter/retweet/${tweetId}`, {
            method: 'POST',
        });
    },
    
    /**
     * Check if Twitter API is connected and working
     */
    async checkConnection() {
        try {
            const result = await this.getMe();
            return {
                connected: true,
                user: result.data,
            };
        } catch (error) {
            return {
                connected: false,
                error: error.message,
            };
        }
    },
};

export default twitterApi;

