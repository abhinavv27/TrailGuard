# TrailGuard

**Explainable Financial Crime Intelligence Platform**

> **Follow the money. Surface the truth.**

TrailGuard is an AI-powered investigation platform that helps analysts detect suspicious transactions, identify money mule networks, and trace complex fund movements. By combining anomaly detection, graph intelligence, and an AI copilot, TrailGuard explains not just *what* is suspicious, but *why*—turning raw data into evidence-backed cases.

---

## 🌟 Key Features

- **Hybrid Risk Scoring:** Explains risk (0-100) using anomaly detection, graph network risk, and temporal behaviors.
- **Mule Money Trail Mode:** Visually isolates and highlights rapid "fan-in / fan-out" fund dispersal patterns.
- **Interactive Graph Visualization:** Trace source and destination accounts dynamically using directed transaction graphs.
- **Explainable AML Alerts:** Deterministic rule-checks for Structuring, Layering, Circular Transfers, and Rapid Pass-Throughs.
- **Account Intelligence Profiles:** Deep-dive into historical risk, counterparty overlap, holding times, and graph centrality.
- **AI Investigation Copilot:** Context-aware assistant that summarizes suspicious activity based entirely on verified evidence.

## 🏗️ Architecture & Tech Stack

TrailGuard is built as a highly performant, local-first web application.

- **Frontend:** Next.js, TypeScript, Tailwind CSS, TanStack Query, React Force Graph
- **Backend:** Python 3.12, FastAPI, SQLAlchemy, NetworkX, scikit-learn
- **Database:** SQLite / PostgreSQL
- **Design:** `react-force-graph` for physics-based network visualization, `shadcn/ui` for components.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.12+

### 1. Backend Setup
```bash
cd services/api
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run migrations and seed synthetic demo data
alembic upgrade head
python -m app.db.seed

# Start the API server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd apps/web
npm install
npm run dev
```
Navigate to `http://localhost:3000` to begin.

---

## 🛠️ Troubleshooting & Known Fixes

If you encounter issues during local testing or demo scenarios:

1. **Missing `metrics_json` Database Crash:** If the Account Profile crashes with `no such column: graph_metrics.metrics_json`, manually run the SQL: `ALTER TABLE graph_metrics ADD COLUMN metrics_json JSON;` or reset your DB and re-run `alembic upgrade head`.
2. **Demo Scenario "$0 Values":** The backend API now features a dynamic fallback to calculate unique counterparties and incoming/outgoing values from raw transactions if pre-calculated `GraphMetrics` are missing.
3. **Blank Graph (React-Force-Graph):** If your graph exploration page is blank but data exists, this is caused by strict state freezing in `react-query`. The `graphData` object is automatically deep-cloned before being passed to `d3-force` to prevent physics engine crashes.
4. **Mule Money Trail Highlights:** The `type` field was previously stripped during Pydantic serialization. The `GraphEdge` schema has been updated (`type: str = "normal"`) to correctly pass suspicious flags to the frontend for red-edge highlighting.

---

## ⚖️ Disclaimer & License

**Important:** TrailGuard is a synthetic-data prototype designed for investigation support. It uses deterministic datasets for demonstration. It does not make legal determinations or replace human investigators.

Released under the **MIT License**.
