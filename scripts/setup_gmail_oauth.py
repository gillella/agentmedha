#!/usr/bin/env python3
"""
Gmail OAuth Setup Script for agentMedha
This script helps set up OAuth credentials for the Gmail MCP server.

Usage:
    python scripts/setup_gmail_oauth.py
"""

import os
import json
import sys
from pathlib import Path

# Add support for Google auth flow
try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
except ImportError:
    print("Installing required packages...")
    os.system("pip install google-auth-oauthlib google-auth")
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


def print_setup_instructions():
    """Print instructions for creating OAuth credentials."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    Gmail OAuth Setup for agentMedha                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  To use the Gmail MCP server, you need to create OAuth credentials:          ║
║                                                                              ║
║  1. Go to: https://console.cloud.google.com/apis/credentials                 ║
║                                                                              ║
║  2. Create a new project (or select existing one)                            ║
║                                                                              ║
║  3. Enable the Gmail API:                                                    ║
║     - Go to "Library" → Search "Gmail API" → Enable                          ║
║                                                                              ║
║  4. Configure OAuth consent screen:                                          ║
║     - Go to "OAuth consent screen"                                           ║
║     - Choose "External" or "Internal" (for workspace)                        ║
║     - Fill in app name: "agentMedha Gmail"                                   ║
║     - Add your email as test user                                            ║
║     - Add scopes: Gmail API (all scopes)                                     ║
║                                                                              ║
║  5. Create OAuth credentials:                                                ║
║     - Go to "Credentials" → "Create Credentials" → "OAuth client ID"         ║
║     - Application type: "Desktop app"                                        ║
║     - Name: "agentMedha Gmail Client"                                        ║
║     - Click "Create"                                                         ║
║                                                                              ║
║  6. Download the JSON file and save it as:                                   ║
║     credentials/gmail_oauth_credentials.json                                 ║
║                                                                              ║
║  7. Run this script again to complete the OAuth flow                         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")


def run_oauth_flow():
    """Run the OAuth flow to get tokens."""
    print("\n🔐 Starting OAuth flow...")
    print(f"Using credentials from: {OAUTH_CREDENTIALS_PATH}")
    
    # Create the flow
    flow = InstalledAppFlow.from_client_secrets_file(
        str(OAUTH_CREDENTIALS_PATH),
        SCOPES
    )
    
    # Run the local server flow
    print("\n🌐 A browser window will open for authentication...")
    print("   If it doesn't open automatically, check your terminal for a URL.\n")
    
    creds = flow.run_local_server(
        port=8080,
        prompt='consent',
        success_message='Authentication successful! You can close this window.'
    )
    
    # Save the token
    token_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': list(creds.scopes) if creds.scopes else SCOPES,
        'account': 'primary',
        'expiry': creds.expiry.isoformat() if creds.expiry else None
    }
    
    with open(TOKEN_PATH, 'w') as f:
        json.dump(token_data, f, indent=2)
    
    print(f"\n✅ Token saved to: {TOKEN_PATH}")
    print("\n🎉 Gmail OAuth setup complete!")
    print("\nYou can now start the Gmail MCP server:")
    print("  docker-compose up -d gmail-mcp")
    
    return True


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
        print_setup_instructions()
        return False
    
    # Validate the credentials file
    try:
        with open(OAUTH_CREDENTIALS_PATH) as f:
            creds_data = json.load(f)
        
        if 'installed' not in creds_data and 'web' not in creds_data:
            print("\n❌ Invalid credentials file format.")
            print("   Expected 'installed' or 'web' client credentials.")
            print_setup_instructions()
            return False
        
        print(f"\n✅ Found credentials file")
        client_type = 'installed' if 'installed' in creds_data else 'web'
        project_id = creds_data[client_type].get('project_id', 'Unknown')
        print(f"   Project: {project_id}")
        
    except json.JSONDecodeError:
        print("\n❌ Invalid JSON in credentials file.")
        print_setup_instructions()
        return False
    
    # Check if token already exists
    if TOKEN_PATH.exists():
        print(f"\n⚠️  Token file already exists at: {TOKEN_PATH}")
        response = input("   Do you want to re-authenticate? (y/N): ").strip().lower()
        if response != 'y':
            print("\n   Keeping existing token.")
            return True
    
    # Run OAuth flow
    return run_oauth_flow()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
