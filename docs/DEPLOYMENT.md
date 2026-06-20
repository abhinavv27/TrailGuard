# TrailGuard AI — Deployment Guide

## Local Development (No-Docker)

### Prerequisites
- Node.js 18+
- Python 3.12+
- Git

### Setup

```bash
git clone https://github.com/your-org/trailguard-ai.git
cd trailguard-ai
cp .env.example .env

# Install dependencies
cd services/api && pip install -r requirements.txt
cd ../..
cd apps/web && npm install
cd ../..

# Run database migrations
cd services/api && alembic upgrade head

# Seed demo data
python -m app.db.seed
```

### Running (Two Terminals)

**Terminal 1 — Backend:**
```bash
cd services/api
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd apps/web
npm run dev
```

Or use the convenience launchers:
```bash
# Linux/Mac
./start.sh

# Windows PowerShell
./start.ps1
```

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database connectivity (via API)
curl http://localhost:8000/health/db

# Frontend
curl http://localhost:3000
```

### Access
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Stopping
Press `Ctrl+C` in each terminal, or kill the background processes from the launcher script.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | No | `sqlite:///../../data/trailguard.db` | SQLite connection (auto-created) |
| `SECRET_KEY` | No | `dev-secret-key-change-in-production` | JWT signing secret |
| `CORS_ORIGINS` | No | `http://localhost:3000` | Allowed CORS origins |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | JWT token expiry |
| `DEMO_MODE` | No | `true` | Enable demo features |
| `LLM_PROVIDER` | No | (none) | LLM provider (openai, anthropic) |
| `LLM_API_KEY` | No | (none) | LLM API key (optional) |
| `STRUCTURING_THRESHOLD` | No | `10000` | Structuring detection threshold |
| `STRUCTURING_WINDOW_HOURS` | No | `24` | Structuring time window |

## Production Considerations

### Database (SQLite vs PostgreSQL)

SQLite is ideal for local dev, demos, and single-user deployments. For multi-user production:

**When to keep SQLite:**
- Single-analyst investigations
- Internal audit tools with one concurrent user
- Demos and training environments

**When to switch to PostgreSQL:**
- Multiple concurrent users
- High write throughput
- Horizontal scaling needed

To switch, update `DATABASE_URL` in `.env`:
```
DATABASE_URL=postgresql://user:password@host:5432/trailguard
```

### API
- Set a strong `SECRET_KEY` (64+ random characters)
- Disable `DEMO_MODE` by setting `DEMO_MODE=false`
- Configure `CORS_ORIGINS` to match your frontend domain
- Use a production ASGI server: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4`
- Enable request rate limiting

### Frontend
- Build for production: `npm run build`
- Set `NEXT_PUBLIC_API_URL` to production API URL
- Configure custom domain and SSL via Vercel

## Platform Deployment

### Vercel (Frontend)

```bash
npm i -g vercel
cd apps/web
vercel --prod
```

Set environment variable: `NEXT_PUBLIC_API_URL=https://your-api.railway.app`

### Render / Fly.io (API + Database)

**Render:**

```bash
# Deploy API as a Web Service
# Build command: pip install -r requirements.txt
# Start command: uvicorn app.main:app --host 0.0.0.0 --port 8000
# Add a PostgreSQL or SQLite persistent disk
```

**Fly.io:**

```bash
fly launch
fly deploy
fly postgres create
fly postgres attach
```

### Running with PostgreSQL

If switching to PostgreSQL, install the driver:

```bash
pip install psycopg2-binary
```

Update `.env`:
```
DATABASE_URL=postgresql://user:password@host:5432/trailguard
```

## Health Check Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | API server status |
| `GET /health/db` | Database connectivity check |

Returns `{"status": "healthy"}` or `{"status": "unhealthy"}` with appropriate HTTP status codes.
