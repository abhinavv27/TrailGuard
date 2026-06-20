# TrailGuard AI

An explainable financial-crime investigation platform that identifies suspicious transactions, detects mule-account networks and layered money trails, visualizes the movement of funds interactively, and converts evidence into investigator-ready case reports.

## Architecture

Next.js Web App (port 3000) ↔ FastAPI Backend (port 8000) → SQLite (data/trailguard.db)

Two processes, zero containers.

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.12+

### Setup

```bash
# 1. Install dependencies
cd services/api && pip install -r requirements.txt
cd apps/web && npm install

# 2. Run database migrations
cd services/api && alembic upgrade head

# 3. Seed demo data
python -m app.db.seed

# 4. Start backend (Terminal 1)
cd services/api && uvicorn app.main:app --reload --port 8000

# 5. Start frontend (Terminal 2)
cd apps/web && npm run dev
```

### Demo Credentials
- Admin: admin@trailguard.ai / admin1234
- Analyst: analyst@trailguard.ai / demo1234

## Tech Stack
- **Frontend:** Next.js 15, TypeScript, Tailwind CSS, TanStack Query, Recharts, React Force Graph
- **Backend:** Python 3.12+, FastAPI, SQLAlchemy 2.x, NetworkX, scikit-learn
- **Database:** SQLite (auto-created at data/trailguard.db)

## Project Structure

```
trailguard-ai/
├── apps/web/                # Next.js frontend
│   ├── app/                 # App Router pages
│   ├── components/          # React components
│   ├── hooks/               # Custom hooks
│   └── lib/                 # Utilities & API client
├── services/api/            # FastAPI backend
│   ├── app/                 # Application code
│   │   ├── api/             # Route handlers
│   │   ├── core/            # Config & security
│   │   ├── db/              # Database layer
│   │   ├── detection/       # Detection engine
│   │   ├── graph/           # Graph analysis
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   └── reports/         # Report generation
│   └── tests/               # Backend tests
├── data/                    # SQLite database lives here
├── docs/                    # Documentation
├── package.json             # Root convenience scripts
├── start.sh                 # Linux/Mac launcher
├── start.ps1                # Windows launcher
└── .env.example             # Environment template
```

## Security

- JWT-based authentication with 30-minute token expiry
- Role-based access control (Analyst, Investigator, Admin)
- All input validated via Pydantic schemas
- Passwords hashed with bcrypt
- CORS restricted to configured origins
- Audit logging for sensitive operations

See [SECURITY.md](SECURITY.md) for full security policy.

## License

TrailGuard AI is open source under the MIT License. See [NOTICE.md](NOTICE.md) for third-party attribution.
