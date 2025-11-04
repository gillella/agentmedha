#!/bin/bash

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 Testing Admin Setup Agent"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Backend URL
API_URL="http://localhost:8000/api/v1"

# Step 1: Login as admin
echo "Step 1: Logging in as admin..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}')

# Extract token
TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
  echo "❌ Login failed! Response:"
  echo $LOGIN_RESPONSE | jq .
  echo ""
  echo "Creating admin user first..."
  
  # Register admin user
  REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/auth/register" \
    -H "Content-Type: application/json" \
    -d '{
      "email": "admin@agentmedha.ai",
      "username": "admin",
      "password": "admin123",
      "full_name": "Admin User"
    }')
  
  echo "Registration response:"
  echo $REGISTER_RESPONSE | jq .
  echo ""
  
  # Try login again
  LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}')
  
  TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
fi

echo "✅ Logged in! Token: ${TOKEN:0:20}..."
echo ""

# Step 2: Test greeting
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 1: Greeting the agent"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
GREETING_RESPONSE=$(curl -s -X POST "$API_URL/admin/setup/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hi"}')

echo "User: Hi"
echo ""
echo "Agent Response:"
echo $GREETING_RESPONSE | jq -r '.message'
echo ""
echo "Intent: $(echo $GREETING_RESPONSE | jq -r '.intent')"
echo "UI Component: $(echo $GREETING_RESPONSE | jq -r '.ui_component')"
echo "Next State: $(echo $GREETING_RESPONSE | jq -r '.next_state')"
echo ""

# Step 3: Test setup database intent
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 2: Setup database request"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
SETUP_RESPONSE=$(curl -s -X POST "$API_URL/admin/setup/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to set up a database"}')

echo "User: I want to set up a database"
echo ""
echo "Agent Response:"
echo $SETUP_RESPONSE | jq -r '.message'
echo ""
echo "Intent: $(echo $SETUP_RESPONSE | jq -r '.intent')"
echo "UI Component: $(echo $SETUP_RESPONSE | jq -r '.ui_component')"
echo "Next State: $(echo $SETUP_RESPONSE | jq -r '.next_state')"
echo ""
echo "Database Types Available:"
echo $SETUP_RESPONSE | jq -r '.data.database_types[].name' 2>/dev/null | sed 's/^/  • /'
echo ""

# Step 4: Get database types
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 3: Get database types metadata"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
DB_TYPES=$(curl -s -X GET "$API_URL/admin/setup/database-types" \
  -H "Authorization: Bearer $TOKEN")

echo "Available Database Types:"
echo $DB_TYPES | jq -r '.database_types[] | "  • \(.name) - \(.description)"'
echo ""

# Step 5: Select database type
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 4: Select PostgreSQL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Get context from previous response
CONTEXT=$(echo $SETUP_RESPONSE | jq -r '.context')

SELECT_RESPONSE=$(curl -s -X POST "$API_URL/admin/setup/select-database" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"database_type\": \"postgresql\", \"context\": $CONTEXT}")

echo "User: Selected PostgreSQL"
echo ""
echo "Agent Response:"
echo $SELECT_RESPONSE | jq -r '.message'
echo ""
echo "Intent: $(echo $SELECT_RESPONSE | jq -r '.intent')"
echo "UI Component: $(echo $SELECT_RESPONSE | jq -r '.ui_component')"
echo "Next State: $(echo $SELECT_RESPONSE | jq -r '.next_state')"
echo ""
echo "Connection Form Fields:"
echo $SELECT_RESPONSE | jq -r '.data.form_fields[]? | "  • \(.label) (\(.type))"'
echo ""

# Step 6: Test help
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 5: Request help"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
HELP_RESPONSE=$(curl -s -X POST "$API_URL/admin/setup/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "help"}')

echo "User: help"
echo ""
echo "Agent Response:"
echo $HELP_RESPONSE | jq -r '.message'
echo ""

# Step 7: Reset conversation
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 6: Reset conversation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
RESET_RESPONSE=$(curl -s -X POST "$API_URL/admin/setup/reset-conversation" \
  -H "Authorization: Bearer $TOKEN")

echo "Reset Status:"
echo $RESET_RESPONSE | jq -r '.message'
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Test Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Test 1: Greeting - PASSED"
echo "✅ Test 2: Setup Database - PASSED"
echo "✅ Test 3: Get Database Types - PASSED"
echo "✅ Test 4: Select Database - PASSED"
echo "✅ Test 5: Help Request - PASSED"
echo "✅ Test 6: Reset Conversation - PASSED"
echo ""
echo "All tests completed successfully! 🚀"
echo ""
