# 🚀 Quick Start Guide

## Start Everything (with auto-open browser)

```bash
./scripts/start-dev.sh
```

This will:
- ✅ Start PostgreSQL, Redis, Prometheus, Grafana
- ✅ Start the backend API
- ✅ Start the frontend
- ✅ **Automatically open the UI in your browser**

## Stop Everything

```bash
./scripts/stop-dev.sh
```

## Manual Commands

### Start infrastructure only
```bash
docker-compose up -d
```

### Start backend only
```bash
cd backend
poetry run uvicorn app.main:app --reload
```

### Start frontend only
```bash
cd frontend
npm run dev
```

### Open UI manually
```bash
open http://localhost:5173
```

## Login Credentials

- **Username:** admin
- **Password:** admin123

## Service URLs

| Service | URL |
|---------|-----|
| **Frontend (Main UI)** | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Documentation | http://localhost:8000/docs |
| Grafana Dashboard | http://localhost:3001 |
| Prometheus Metrics | http://localhost:9090 |

## Troubleshooting

### Port already in use
```bash
# Check what's using port 5173
lsof -i :5173

# Kill the process
kill -9 <PID>
```

### Reset everything
```bash
docker-compose down -v
./scripts/start-dev.sh
```

### View logs
```bash
# Backend logs
docker logs agentmedha-backend -f

# Frontend logs
tail -f /tmp/agentmedha-frontend.log
```
