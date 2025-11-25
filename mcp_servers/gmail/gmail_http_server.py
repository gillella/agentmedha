#!/usr/bin/env python3
"""
Gmail HTTP API Server for agentMedha
Exposes Gmail operations as REST endpoints for easy integration with the backend.
"""

import json
import os
import base64
import logging
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gmail-http-server")

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels',
]

# Paths for credentials
CREDENTIALS_PATH = os.environ.get(
    'GMAIL_CREDENTIALS_PATH', 
    '/app/credentials/gmail_oauth_credentials.json'
)
TOKEN_PATH = os.environ.get(
    'GMAIL_TOKEN_PATH', 
    '/app/credentials/gmail_oauth_token.json'
)


class GmailService:
    """Gmail API service wrapper."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self.services = {}
        self.credentials = {}
        self._load_credentials()
        self._initialized = True
    
    def _load_credentials(self):
        """Load OAuth credentials from token file."""
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
                    self._save_token(creds, 'primary')
                
                self.credentials['primary'] = creds
                self.services['primary'] = build('gmail', 'v1', credentials=creds)
                logger.info("Gmail service initialized for primary account")
            else:
                logger.warning(f"Token file not found at {TOKEN_PATH}")
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            raise
    
    def _save_token(self, creds: Credentials, account_id: str):
        """Save refreshed token."""
        try:
            token_data = {
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'scopes': list(creds.scopes) if creds.scopes else SCOPES,
                'account': account_id,
                'expiry': creds.expiry.isoformat() if creds.expiry else None
            }
            with open(TOKEN_PATH, 'w') as f:
                json.dump(token_data, f)
        except Exception as e:
            logger.error(f"Failed to save token: {e}")
    
    def get_service(self, account_id: str = 'primary'):
        if account_id not in self.services:
            raise ValueError(f"Account '{account_id}' not configured")
        return self.services[account_id]


# Initialize Gmail service globally
gmail_service: Optional[GmailService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global gmail_service
    try:
        gmail_service = GmailService()
        logger.info("Gmail service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Gmail service: {e}")
    yield
    logger.info("Shutting down Gmail HTTP server")


app = FastAPI(
    title="Gmail MCP HTTP Server",
    description="HTTP API for Gmail operations - Part of agentMedha",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic Models
class SendEmailRequest(BaseModel):
    to: list[str] = Field(..., description="List of recipient emails")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body")
    cc: Optional[list[str]] = Field(default=None)
    bcc: Optional[list[str]] = Field(default=None)
    html: bool = Field(default=False)
    reply_to_message_id: Optional[str] = Field(default=None)


class CreateDraftRequest(BaseModel):
    to: list[str]
    subject: str
    body: str
    html: bool = False


class ModifyLabelsRequest(BaseModel):
    add_labels: Optional[list[str]] = None
    remove_labels: Optional[list[str]] = None


# Helper functions
def extract_body(payload: dict) -> str:
    """Extract email body from payload."""
    if 'body' in payload and payload['body'].get('data'):
        return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                if part['body'].get('data'):
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            elif part['mimeType'] == 'text/html':
                if part['body'].get('data'):
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            elif 'parts' in part:
                body = extract_body(part)
                if body:
                    return body
    return ""


def extract_attachments(payload: dict) -> list[dict]:
    """Extract attachment info."""
    attachments = []
    
    def process_parts(parts):
        for part in parts:
            if part.get('filename'):
                attachments.append({
                    'filename': part['filename'],
                    'mime_type': part['mimeType'],
                    'size': part['body'].get('size', 0),
                    'attachment_id': part['body'].get('attachmentId')
                })
            if 'parts' in part:
                process_parts(part['parts'])
    
    if 'parts' in payload:
        process_parts(payload['parts'])
    return attachments


# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "gmail-mcp-http",
        "gmail_connected": gmail_service is not None and len(gmail_service.services) > 0
    }


@app.get("/accounts")
async def list_accounts():
    """List configured Gmail accounts."""
    if gmail_service is None:
        return {"accounts": [], "error": "Gmail service not initialized"}
    
    accounts = []
    for account_id, service in gmail_service.services.items():
        try:
            profile = service.users().getProfile(userId='me').execute()
            accounts.append({
                'id': account_id,
                'email': profile.get('emailAddress'),
                'messages_total': profile.get('messagesTotal'),
                'threads_total': profile.get('threadsTotal')
            })
        except Exception as e:
            logger.error(f"Failed to get profile for {account_id}: {e}")
    return {"accounts": accounts}


@app.get("/messages")
async def list_messages(
    account_id: str = Query(default="primary"),
    query: Optional[str] = Query(default=None, description="Gmail search query"),
    label_ids: Optional[str] = Query(default=None, description="Comma-separated label IDs"),
    max_results: int = Query(default=20, le=100),
    include_spam_trash: bool = Query(default=False)
):
    """List messages from Gmail."""
    try:
        service = gmail_service.get_service(account_id)
        
        kwargs = {
            'userId': 'me',
            'maxResults': max_results,
            'includeSpamTrash': include_spam_trash
        }
        if query:
            kwargs['q'] = query
        if label_ids:
            kwargs['labelIds'] = label_ids.split(',')
        
        results = service.users().messages().list(**kwargs).execute()
        messages = results.get('messages', [])
        
        detailed_messages = []
        for msg in messages[:max_results]:
            try:
                msg_detail = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'To', 'Subject', 'Date']
                ).execute()
                
                headers = {h['name']: h['value'] for h in msg_detail.get('payload', {}).get('headers', [])}
                detailed_messages.append({
                    'id': msg['id'],
                    'thread_id': msg_detail.get('threadId'),
                    'snippet': msg_detail.get('snippet'),
                    'from': headers.get('From'),
                    'to': headers.get('To'),
                    'subject': headers.get('Subject'),
                    'date': headers.get('Date'),
                    'labels': msg_detail.get('labelIds', []),
                    'is_unread': 'UNREAD' in msg_detail.get('labelIds', [])
                })
            except HttpError as e:
                logger.warning(f"Failed to get message {msg['id']}: {e}")
        
        return {
            'messages': detailed_messages,
            'result_count': len(detailed_messages),
            'next_page_token': results.get('nextPageToken')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/messages/{message_id}")
async def get_message(
    message_id: str,
    account_id: str = Query(default="primary"),
    format: str = Query(default="full")
):
    """Get a specific message."""
    try:
        service = gmail_service.get_service(account_id)
        
        msg = service.users().messages().get(
            userId='me',
            id=message_id,
            format=format
        ).execute()
        
        headers = {h['name']: h['value'] for h in msg.get('payload', {}).get('headers', [])}
        
        return {
            'id': msg['id'],
            'thread_id': msg.get('threadId'),
            'labels': msg.get('labelIds', []),
            'snippet': msg.get('snippet'),
            'from': headers.get('From'),
            'to': headers.get('To'),
            'cc': headers.get('Cc'),
            'subject': headers.get('Subject'),
            'date': headers.get('Date'),
            'body': extract_body(msg.get('payload', {})),
            'attachments': extract_attachments(msg.get('payload', {}))
        }
    except HttpError as e:
        raise HTTPException(status_code=e.resp.status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/threads/{thread_id}")
async def get_thread(
    thread_id: str,
    account_id: str = Query(default="primary")
):
    """Get all messages in a thread."""
    try:
        service = gmail_service.get_service(account_id)
        
        thread = service.users().threads().get(
            userId='me',
            id=thread_id,
            format='full'
        ).execute()
        
        messages = []
        for msg in thread.get('messages', []):
            headers = {h['name']: h['value'] for h in msg.get('payload', {}).get('headers', [])}
            messages.append({
                'id': msg['id'],
                'from': headers.get('From'),
                'to': headers.get('To'),
                'subject': headers.get('Subject'),
                'date': headers.get('Date'),
                'snippet': msg.get('snippet'),
                'body': extract_body(msg.get('payload', {})),
                'labels': msg.get('labelIds', [])
            })
        
        return {
            'thread_id': thread_id,
            'message_count': len(messages),
            'messages': messages
        }
    except HttpError as e:
        raise HTTPException(status_code=e.resp.status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/messages/send")
async def send_email(
    request: SendEmailRequest,
    account_id: str = Query(default="primary")
):
    """Send an email."""
    try:
        service = gmail_service.get_service(account_id)
        
        if request.html:
            message = MIMEMultipart('alternative')
            message.attach(MIMEText(request.body, 'html'))
        else:
            message = MIMEText(request.body)
        
        message['To'] = ', '.join(request.to)
        message['Subject'] = request.subject
        
        if request.cc:
            message['Cc'] = ', '.join(request.cc)
        if request.bcc:
            message['Bcc'] = ', '.join(request.bcc)
        
        profile = service.users().getProfile(userId='me').execute()
        message['From'] = profile['emailAddress']
        
        if request.reply_to_message_id:
            original = service.users().messages().get(
                userId='me',
                id=request.reply_to_message_id,
                format='metadata',
                metadataHeaders=['Message-ID', 'References']
            ).execute()
            headers = {h['name']: h['value'] for h in original.get('payload', {}).get('headers', [])}
            if headers.get('Message-ID'):
                message['In-Reply-To'] = headers['Message-ID']
                message['References'] = headers.get('References', '') + ' ' + headers['Message-ID']
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        send_body = {'raw': raw}
        if request.reply_to_message_id:
            original = service.users().messages().get(userId='me', id=request.reply_to_message_id).execute()
            send_body['threadId'] = original.get('threadId')
        
        result = service.users().messages().send(userId='me', body=send_body).execute()
        
        return {
            'success': True,
            'message_id': result['id'],
            'thread_id': result.get('threadId')
        }
    except HttpError as e:
        raise HTTPException(status_code=e.resp.status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/drafts")
async def create_draft(
    request: CreateDraftRequest,
    account_id: str = Query(default="primary")
):
    """Create a draft email."""
    try:
        service = gmail_service.get_service(account_id)
        
        if request.html:
            message = MIMEMultipart('alternative')
            message.attach(MIMEText(request.body, 'html'))
        else:
            message = MIMEText(request.body)
        
        message['To'] = ', '.join(request.to)
        message['Subject'] = request.subject
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        draft = service.users().drafts().create(
            userId='me',
            body={'message': {'raw': raw}}
        ).execute()
        
        return {
            'success': True,
            'draft_id': draft['id'],
            'message_id': draft['message']['id']
        }
    except HttpError as e:
        raise HTTPException(status_code=e.resp.status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/messages/{message_id}/labels")
async def modify_labels(
    message_id: str,
    request: ModifyLabelsRequest,
    account_id: str = Query(default="primary")
):
    """Modify message labels."""
    try:
        service = gmail_service.get_service(account_id)
        
        body = {}
        if request.add_labels:
            body['addLabelIds'] = request.add_labels
        if request.remove_labels:
            body['removeLabelIds'] = request.remove_labels
        
        result = service.users().messages().modify(
            userId='me',
            id=message_id,
            body=body
        ).execute()
        
        return {
            'success': True,
            'message_id': result['id'],
            'labels': result.get('labelIds', [])
        }
    except HttpError as e:
        raise HTTPException(status_code=e.resp.status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/labels")
async def list_labels(account_id: str = Query(default="primary")):
    """List all labels."""
    try:
        service = gmail_service.get_service(account_id)
        
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        return {
            'labels': [
                {
                    'id': label['id'],
                    'name': label['name'],
                    'type': label.get('type'),
                    'message_count': label.get('messagesTotal', 0),
                    'unread_count': label.get('messagesUnread', 0)
                }
                for label in labels
            ]
        }
    except HttpError as e:
        raise HTTPException(status_code=e.resp.status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/messages/{message_id}/trash")
async def trash_message(
    message_id: str,
    account_id: str = Query(default="primary")
):
    """Move message to trash."""
    try:
        service = gmail_service.get_service(account_id)
        service.users().messages().trash(userId='me', id=message_id).execute()
        return {'success': True, 'message_id': message_id, 'action': 'trashed'}
    except HttpError as e:
        raise HTTPException(status_code=e.resp.status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/messages/{message_id}/archive")
async def archive_message(
    message_id: str,
    account_id: str = Query(default="primary")
):
    """Archive message."""
    try:
        service = gmail_service.get_service(account_id)
        result = service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'removeLabelIds': ['INBOX']}
        ).execute()
        return {'success': True, 'message_id': result['id'], 'action': 'archived'}
    except HttpError as e:
        raise HTTPException(status_code=e.resp.status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search")
async def search_emails(
    query: str,
    account_id: str = Query(default="primary"),
    max_results: int = Query(default=20, le=100)
):
    """Search emails with Gmail search syntax."""
    return await list_messages(
        account_id=account_id,
        query=query,
        max_results=max_results
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
