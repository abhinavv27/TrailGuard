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

## Troubleshooting & Known Fixes (Workarounds)

If you are running into issues with the graph or missing data, the following fixes have been applied and should be noted:

### 1. Missing `metrics_json` Column in Database
If you encounter a `sqlite3.OperationalError: no such column: graph_metrics.metrics_json` crash when loading an Account Intelligence Profile, your local SQLite database is missing a column that the backend expects.
**Workaround/Fix:** We have run a raw SQL migration to add this column (`ALTER TABLE graph_metrics ADD COLUMN metrics_json JSON;`). If you reset your database, ensure Alembic migrations are fully applied using `alembic upgrade head`.

### 2. Demo Scenario "Zero Values" Issue
If you inject the Demo Scenario, the generated accounts may show `$0` for Incoming/Outgoing values. This occurred because the demo script did not pre-calculate `GraphMetrics`.
**Fix Applied:** The backend `/api/v1/accounts/{id}` endpoint now features a dynamic fallback. If `GraphMetrics` are missing, it calculates the incoming/outgoing values and unique counterparties directly from the raw `Transaction` tables on the fly.

### 3. Blank Graph & React-Force-Graph Freezing
If the graph exploration page appears empty but stats show nodes exist, this is caused by `react-query` freezing the state data, preventing the `d3-force` physics engine from assigning `x` and `y` coordinates.
**Fix Applied:** The `graphData` object passed into `<ForceGraph2D />` must be deeply cloned (`JSON.parse(JSON.stringify(graphData))`) to allow the physics engine to safely mutate the nodes.

### 4. Mule Money Trail Toggle Not Highlighting
If turning on the "Mule Money Trail" does nothing, ensure the `GraphEdge` Pydantic schema in the backend includes the `type: str = "normal"` field. Without it, the "suspicious" flag is stripped during serialization, preventing the frontend from applying the red highlights.

## License

TrailGuard AI is open source under the MIT License. See [NOTICE.md](NOTICE.md) for third-party attribution.
