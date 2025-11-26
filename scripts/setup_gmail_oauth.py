#!/usr/bin/env python3
"""
Gmail OAuth Setup Script for agentMedha
Supports both Desktop and Web application OAuth credentials.
"""

import os
import json
import sys
from pathlib import Path

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
except ImportError:
    print("Installing required packages...")
    os.system("pip install google-auth-oauthlib google-auth google-api-python-client")
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials

# Scopes required for Gmail MCP
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels',
]

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
CREDENTIALS_DIR = PROJECT_ROOT / "credentials"
OAUTH_CREDENTIALS_PATH = CREDENTIALS_DIR / "gmail_oauth_credentials.json"
TOKEN_PATH = CREDENTIALS_DIR / "gmail_oauth_token.json"


def run_oauth_flow(account_name: str = "primary"):
    """Run the OAuth flow to get tokens."""
    print(f"\n🔐 Starting OAuth flow for account: {account_name}")
    print(f"Using credentials from: {OAUTH_CREDENTIALS_PATH}")
    
    # Load credentials file
    with open(OAUTH_CREDENTIALS_PATH) as f:
        creds_data = json.load(f)
    
    # Determine client type and get config
    if 'web' in creds_data:
        client_config = creds_data
        redirect_uri = creds_data['web']['redirect_uris'][0]
        print(f"Using Web application credentials")
        print(f"Redirect URI: {redirect_uri}")
    elif 'installed' in creds_data:
        client_config = creds_data
        redirect_uri = None
        print(f"Using Desktop application credentials")
    else:
        print("❌ Invalid credentials format")
        return None
    
    # Create the flow
    flow = InstalledAppFlow.from_client_config(
        client_config,
        SCOPES,
        redirect_uri=redirect_uri
    )
    
    # Run the local server flow
    print("\n🌐 A browser window will open for authentication...")
    print("   Please sign in with your Gmail account.\n")
    
    try:
        creds = flow.run_local_server(
            port=8080,
            prompt='consent',
            success_message='✅ Authentication successful! You can close this window.',
            open_browser=True
        )
    except Exception as e:
        print(f"❌ OAuth flow failed: {e}")
        return None
    
    # Get client info for token
    if 'web' in creds_data:
        client_id = creds_data['web']['client_id']
        client_secret = creds_data['web']['client_secret']
    else:
        client_id = creds_data['installed']['client_id']
        client_secret = creds_data['installed']['client_secret']
    
    # Save the token
    token_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': client_id,
        'client_secret': client_secret,
        'scopes': list(creds.scopes) if creds.scopes else SCOPES,
        'account': account_name,
        'expiry': creds.expiry.isoformat() if creds.expiry else None
    }
    
    # Save token
    token_file = TOKEN_PATH if account_name == "primary" else CREDENTIALS_DIR / f"gmail_token_{account_name}.json"
    with open(token_file, 'w') as f:
        json.dump(token_data, f, indent=2)
    
    print(f"\n✅ Token saved to: {token_file}")
    return token_data


def test_gmail_access(token_file: Path):
    """Test Gmail access with the token."""
    try:
        from googleapiclient.discovery import build
        from google.auth.transport.requests import Request
        
        with open(token_file) as f:
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
        
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        
        print(f"✅ Successfully connected to: {profile['emailAddress']}")
        print(f"   Total messages: {profile.get('messagesTotal', 'N/A')}")
        return profile['emailAddress']
    except Exception as e:
        print(f"❌ Gmail test failed: {e}")
        return None


def main():
    """Main setup function."""
    print("\n" + "="*60)
    print("   agentMedha - Gmail OAuth Setup")
    print("="*60)
    
    # Ensure credentials directory exists
    CREDENTIALS_DIR.mkdir(exist_ok=True)
    
    # Check if credentials file exists
    if not OAUTH_CREDENTIALS_PATH.exists():
        print(f"\n❌ OAuth credentials file not found at:")
        print(f"   {OAUTH_CREDENTIALS_PATH}")
        return False
    
    print(f"\n✅ Found credentials file: {OAUTH_CREDENTIALS_PATH}")
    
    # Check existing token
    if TOKEN_PATH.exists():
        print(f"\n📋 Existing token found. Testing...")
        email = test_gmail_access(TOKEN_PATH)
        if email:
            print(f"\n✅ Already authenticated as: {email}")
            response = input("\nDo you want to re-authenticate or add another account? (y/N): ").strip().lower()
            if response != 'y':
                return True
    
    # Run OAuth flow
    print("\n" + "-"*60)
    print("Starting authentication...")
    print("-"*60)
    
    result = run_oauth_flow("primary")
    
    if result:
        print("\n" + "-"*60)
        print("Testing Gmail access...")
        print("-"*60)
        test_gmail_access(TOKEN_PATH)
        
        print("\n🎉 Gmail OAuth setup complete!")
        print("\nTo restart the Gmail MCP server, run:")
        print("  docker-compose restart gmail-mcp")
        
        # Ask about additional accounts
        add_more = input("\nDo you want to add another Gmail account? (y/N): ").strip().lower()
        if add_more == 'y':
            account_name = input("Enter account name (e.g., 'work', 'personal'): ").strip()
            if account_name:
                run_oauth_flow(account_name)
        
        return True
    
    return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
