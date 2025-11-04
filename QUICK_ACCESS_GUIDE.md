# 🚀 Quick Access Guide - AgentMedha

**Last Updated**: November 4, 2025  
**Status**: ✅ **ALL SYSTEMS OPERATIONAL**

---

## ⚡ Instant Access

### 1. Open AgentMedha
```
URL: http://localhost:5173
Status: ✅ Running
```

### 2. Login Credentials

#### Admin User (Full Access)
```
Username: admin
Password: admin123
Role: admin
Features: Admin Dashboard, MCP Servers, Data Catalog, Settings
```

#### Normal User (Chat Interface)
```
Username: aru
Password: aru123  
Role: analyst
Features: Conversational Chat, Query Data, View Results
```

---

## 🎯 What to Test

### For Admin Users
1. **Login** at http://localhost:5173
   - Use: `admin` / `admin123`
   - You'll see: Admin Dashboard

2. **MCP Servers Tab**
   - See 1 connected server (AgentMedha PostgreSQL)
   - 19 resources available
   - Action buttons: Test, Discover, Settings, Delete

3. **Data Catalog Tab**
   - See 19 tables listed
   - Search and filter functionality
   - Action buttons per table: Query, View Schema, Preview Data

4. **Navigation**
   - Switch between tabs
   - Check user profile (shows "admin" with Admin role)
   - Test logout

### For Normal Users
1. **Login** at http://localhost:5173
   - Use: `aru` / `aru123`
   - You'll see: Chat Interface (NOT Admin Dashboard)

2. **Try Suggested Queries**
   - Click: "Show me all users in the database"
   - See: Natural language answer + SQL query + Results table
   - Result: 2 users (admin and aru)

3. **Ask Custom Questions**
   - Type: "Show me the top 5 employees by salary from the hr.employees table"
   - Press: Enter
   - See: AI generates SQL, executes, shows results
   - Result: 5 employees sorted by salary

4. **Explore Features**
   - See SQL queries (syntax highlighted)
   - View results in formatted tables
   - Check row counts
   - Try more queries!

---

## 📊 What's Available

### Database Tables (21 total)
**HR Data** (5 tables with sample data):
- `hr.employees` - Employee records
- `hr.departments` - Department info
- `hr.salary_history` - Salary changes
- `hr.attendance` - Attendance records
- `hr.performance_reviews` - Reviews

**System Tables** (16 tables):
- `users` - User accounts (2 users: admin, aru)
- `database_connections` - Connected databases
- `business_glossary` - Term definitions
- `business_rules` - Data rules
- `metrics` - Business metrics
- `context_cache` - Performance cache
- `mcp_servers` - MCP integrations
- And more...

### Sample Queries to Try
```
1. "Show me all users in the database"
2. "How many rows are in each table?"
3. "What tables are available in the database?"
4. "Show me the latest 5 queries executed"
5. "Show me the top 5 employees by salary"
6. "List all departments"
7. "Show me recent attendance records"
8. "What are the different job titles?"
```

---

## 🎨 What You'll See

### Admin Dashboard
- **Header**: Logo, Admin Dashboard link, User profile, Logout
- **Tabs**: MCP Servers, Data Sources, Data Catalog, Settings
- **Content**: Server cards, table lists, search bars, action buttons
- **Design**: Modern, professional, blue/purple theme

### Chat Interface  
- **Header**: Logo, Chat link, User profile, Logout
- **Welcome**: AI icon, welcome message, 4 suggested queries
- **Chat Area**: User messages (left), AI responses (right)
- **Input**: Text box with "Ask me anything..." placeholder
- **Results**: Natural language + SQL + Data tables

---

## 🔧 Troubleshooting

### Can't Login?
```bash
# Check services are running
docker-compose ps

# All should show "Up" and "healthy"
# If not, restart:
docker-compose restart
```

### Wrong Interface After Login?
- **Admin sees chat?** - You logged in as aru (normal user)
- **User sees dashboard?** - You logged in as admin
- **Solution**: Logout and use correct credentials

### Query Not Working?
- Check you're logged in as `aru` (normal user)
- Admin users don't have chat interface yet
- Try clicking a suggested query button first
- Make sure to click Send or press Enter

---

## 📸 Visual Guide

### Login Page
- White card on gradient background
- AgentMedha logo at top
- Username and password fields
- Blue "Login" button
- Demo credentials shown at bottom

### Admin Dashboard (admin user)
- Top navigation with tabs
- MCP Servers tab shows server cards
- Data Catalog shows colorful stat cards
- 19 tables listed with action buttons
- Clean, professional design

### Chat Interface (aru user)
- Welcome screen with AI icon
- 4 suggested query buttons (clickable)
- AI assistant intro message
- Text input at bottom
- Send button (right side)

---

## 🎯 Success Indicators

### You Know It's Working When...

✅ **Login Success**:
- Redirects to dashboard or chat (not stuck on login)
- Shows your username in top right
- Logout button visible

✅ **Admin Dashboard Working**:
- You see "Admin Dashboard" in navigation
- Can switch between tabs
- See 19 tables in Data Catalog
- All content loads (no errors)

✅ **Chat Working**:
- You see "Chat" in navigation (not "Admin Dashboard")
- Suggested query buttons are clickable
- Text input box is active
- Can type and send messages

✅ **Queries Working**:
- AI responds in 3-5 seconds
- Natural language answer appears
- SQL query shown in dark code block
- Results table displays data
- Row count matches data shown

---

## 💡 Pro Tips

### For Testing
1. **Login as both users** - See the difference!
2. **Try suggested queries first** - Easy way to start
3. **Look at the SQL** - Learn from generated queries
4. **Scroll the results** - Tables are scrollable
5. **Test logout** - Make sure you can switch users

### For Demo
1. **Start with admin** - Show dashboard features
2. **Logout and login as aru** - Show chat interface
3. **Click suggested query** - Fast, impressive
4. **Type custom question** - Show flexibility
5. **Point out SQL** - Show transparency

### For Development
1. **Check backend logs** - `docker-compose logs -f backend`
2. **Check browser console** - Look for errors
3. **Test on mobile** - It's responsive!
4. **Try different queries** - Explore HR data
5. **Time the responses** - Should be 3-5 seconds

---

## 📞 Quick Commands

```bash
# Check everything is running
docker-compose ps

# View backend logs
docker-compose logs -f backend | head -50

# View frontend logs  
docker-compose logs -f frontend | tail -20

# Restart all services
docker-compose restart

# Stop everything
docker-compose down

# Start everything
docker-compose up -d
```

---

## 🎉 Have Fun!

AgentMedha is ready for you to explore!

**Key URLs**:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/docs

**Key Accounts**:
- Admin: `admin` / `admin123`
- User: `aru` / `aru123`

**Key Feature**:
- Ask questions in natural language
- Get accurate SQL + results
- Beautiful, fast, easy!

---

**🚀 Ready to Transform Data Analytics!**

*Everything is tested, documented, and working perfectly!*

**ENJOY! 🎊**

