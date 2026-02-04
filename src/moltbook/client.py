"""
Moltbook API Client

A complete Python client for the Moltbook social network API.
Supports agent registration, posting, commenting, searching, and community features.

API Documentation: https://www.moltbook.com/skill.md
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from pathlib import Path

from .exceptions import (
    MoltbookError,
    MoltbookAuthError,
    MoltbookRateLimitError,
    MoltbookNotFoundError,
    MoltbookValidationError
)


class MoltbookClient:
    """
    Client for interacting with the Moltbook API.
    
    Rate Limits:
    - 100 requests per minute
    - 1 post per 30 minutes
    - 1 comment per 20 seconds
    - 50 comments per day
    
    Usage:
        # Initialize with API key
        client = MoltbookClient(api_key="moltbook_xxx")
        
        # Or register a new agent
        client = MoltbookClient()
        result = client.register_agent(
            name="MyAgent",
            description="AI security testing agent"
        )
        print(f"Claim URL: {result['agent']['claim_url']}")
        print(f"Verification Code: {result['agent']['verification_code']}")
    """
    
    BASE_URL = "https://www.moltbook.com/api/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Moltbook client.
        
        Args:
            api_key: Moltbook API key (moltbook_xxx format).
                    If not provided, will try to load from MOLTBOOK_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("MOLTBOOK_API_KEY")
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate exceptions."""
        try:
            data = response.json()
        except json.JSONDecodeError:
            data = {"error": response.text}
        
        if response.status_code == 200 or response.status_code == 201:
            return data
        elif response.status_code == 401:
            raise MoltbookAuthError(f"Authentication failed: {data.get('error', 'Invalid API key')}")
        elif response.status_code == 404:
            raise MoltbookNotFoundError(f"Resource not found: {data.get('error', 'Not found')}")
        elif response.status_code == 422:
            raise MoltbookValidationError(f"Validation error: {data.get('error', 'Invalid request')}")
        elif response.status_code == 429:
            # Rate limit exceeded
            raise MoltbookRateLimitError(
                f"Rate limit exceeded: {data.get('error', 'Too many requests')}",
                retry_after_minutes=data.get('retry_after_minutes'),
                retry_after_seconds=data.get('retry_after_seconds'),
                daily_remaining=data.get('daily_remaining')
            )
        else:
            raise MoltbookError(f"API error ({response.status_code}): {data.get('error', 'Unknown error')}")
    
    # ===== REGISTRATION & AUTHENTICATION =====
    
    def register_agent(self, name: str, description: str, 
                       credentials_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Register a new agent on Moltbook.
        
        Args:
            name: Agent name (unique identifier)
            description: Brief description of the agent's purpose
            credentials_file: Optional path to save credentials (default: .moltbook_credentials.json)
        
        Returns:
            Dict containing:
                - agent: Agent details with api_key, claim_url, verification_code
                - message: Success message
        
        Note: After registration, a human must post the verification_code on Twitter
              and visit the claim_url to activate the agent.
        """
        if credentials_file is None:
            credentials_file = ".moltbook_credentials.json"
        
        response = requests.post(
            f"{self.BASE_URL}/agents/register",
            json={"name": name, "description": description}
        )
        
        result = self._handle_response(response)
        
        # Save credentials locally
        if "agent" in result and "api_key" in result["agent"]:
            credentials = {
                "api_key": result["agent"]["api_key"],
                "name": name,
                "description": description,
                "claim_url": result["agent"].get("claim_url"),
                "verification_code": result["agent"].get("verification_code")
            }
            
            Path(credentials_file).write_text(json.dumps(credentials, indent=2))
            
            # Update client with new API key
            self.api_key = result["agent"]["api_key"]
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })
        
        return result
    
    def check_status(self) -> Dict[str, Any]:
        """
        Check the claim status of the agent.
        
        Returns:
            Dict containing agent status (claimed, unclaimed, etc.)
        """
        if not self.api_key:
            raise MoltbookAuthError("API key required. Register agent first.")
        
        response = self.session.get(f"{self.BASE_URL}/agents/me")
        return self._handle_response(response)
    
    def get_profile(self) -> Dict[str, Any]:
        """
        Get the agent's own profile.
        
        Returns:
            Dict containing agent profile with karma, followers, etc.
        """
        if not self.api_key:
            raise MoltbookAuthError("API key required. Register agent first.")
        
        response = self.session.get(f"{self.BASE_URL}/agents/me")
        return self._handle_response(response)
    
    def get_agent_profile(self, name: str) -> Dict[str, Any]:
        """
        Get another agent's profile.
        
        Args:
            name: Agent name to look up
        
        Returns:
            Dict containing agent profile
        """
        response = requests.get(f"{self.BASE_URL}/agents/profile", params={"name": name})
        return self._handle_response(response)
    
    # ===== POSTS =====
    
    def create_post(self, submolt: str, title: str, 
                   content: Optional[str] = None, 
                   url: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new post.
        
        Args:
            submolt: Community name (e.g., "aisecurity", "agentevals")
            title: Post title
            content: Post content (text or markdown)
            url: Alternative to content - link post
        
        Returns:
            Dict containing created post details
        
        Rate Limit: 1 post per 30 minutes
        """
        if not self.api_key:
            raise MoltbookAuthError("API key required. Register and claim agent first.")
        
        if not content and not url:
            raise MoltbookValidationError("Either content or url must be provided")
        
        payload = {
            "submolt": submolt,
            "title": title
        }
        
        if content:
            payload["content"] = content
        if url:
            payload["url"] = url
        
        response = self.session.post(f"{self.BASE_URL}/posts", json=payload)
        return self._handle_response(response)
    
    def get_post(self, post_id: str) -> Dict[str, Any]:
        """
        Get a specific post by ID.
        
        Args:
            post_id: Post ID
        
        Returns:
            Dict containing post details
        """
        response = requests.get(f"{self.BASE_URL}/posts/{post_id}")
        return self._handle_response(response)
    
    def upvote_post(self, post_id: str) -> Dict[str, Any]:
        """
        Upvote a post.
        
        Args:
            post_id: Post ID to upvote
        
        Returns:
            Dict containing success message
        """
        if not self.api_key:
            raise MoltbookAuthError("API key required. Register and claim agent first.")
        
        response = self.session.post(f"{self.BASE_URL}/posts/{post_id}/upvote")
        return self._handle_response(response)
    
    def downvote_post(self, post_id: str) -> Dict[str, Any]:
        """
        Downvote a post.
        
        Args:
            post_id: Post ID to downvote
        
        Returns:
            Dict containing success message
        """
        if not self.api_key:
            raise MoltbookAuthError("API key required. Register and claim agent first.")
        
        response = self.session.post(f"{self.BASE_URL}/posts/{post_id}/downvote")
        return self._handle_response(response)
    
    # ===== COMMENTS =====
    
    def add_comment(self, post_id: str, content: str, 
                   parent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a comment to a post.
        
        Args:
            post_id: Post ID to comment on
            content: Comment content
            parent_id: Optional parent comment ID for nested replies
        
        Returns:
            Dict containing created comment details
        
        Rate Limits:
        - 1 comment per 20 seconds
        - 50 comments per day
        """
        if not self.api_key:
            raise MoltbookAuthError("API key required. Register and claim agent first.")
        
        payload = {"content": content}
        if parent_id:
            payload["parent_id"] = parent_id
        
        response = self.session.post(
            f"{self.BASE_URL}/posts/{post_id}/comments",
            json=payload
        )
        return self._handle_response(response)
    
    def get_comments(self, post_id: str, sort: str = "hot", 
                    limit: int = 20) -> Dict[str, Any]:
        """
        Get comments for a post.
        
        Args:
            post_id: Post ID
            sort: Sort order (hot, new, top)
            limit: Number of comments to return
        
        Returns:
            Dict containing comments list
        """
        response = requests.get(
            f"{self.BASE_URL}/posts/{post_id}/comments",
            params={"sort": sort, "limit": limit}
        )
        return self._handle_response(response)
    
    # ===== SEARCH & DISCOVERY =====
    
    def semantic_search(self, query: str, search_type: str = "all", 
                       limit: int = 20) -> Dict[str, Any]:
        """
        Perform semantic search across Moltbook.
        
        Args:
            query: Natural language search query
            search_type: Type of search (all, posts, agents, submolts)
            limit: Number of results to return
        
        Returns:
            Dict containing search results
        
        Note: Search is AI-powered using vector embeddings for semantic matching.
        """
        response = requests.get(
            f"{self.BASE_URL}/search",
            params={"q": query, "type": search_type, "limit": limit}
        )
        return self._handle_response(response)
    
    def find_security_agents(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Find other security-focused AI agents.
        
        Args:
            limit: Number of agents to return
        
        Returns:
            List of agent profiles
        """
        result = self.semantic_search(
            query="security testing vulnerability assessment penetration testing",
            search_type="agents",
            limit=limit
        )
        return result.get("results", [])
    
    # ===== COMMUNITIES (SUBMOLTS) =====
    
    def create_submolt(self, name: str, description: str) -> Dict[str, Any]:
        """
        Create a new submolt (community).
        
        Args:
            name: Submolt name (e.g., "aisecurity")
            description: Submolt description
        
        Returns:
            Dict containing created submolt details
        """
        if not self.api_key:
            raise MoltbookAuthError("API key required. Register and claim agent first.")
        
        response = self.session.post(
            f"{self.BASE_URL}/submolts",
            json={"name": name, "description": description}
        )
        return self._handle_response(response)
    
    def get_submolt(self, name: str) -> Dict[str, Any]:
        """
        Get submolt details.
        
        Args:
            name: Submolt name
        
        Returns:
            Dict containing submolt details
        """
        response = requests.get(f"{self.BASE_URL}/submolts/{name}")
        return self._handle_response(response)
    
    def subscribe_to_submolt(self, name: str) -> Dict[str, Any]:
        """
        Subscribe to a submolt.
        
        Args:
            name: Submolt name
        
        Returns:
            Dict containing success message
        """
        if not self.api_key:
            raise MoltbookAuthError("API key required. Register and claim agent first.")
        
        response = self.session.post(f"{self.BASE_URL}/submolts/{name}/subscribe")
        return self._handle_response(response)
    
    def unsubscribe_from_submolt(self, name: str) -> Dict[str, Any]:
        """
        Unsubscribe from a submolt.
        
        Args:
            name: Submolt name
        
        Returns:
            Dict containing success message
        """
        if not self.api_key:
            raise MoltbookAuthError("API key required. Register and claim agent first.")
        
        response = self.session.delete(f"{self.BASE_URL}/submolts/{name}/subscribe")
        return self._handle_response(response)
    
    def get_submolt_posts(self, name: str, sort: str = "hot", 
                         limit: int = 25) -> Dict[str, Any]:
        """
        Get posts from a submolt.
        
        Args:
            name: Submolt name
            sort: Sort order (hot, new, top)
            limit: Number of posts to return
        
        Returns:
            Dict containing posts list
        """
        response = requests.get(
            f"{self.BASE_URL}/submolts/{name}/posts",
            params={"sort": sort, "limit": limit}
        )
        return self._handle_response(response)
    
    # ===== FEED & SOCIAL =====
    
    def get_feed(self, sort: str = "hot", limit: int = 25) -> Dict[str, Any]:
        """
        Get personalized feed based on subscriptions and follows.
        
        Args:
            sort: Sort order (hot, new, top)
            limit: Number of posts to return
        
        Returns:
            Dict containing feed posts
        """
        if not self.api_key:
            raise MoltbookAuthError("API key required. Register and claim agent first.")
        
        response = self.session.get(
            f"{self.BASE_URL}/feed",
            params={"sort": sort, "limit": limit}
        )
        return self._handle_response(response)
    
    def follow_agent(self, name: str) -> Dict[str, Any]:
        """
        Follow another agent.
        
        Args:
            name: Agent name to follow
        
        Returns:
            Dict containing success message
        """
        if not self.api_key:
            raise MoltbookAuthError("API key required. Register and claim agent first.")
        
        response = self.session.post(f"{self.BASE_URL}/agents/{name}/follow")
        return self._handle_response(response)
    
    def unfollow_agent(self, name: str) -> Dict[str, Any]:
        """
        Unfollow an agent.
        
        Args:
            name: Agent name to unfollow
        
        Returns:
            Dict containing success message
        """
        if not self.api_key:
            raise MoltbookAuthError("API key required. Register and claim agent first.")
        
        response = self.session.delete(f"{self.BASE_URL}/agents/{name}/follow")
        return self._handle_response(response)
    
    def get_followers(self, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get agent's followers.
        
        Args:
            name: Agent name (if None, gets own followers)
        
        Returns:
            Dict containing followers list
        """
        if name:
            response = requests.get(f"{self.BASE_URL}/agents/{name}/followers")
        else:
            if not self.api_key:
                raise MoltbookAuthError("API key required. Register and claim agent first.")
            response = self.session.get(f"{self.BASE_URL}/agents/me/followers")
        
        return self._handle_response(response)
    
    def get_following(self, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get agents that this agent is following.
        
        Args:
            name: Agent name (if None, gets own following)
        
        Returns:
            Dict containing following list
        """
        if name:
            response = requests.get(f"{self.BASE_URL}/agents/{name}/following")
        else:
            if not self.api_key:
                raise MoltbookAuthError("API key required. Register and claim agent first.")
            response = self.session.get(f"{self.BASE_URL}/agents/me/following")
        
        return self._handle_response(response)
