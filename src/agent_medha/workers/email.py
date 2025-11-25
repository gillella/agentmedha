"""
Email Worker for agentMedha
Integrates with the Gmail MCP HTTP Server to provide email management capabilities.
"""

import os
import httpx
from typing import Optional
from langchain_core.tools import tool

# Gmail MCP Server URL
GMAIL_MCP_URL = os.environ.get("GMAIL_MCP_URL", "http://localhost:8001")


class GmailClient:
    """HTTP client for Gmail MCP Server."""
    
    def __init__(self, base_url: str = GMAIL_MCP_URL):
        self.base_url = base_url
        self.client = httpx.Client(timeout=30.0)
    
    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make HTTP request to Gmail MCP server."""
        url = f"{self.base_url}{endpoint}"
        response = self.client.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    
    def list_accounts(self) -> dict:
        return self._request("GET", "/accounts")
    
    def list_messages(self, account_id: str = "primary", query: str = None, max_results: int = 20) -> dict:
        params = {"account_id": account_id, "max_results": max_results}
        if query:
            params["query"] = query
        return self._request("GET", "/messages", params=params)
    
    def get_message(self, message_id: str, account_id: str = "primary") -> dict:
        return self._request("GET", f"/messages/{message_id}", params={"account_id": account_id})
    
    def get_thread(self, thread_id: str, account_id: str = "primary") -> dict:
        return self._request("GET", f"/threads/{thread_id}", params={"account_id": account_id})
    
    def send_email(self, to: list[str], subject: str, body: str, account_id: str = "primary", 
                   cc: list[str] = None, reply_to_message_id: str = None) -> dict:
        data = {"to": to, "subject": subject, "body": body}
        if cc:
            data["cc"] = cc
        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id
        return self._request("POST", "/messages/send", params={"account_id": account_id}, json=data)
    
    def create_draft(self, to: list[str], subject: str, body: str, account_id: str = "primary") -> dict:
        return self._request("POST", "/drafts", params={"account_id": account_id},
                           json={"to": to, "subject": subject, "body": body})
    
    def search(self, query: str, account_id: str = "primary", max_results: int = 20) -> dict:
        return self._request("GET", "/search", 
                           params={"query": query, "account_id": account_id, "max_results": max_results})
    
    def list_labels(self, account_id: str = "primary") -> dict:
        return self._request("GET", "/labels", params={"account_id": account_id})
    
    def trash_message(self, message_id: str, account_id: str = "primary") -> dict:
        return self._request("POST", f"/messages/{message_id}/trash", params={"account_id": account_id})
    
    def archive_message(self, message_id: str, account_id: str = "primary") -> dict:
        return self._request("POST", f"/messages/{message_id}/archive", params={"account_id": account_id})


# Initialize global client
gmail_client = GmailClient()


# LangChain Tools
@tool
def list_email_accounts() -> str:
    """List all configured Gmail accounts with their email addresses and message counts."""
    try:
        result = gmail_client.list_accounts()
        accounts = result.get("accounts", [])
        if not accounts:
            return "No Gmail accounts configured."
        
        output = "📧 Configured Gmail Accounts:\n"
        for acc in accounts:
            output += f"\n• {acc['email']} ({acc['id']})\n"
            output += f"  - Total messages: {acc.get('messages_total', 'N/A')}\n"
        return output
    except Exception as e:
        return f"Error listing accounts: {str(e)}"


@tool
def read_emails(query: str = None, account_id: str = "primary", max_results: int = 10) -> str:
    """
    Read emails from Gmail. Use Gmail search syntax for filtering.
    
    Args:
        query: Gmail search query (e.g., "is:unread", "from:john@example.com", "subject:meeting")
        account_id: Account to read from (default: "primary")
        max_results: Maximum number of emails to return (default: 10)
    """
    try:
        result = gmail_client.list_messages(account_id=account_id, query=query, max_results=max_results)
        messages = result.get("messages", [])
        
        if not messages:
            return f"No emails found{' matching: ' + query if query else ''}."
        
        output = f"📬 Found {len(messages)} email(s):\n\n"
        for i, msg in enumerate(messages, 1):
            unread = "🔵 " if msg.get("is_unread") else ""
            output += f"{i}. {unread}{msg.get('subject', '(no subject)')}\n"
            output += f"   From: {msg.get('from', 'Unknown')}\n"
            output += f"   Date: {msg.get('date', 'Unknown')}\n"
            output += f"   ID: {msg.get('id')}\n\n"
        return output
    except Exception as e:
        return f"Error reading emails: {str(e)}"


@tool
def get_email_details(message_id: str, account_id: str = "primary") -> str:
    """Get full details of a specific email including the complete body."""
    try:
        msg = gmail_client.get_message(message_id, account_id)
        
        output = f"📧 Email Details:\n\n"
        output += f"From: {msg.get('from', 'Unknown')}\n"
        output += f"To: {msg.get('to', 'Unknown')}\n"
        output += f"Subject: {msg.get('subject', '(no subject)')}\n"
        output += f"Date: {msg.get('date', 'Unknown')}\n\n"
        output += f"--- Body ---\n{msg.get('body', '(empty)')}\n"
        return output
    except Exception as e:
        return f"Error getting email: {str(e)}"


@tool
def send_email(to: str, subject: str, body: str, account_id: str = "primary") -> str:
    """
    Send an email from your Gmail account.
    
    Args:
        to: Recipient email address (comma-separated for multiple)
        subject: Email subject
        body: Email body content
        account_id: Account to send from (default: "primary")
    """
    try:
        to_list = [e.strip() for e in to.split(",")]
        result = gmail_client.send_email(to=to_list, subject=subject, body=body, account_id=account_id)
        
        if result.get("success"):
            return f"✅ Email sent successfully!\nMessage ID: {result.get('message_id')}"
        return f"❌ Failed to send email: {result}"
    except Exception as e:
        return f"Error sending email: {str(e)}"


@tool
def search_emails(query: str, account_id: str = "primary", max_results: int = 10) -> str:
    """
    Search emails using Gmail's powerful search syntax.
    
    Args:
        query: Search query (e.g., "from:john@example.com", "subject:invoice", "has:attachment")
        account_id: Account to search in (default: "primary")
        max_results: Maximum results to return (default: 10)
    """
    try:
        result = gmail_client.search(query, account_id, max_results)
        messages = result.get("messages", [])
        
        if not messages:
            return f"No emails found matching: {query}"
        
        output = f"🔍 Search Results for '{query}' ({len(messages)} found):\n\n"
        for i, msg in enumerate(messages, 1):
            output += f"{i}. {msg.get('subject', '(no subject)')}\n"
            output += f"   From: {msg.get('from', 'Unknown')}\n"
            output += f"   ID: {msg.get('id')}\n\n"
        return output
    except Exception as e:
        return f"Error searching emails: {str(e)}"


class EmailManager:
    """Email Manager for agentMedha - provides tools for email operations."""
    
    def get_tools(self):
        """Return all email tools for the agent."""
        return [
            list_email_accounts,
            read_emails,
            get_email_details,
            send_email,
            search_emails
        ]
