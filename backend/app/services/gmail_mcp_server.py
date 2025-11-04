"""
Gmail MCP Server Implementation

Provides Gmail operations via MCP protocol, using existing Google Auth infrastructure.
This eliminates browser prompts and provides direct AI-to-Gmail communication.
"""
import sys
import os
import json
import base64
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime, timedelta

# Add google-auth helper to path
GOOGLE_AUTH_PATH = Path.home() / ".local" / "bin" / "google-auth"
if str(GOOGLE_AUTH_PATH) not in sys.path:
    sys.path.insert(0, str(GOOGLE_AUTH_PATH))

try:
    from google_api_helper import (
        get_credentials,
        list_emails as helper_list_emails,
        list_calendar_events as helper_list_calendar,
    )
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from email.mime.text import MIMEText
except ImportError as e:
    # Will be handled at runtime
    pass

import structlog

logger = structlog.get_logger()


class GmailMCPServer:
    """
    Gmail MCP Server - Provides Gmail operations via MCP protocol.
    
    Uses existing Google Auth tokens from ~/.local/share/google-auth/
    No browser prompts needed!
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Gmail MCP Server.
        
        Args:
            config: Server configuration with:
                - default_account: Default email account to use
                - accounts: List of available accounts
                - token_path: Path to token storage (optional)
        """
        self.config = config
        self.default_account = config.get('default_account', 'arvinda.reddy@gmail.com')
        self.accounts = config.get('accounts', [self.default_account])
        self.token_path = config.get('token_path', str(Path.home() / '.local' / 'share' / 'google-auth'))
        
        logger.info("gmail_mcp.initialized", default_account=self.default_account)
    
    def get_account(self, account: Optional[str] = None) -> str:
        """Get account email, defaulting to configured default."""
        return account or self.default_account
    
    # MCP Tools - List of available operations
    
    def list_available_tools(self) -> List[Dict[str, Any]]:
        """Return list of MCP tools this server provides."""
        return [
            {
                "name": "gmail_list_emails",
                "description": "List emails from Gmail account",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "account": {
                            "type": "string",
                            "description": "Email account (default: configured default)",
                            "enum": self.accounts
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of emails to return (default: 20)",
                            "default": 20
                        },
                        "query": {
                            "type": "string",
                            "description": "Gmail search query (e.g., 'from:someone@example.com', 'is:unread')"
                        },
                        "mark_read": {
                            "type": "boolean",
                            "description": "Mark emails as read after listing (default: false)",
                            "default": False
                        }
                    }
                }
            },
            {
                "name": "gmail_get_email",
                "description": "Get full content of a specific email",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message_id": {
                            "type": "string",
                            "description": "Gmail message ID"
                        },
                        "account": {
                            "type": "string",
                            "description": "Email account",
                            "enum": self.accounts
                        }
                    },
                    "required": ["message_id"]
                }
            },
            {
                "name": "gmail_send_email",
                "description": "Send an email via Gmail",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "to": {
                            "type": "string",
                            "description": "Recipient email address"
                        },
                        "subject": {
                            "type": "string",
                            "description": "Email subject"
                        },
                        "body": {
                            "type": "string",
                            "description": "Email body (plain text)"
                        },
                        "bcc": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "BCC recipients"
                        },
                        "cc": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "CC recipients"
                        },
                        "account": {
                            "type": "string",
                            "description": "Email account to send from",
                            "enum": self.accounts
                        }
                    },
                    "required": ["to", "subject", "body"]
                }
            },
            {
                "name": "gmail_search_emails",
                "description": "Search emails with advanced filters",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "account": {
                            "type": "string",
                            "description": "Email account",
                            "enum": self.accounts
                        },
                        "query": {
                            "type": "string",
                            "description": "Gmail search query"
                        },
                        "max_results": {
                            "type": "integer",
                            "default": 50
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "gmail_mark_read",
                "description": "Mark emails as read",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of message IDs to mark as read"
                        },
                        "account": {
                            "type": "string",
                            "description": "Email account",
                            "enum": self.accounts
                        }
                    },
                    "required": ["message_ids"]
                }
            },
            {
                "name": "gmail_get_calendar",
                "description": "Get calendar events from Google Calendar",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "account": {
                            "type": "string",
                            "description": "Email account",
                            "enum": self.accounts
                        },
                        "max_results": {
                            "type": "integer",
                            "default": 10
                        },
                        "days_ahead": {
                            "type": "integer",
                            "description": "Number of days ahead to look",
                            "default": 7
                        }
                    }
                }
            }
        ]
    
    # Tool Implementations
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an MCP tool.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        try:
            account = self.get_account(arguments.get('account'))
            
            if tool_name == "gmail_list_emails":
                return await self._list_emails(
                    account=account,
                    max_results=arguments.get('max_results', 20),
                    query=arguments.get('query', ''),
                    mark_read=arguments.get('mark_read', False)
                )
            
            elif tool_name == "gmail_get_email":
                return await self._get_email(
                    account=account,
                    message_id=arguments['message_id']
                )
            
            elif tool_name == "gmail_send_email":
                return await self._send_email(
                    account=account,
                    to=arguments['to'],
                    subject=arguments['subject'],
                    body=arguments['body'],
                    bcc=arguments.get('bcc', []),
                    cc=arguments.get('cc', [])
                )
            
            elif tool_name == "gmail_search_emails":
                return await self._search_emails(
                    account=account,
                    query=arguments['query'],
                    max_results=arguments.get('max_results', 50)
                )
            
            elif tool_name == "gmail_mark_read":
                return await self._mark_read(
                    account=account,
                    message_ids=arguments['message_ids']
                )
            
            elif tool_name == "gmail_get_calendar":
                return await self._get_calendar(
                    account=account,
                    max_results=arguments.get('max_results', 10),
                    days_ahead=arguments.get('days_ahead', 7)
                )
            
            else:
                return {"error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            logger.error("gmail_mcp.tool_error", tool=tool_name, error=str(e))
            return {"error": str(e)}
    
    # Private Implementation Methods
    
    async def _list_emails(
        self,
        account: str,
        max_results: int = 20,
        query: str = "",
        mark_read: bool = False
    ) -> Dict[str, Any]:
        """List emails from Gmail."""
        try:
            result = helper_list_emails(
                max_results=max_results,
                query=query,
                email=account
            )
            
            if mark_read and result.get('emails'):
                # Mark emails as read
                creds = get_credentials(account)
                service = build('gmail', 'v1', credentials=creds)
                
                message_ids = []
                # Get message IDs from the list
                results = service.users().messages().list(
                    userId='me',
                    maxResults=max_results,
                    q=query
                ).execute()
                
                messages = results.get('messages', [])
                for msg in messages:
                    message_ids.append(msg['id'])
                
                if message_ids:
                    # Batch mark as read
                    for msg_id in message_ids[:100]:  # Process in batches
                        try:
                            service.users().messages().modify(
                                userId='me',
                                id=msg_id,
                                body={'removeLabelIds': ['UNREAD']}
                            ).execute()
                        except Exception as e:
                            logger.warning("gmail_mcp.mark_read_error", msg_id=msg_id, error=str(e))
            
            return result
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_email(self, account: str, message_id: str) -> Dict[str, Any]:
        """Get full email content."""
        try:
            creds = get_credentials(account)
            service = build('gmail', 'v1', credentials=creds)
            
            message = service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = {h['name']: h['value'] for h in message['payload']['headers']}
            
            # Extract body
            body = self._extract_email_body(message['payload'])
            
            return {
                "id": message['id'],
                "threadId": message.get('threadId'),
                "from": headers.get('From'),
                "to": headers.get('To'),
                "subject": headers.get('Subject'),
                "date": headers.get('Date'),
                "body": body,
                "snippet": message.get('snippet', ''),
                "headers": headers
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _extract_email_body(self, payload: Dict) -> str:
        """Recursively extract email body from payload."""
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif 'parts' in part:
                    result = self._extract_email_body(part)
                    if result:
                        return result
        elif 'body' in payload and 'data' in payload['body']:
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        return ""
    
    async def _send_email(
        self,
        account: str,
        to: str,
        subject: str,
        body: str,
        bcc: List[str] = None,
        cc: List[str] = None
    ) -> Dict[str, Any]:
        """Send email via Gmail."""
        try:
            creds = get_credentials(account)
            service = build('gmail', 'v1', credentials=creds)
            
            # Create message
            message = MIMEText(body)
            message['To'] = to
            message['From'] = account
            message['Subject'] = subject
            
            if bcc:
                message['Bcc'] = ', '.join(bcc)
            if cc:
                message['Cc'] = ', '.join(cc)
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send
            send_message = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return {
                "success": True,
                "message_id": send_message['id'],
                "to": to,
                "subject": subject,
                "bcc": bcc or [],
                "cc": cc or []
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _search_emails(
        self,
        account: str,
        query: str,
        max_results: int = 50
    ) -> Dict[str, Any]:
        """Search emails with query."""
        return await self._list_emails(
            account=account,
            max_results=max_results,
            query=query,
            mark_read=False
        )
    
    async def _mark_read(
        self,
        account: str,
        message_ids: List[str]
    ) -> Dict[str, Any]:
        """Mark emails as read."""
        try:
            creds = get_credentials(account)
            service = build('gmail', 'v1', credentials=creds)
            
            marked_count = 0
            errors = []
            
            for msg_id in message_ids:
                try:
                    service.users().messages().modify(
                        userId='me',
                        id=msg_id,
                        body={'removeLabelIds': ['UNREAD']}
                    ).execute()
                    marked_count += 1
                except Exception as e:
                    errors.append({"message_id": msg_id, "error": str(e)})
            
            return {
                "success": True,
                "marked_count": marked_count,
                "total": len(message_ids),
                "errors": errors if errors else None
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_calendar(
        self,
        account: str,
        max_results: int = 10,
        days_ahead: int = 7
    ) -> Dict[str, Any]:
        """Get calendar events."""
        try:
            result = helper_list_calendar(
                max_results=max_results,
                days_ahead=days_ahead,
                email=account
            )
            return result
        except Exception as e:
            return {"error": str(e)}


def create_gmail_mcp_server(config: Dict[str, Any]) -> GmailMCPServer:
    """Factory function to create Gmail MCP server."""
    return GmailMCPServer(config)










