#!/usr/bin/env python3
"""
Gmail MCP Server for agentMedha
A Model Context Protocol server that provides Gmail integration tools.
This is the stdio-based MCP server implementation.
"""

import asyncio
import json
import os
import base64
import logging
from typing import Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, CallToolResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gmail-mcp-server")

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.modify',
]

# Paths for credentials
CREDENTIALS_PATH = os.environ.get('GMAIL_CREDENTIALS_PATH', '/app/credentials/gmail_oauth_credentials.json')
TOKEN_PATH = os.environ.get('GMAIL_TOKEN_PATH', '/app/credentials/gmail_oauth_token.json')


class GmailService:
    """Gmail API service wrapper."""
    
    def __init__(self):
        self.services = {}
        self._load_credentials()
    
    def _load_credentials(self):
        """Load OAuth credentials."""
        try:
            if os.path.exists(TOKEN_PATH):
                with open(TOKEN_PATH, 'r') as f:
                    token_data = json.load(f)
                
                creds = Credentials(
                    token=token_data.get('token'),
                    refresh_token=token_data.get('refresh_token'),
                    token_uri=token_data.get('token_uri'),
                    client_id=token_data.get('client_id'),
                    client_secret=token_data.get('client_secret'),
                    scopes=token_data.get('scopes', SCOPES)
                )
                
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                
                self.services['primary'] = build('gmail', 'v1', credentials=creds)
                logger.info("Gmail service initialized")
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
    
    def get_service(self, account_id: str = 'primary'):
        if account_id not in self.services:
            raise ValueError(f"Account '{account_id}' not configured")
        return self.services[account_id]


class GmailMCPServer:
    """MCP Server for Gmail operations."""
    
    def __init__(self):
        self.server = Server("gmail-mcp-server")
        self.gmail = GmailService()
        self._register_handlers()
    
    def _register_handlers(self):
        """Register MCP tool handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="gmail_list_messages",
                    description="List emails from Gmail with optional search query",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Gmail search query"},
                            "max_results": {"type": "integer", "default": 20}
                        }
                    }
                ),
                Tool(
                    name="gmail_get_message",
                    description="Get full details of a specific email",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message_id": {"type": "string", "description": "Message ID"}
                        },
                        "required": ["message_id"]
                    }
                ),
                Tool(
                    name="gmail_send_email",
                    description="Send an email",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "to": {"type": "array", "items": {"type": "string"}},
                            "subject": {"type": "string"},
                            "body": {"type": "string"}
                        },
                        "required": ["to", "subject", "body"]
                    }
                ),
                Tool(
                    name="gmail_search",
                    description="Search emails with Gmail syntax",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"}
                        },
                        "required": ["query"]
                    }
                ),
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> CallToolResult:
            try:
                if name == "gmail_list_messages":
                    result = await self._list_messages(**arguments)
                elif name == "gmail_get_message":
                    result = await self._get_message(**arguments)
                elif name == "gmail_send_email":
                    result = await self._send_email(**arguments)
                elif name == "gmail_search":
                    result = await self._list_messages(query=arguments.get('query'))
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Unknown tool: {name}")],
                        isError=True
                    )
                
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(result, indent=2))]
                )
            except Exception as e:
                logger.error(f"Error in {name}: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True
                )
    
    async def _list_messages(self, query: str = None, max_results: int = 20) -> dict:
        """List messages."""
        service = self.gmail.get_service()
        kwargs = {'userId': 'me', 'maxResults': max_results}
        if query:
            kwargs['q'] = query
        
        results = service.users().messages().list(**kwargs).execute()
        messages = []
        
        for msg in results.get('messages', [])[:max_results]:
            msg_detail = service.users().messages().get(
                userId='me', id=msg['id'], format='metadata',
                metadataHeaders=['From', 'Subject', 'Date']
            ).execute()
            headers = {h['name']: h['value'] for h in msg_detail.get('payload', {}).get('headers', [])}
            messages.append({
                'id': msg['id'],
                'from': headers.get('From'),
                'subject': headers.get('Subject'),
                'date': headers.get('Date'),
                'snippet': msg_detail.get('snippet')
            })
        
        return {'messages': messages, 'count': len(messages)}
    
    async def _get_message(self, message_id: str) -> dict:
        """Get message details."""
        service = self.gmail.get_service()
        msg = service.users().messages().get(userId='me', id=message_id, format='full').execute()
        headers = {h['name']: h['value'] for h in msg.get('payload', {}).get('headers', [])}
        
        body = ""
        payload = msg.get('payload', {})
        if 'body' in payload and payload['body'].get('data'):
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        elif 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain' and part['body'].get('data'):
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
        
        return {
            'id': msg['id'],
            'from': headers.get('From'),
            'to': headers.get('To'),
            'subject': headers.get('Subject'),
            'date': headers.get('Date'),
            'body': body
        }
    
    async def _send_email(self, to: list[str], subject: str, body: str) -> dict:
        """Send email."""
        service = self.gmail.get_service()
        message = MIMEText(body)
        message['To'] = ', '.join(to)
        message['Subject'] = subject
        
        profile = service.users().getProfile(userId='me').execute()
        message['From'] = profile['emailAddress']
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        result = service.users().messages().send(userId='me', body={'raw': raw}).execute()
        
        return {'success': True, 'message_id': result['id']}
    
    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, self.server.create_initialization_options())


def main():
    """Main entry point."""
    server = GmailMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
