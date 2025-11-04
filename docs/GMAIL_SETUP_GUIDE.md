# Gmail Setup Guide for AgentMedha

## 📧 Adding Gmail Accounts

### Your GCP Project
- **Project Name**: `aru-gmail-auth-project`
- **Accounts to Add**:
  - arvinda.gillella@gmail.com
  - arvinda.reddy@gmail.com

---

## 🚀 Setup Steps

### Step 1: Download OAuth Credentials

1. Go to [GCP Console - Credentials](https://console.cloud.google.com/apis/credentials?project=aru-gmail-auth-project)
2. Find your OAuth 2.0 Client ID
3. Click **⬇️ DOWNLOAD JSON** button
4. Save the downloaded file

### Step 2: Replace Credentials File

```bash
# Copy your downloaded OAuth credentials to the correct location
cp ~/Downloads/client_secret_*.json ~/.local/share/google-auth/credentials.json
```

### Step 3: Add Test Users to OAuth Consent Screen

⚠️ **Important**: Before authenticating, make sure both emails are added as test users:

1. Go to [OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent?project=aru-gmail-auth-project)
2. Click **"ADD USERS"** under "Test users"
3. Add both:
   - `arvinda.gillella@gmail.com`
   - `arvinda.reddy@gmail.com`
4. Click **"SAVE"**

### Step 4: Authenticate Your Accounts

```bash
# Remove old tokens (they're from deleted OAuth client)
rm ~/.local/share/google-auth/token_*.json

# Authenticate first account
~/.local/bin/gmail switch --email arvinda.gillella@gmail.com
# Browser will open - sign in and grant permissions

# Authenticate second account  
~/.local/bin/gmail switch --email arvinda.reddy@gmail.com
# Browser will open - sign in and grant permissions
```

### Step 5: Verify Setup

```bash
# List all accounts
~/.local/bin/gmail list

# Test fetching emails
~/.local/bin/gmail emails

# Test both accounts
~/.local/bin/gmail emails --account arvinda.gillella@gmail.com
~/.local/bin/gmail emails --account arvinda.reddy@gmail.com
```

---

## 🔧 Using with AgentMedha

Once authenticated, AgentMedha will automatically use these accounts through the Gmail MCP server.

The MCP server configuration is already set up in:
- `backend/app/services/gmail_mcp_server.py`

### Default Account
The system uses `arvinda.reddy@gmail.com` as the default account.

### Switching Accounts

To change which account AgentMedha uses:

```bash
~/.local/bin/gmail switch --email arvinda.gillella@gmail.com
```

Or use the interactive switcher:

```bash
~/.local/bin/switch-google-account
```

---

## 📁 File Locations

| File | Location | Purpose |
|------|----------|---------|
| OAuth Credentials | `~/.local/share/google-auth/credentials.json` | OAuth client from GCP |
| Account Config | `~/.local/share/google-auth/config.json` | Active account & list |
| Token (gillella) | `~/.local/share/google-auth/token_arvinda_gillella_at_gmail_com.json` | Auth token |
| Token (reddy) | `~/.local/share/google-auth/token_arvinda_reddy_at_gmail_com.json` | Auth token |

---

## ⚠️ Troubleshooting

### "deleted_client" Error

This means the OAuth client was deleted in GCP. Follow Steps 1-4 above to fix.

### "Access Denied" Error

Make sure the email is added as a test user in the OAuth consent screen (Step 3).

### Re-authenticate Account

```bash
# Remove token
rm ~/.local/share/google-auth/token_arvinda_reddy_at_gmail_com.json

# Re-authenticate
~/.local/bin/gmail switch --email arvinda.reddy@gmail.com
```

### Check Active Account

```bash
~/.local/bin/gmail list
# Active account shows "✓ ACTIVE"
```

---

## 🔐 Security Notes

- Never commit `credentials.json` or `token_*.json` files to git
- These files are already in `.gitignore`
- OAuth scopes: Gmail, Calendar, Drive (read/write)
- Direct Google API access - no third-party servers

---

## 📚 Resources

- **GCP Console**: https://console.cloud.google.com/apis/credentials?project=aru-gmail-auth-project
- **OAuth Consent**: https://console.cloud.google.com/apis/credentials/consent?project=aru-gmail-auth-project
- **Connected Apps**: https://myaccount.google.com/permissions

---

**Last Updated**: November 4, 2025





