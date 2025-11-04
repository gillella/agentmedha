# 🧪 Phase 4 Testing Guide

**Quick start guide to test the new conversational analytics system**

---

## ⚡ Quick Start (5 minutes)

### Step 1: Run the Migration

```bash
cd backend

# Run migration
docker-compose exec backend alembic upgrade head

# Verify tables created
docker-compose exec postgres psql -U postgres -d agentmedha -c "
SELECT tablename FROM pg_tables 
WHERE tablename LIKE 'conversation%';
"

# Expected output:
#  conversation_sessions
#  conversation_messages
```

### Step 2: Start the Services

```bash
# Make sure all services are running
docker-compose up -d

# Check backend is healthy
curl http://localhost:8000/health

# Expected: {"status": "healthy"}
```

### Step 3: Get Authentication Token

```bash
# Register a user (if you haven't already)
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "securepass123",
    "full_name": "Test User"
  }'

# Login to get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "securepass123"
  }'

# Copy the "access_token" from the response
# Set it as environment variable
export TOKEN="your-access-token-here"
```

---

## 🎯 Test Scenarios

### Scenario 1: Discovery Flow

**Test data source discovery:**

```bash
curl -X POST http://localhost:8000/api/v1/chat/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me sales data"
  }' | jq .

# Expected Response:
# {
#   "session_id": 1,
#   "message_type": "discovery",
#   "content": "I found X data sources...",
#   "data_sources": [
#     {
#       "id": 1,
#       "name": "sales_db",
#       "display_name": "Sales Database",
#       "database_type": "postgresql",
#       ...
#     }
#   ]
# }
```

### Scenario 2: Query Execution

**Execute a query after selecting data source:**

```bash
# Get data_source_id from discovery response above
# Let's say it's 1

curl -X POST http://localhost:8000/api/v1/chat/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me all records",
    "session_id": 1,
    "data_source_id": 1
  }' | jq .

# Expected Response:
# {
#   "session_id": 1,
#   "message_type": "query_result",
#   "content": "I found 100 results...",
#   "sql_query": "SELECT * FROM ...",
#   "results": [...],
#   "result_count": 100,
#   "visualization": {
#     "type": "table",
#     "suggested": false
#   },
#   "suggested_actions": [
#     "Show me top 10",
#     "Export results"
#   ],
#   "context_stats": {
#     "query_tokens": 15,
#     "context_tokens": 2500,
#     "cache_hit": false
#   }
# }
```

### Scenario 3: Multi-Turn Conversation

**Continue the conversation:**

```bash
# Follow-up question using same session
curl -X POST http://localhost:8000/api/v1/chat/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me just the top 5",
    "session_id": 1,
    "data_source_id": 1
  }' | jq .

# The system will:
# - Load conversation history
# - Carry forward context
# - Generate refined SQL with LIMIT 5
```

### Scenario 4: Session Management

**List your sessions:**

```bash
curl http://localhost:8000/api/v1/chat/sessions \
  -H "Authorization: Bearer $TOKEN" | jq .

# Expected:
# {
#   "sessions": [
#     {
#       "id": 1,
#       "status": "active",
#       "title": "Show me sales data",
#       "message_count": 4,
#       ...
#     }
#   ],
#   "total": 1
# }
```

**Get session details:**

```bash
curl http://localhost:8000/api/v1/chat/sessions/1 \
  -H "Authorization: Bearer $TOKEN" | jq .

# Shows full conversation history with all messages
```

**End session:**

```bash
curl -X DELETE http://localhost:8000/api/v1/chat/sessions/1 \
  -H "Authorization: Bearer $TOKEN" | jq .

# Expected:
# {
#   "success": true,
#   "message": "Session ended"
# }
```

---

## 🔍 Debug & Troubleshooting

### Check Database

```bash
# Check sessions
docker-compose exec postgres psql -U postgres -d agentmedha -c "
SELECT id, user_id, status, title, data_source_id, started_at 
FROM conversation_sessions;
"

# Check messages
docker-compose exec postgres psql -U postgres -d agentmedha -c "
SELECT id, session_id, role, message_type, content, created_at 
FROM conversation_messages 
ORDER BY created_at DESC 
LIMIT 10;
"
```

