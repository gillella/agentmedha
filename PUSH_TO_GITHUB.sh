#!/bin/bash

# AgentMedha - Push to GitHub Script
# Replace YOUR_USERNAME with your actual GitHub username

echo "🚀 Pushing AgentMedha to GitHub..."
echo ""
echo "⚠️  IMPORTANT: Replace YOUR_USERNAME with your actual GitHub username below!"
echo ""

# Option 1: HTTPS (will prompt for credentials)
# git remote add origin https://github.com/YOUR_USERNAME/agentmedha.git

# Option 2: SSH (requires SSH key setup)
# git remote add origin git@github.com:YOUR_USERNAME/agentmedha.git

# After adding the remote, push
# git push -u origin main

echo ""
echo "Steps to complete:"
echo "1. Create repository on GitHub: https://github.com/new"
echo "2. Name it: agentmedha"
echo "3. DO NOT initialize with README"
echo "4. Copy the repository URL"
echo "5. Run: git remote add origin <YOUR_REPO_URL>"
echo "6. Run: git push -u origin main"
echo ""
echo "Or use GitHub CLI:"
echo "  gh repo create agentmedha --public --source=. --remote=origin --push"