### Check Logs

```bash
# Backend logs
docker-compose logs -f backend | grep "chat_query\|session\|query.processing"

# Look for:
# - "chat_query.request" - New request received
# - "query.discovery" - Running discovery
# - "query.sql_generation" - Generating SQL
# - "query.success" - Query executed successfully
```

### Check Redis Cache

```bash
# Enter Redis CLI
docker-compose exec redis redis-cli

# Check session cache keys
KEYS session:v1:*

# Get a session
GET session:v1:1

# Check context cache
KEYS context:v1:*
```

### Common Issues

**Issue 1: "Session not found"**
```bash
# Solution: Make sure session_id is correct and belongs to user
curl http://localhost:8000/api/v1/chat/sessions \
  -H "Authorization: Bearer $TOKEN"
```

**Issue 2: "Data source not found"**
```bash
# Solution: Check if you have data sources set up
curl http://localhost:8000/api/v1/databases \
  -H "Authorization: Bearer $TOKEN"
```

**Issue 3: "Context retrieval failed"**
```bash
# Solution: Check if context system is set up
docker-compose exec backend python -c "
from app.services.embedding import EmbeddingService
service = EmbeddingService()
emb = service.generate_embedding('test')
print(f'✅ Embeddings working: {len(emb)} dimensions')
"
```

---

## 🧪 Advanced Testing

### Test with Python

```python
import asyncio
from app.models.base import SessionLocal
from app.services.session_manager import SessionManager
from app.services.query_orchestrator import QueryOrchestrator
from app.models.user import User

async def test_session():
    db = SessionLocal()
    
    # Get user
    user = db.query(User).first()
    
    # Create orchestrator
    orchestrator = QueryOrchestrator(db, user)
    
    # Test discovery
    response = await orchestrator.process_message(
        message="Show me sales data"
    )
    print(f"✅ Discovery: {response['message_type']}")
    print(f"   Found {len(response['data_sources'])} sources")
    
    # Test query (assuming data_source_id = 1)
    response = await orchestrator.process_message(
        message="Show me all records",
        session_id=response['session_id'],
        data_source_id=1
    )
    print(f"✅ Query: {response['message_type']}")
    print(f"   Results: {response['result_count']}")
    print(f"   Viz: {response['visualization']['type']}")
    
    await db.close()

# Run test
asyncio.run(test_session())
```

### Load Testing

```bash
# Install Apache Bench
# On Mac: brew install ab
# On Ubuntu: apt-get install apache2-utils

# Test endpoint performance
ab -n 100 -c 10 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -p query.json \
  http://localhost:8000/api/v1/chat/query

# where query.json contains:
# {"message": "Show me all records", "session_id": 1, "data_source_id": 1}

# Expected:
# - 95% of requests < 500ms (discovery)
# - 95% of requests < 5s (query execution)
```

---

## 📊 API Documentation

**View interactive API docs:**

```bash
# Open in browser
open http://localhost:8000/docs

# Navigate to "Conversational Query" section
# Try the endpoints directly from the browser
```

---

## ✅ Success Criteria

After testing, you should be able to:

- [x] Create a new conversation session
- [x] Discover data sources by query
- [x] Select a data source
- [x] Execute SQL queries via natural language
- [x] See SQL query and results
- [x] Get visualization suggestions
- [x] Get follow-up suggestions
- [x] Continue multi-turn conversation
- [x] View session history
- [x] End sessions

---

## 🎯 Next Steps

1. **Frontend Integration**: Update `QueryPage.tsx` to use new endpoint
2. **UI Components**: Add SQL display, results table, chart rendering
3. **Testing**: Write automated tests
4. **Performance**: Monitor and optimize

---

## 📞 Need Help?

**Check logs:**
```bash
docker-compose logs -f backend
```

**Check database:**
```bash
docker-compose exec postgres psql -U postgres -d agentmedha
```

**Reset if needed:**
```bash
# Drop and recreate tables
docker-compose exec backend alembic downgrade -1
docker-compose exec backend alembic upgrade head
```

---

**Happy Testing! 🎉**

*If you encounter any issues, check the logs and database first. Most issues are due to missing data or authentication.*

