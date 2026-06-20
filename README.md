<div align="center">
  <h1>🛡️ TrailGuard</h1>
  <p><b>Explainable Financial Crime Intelligence Platform</b></p>
  <p><i>Follow the money. Surface the truth.</i></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.12+-blue.svg" alt="Python" />
    <img src="https://img.shields.io/badge/Next.js-15-black.svg" alt="Next.js" />
    <img src="https://img.shields.io/badge/FastAPI-0.111-009688.svg" alt="FastAPI" />
    <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License" />
  </p>
</div>

---

TrailGuard is an AI-powered investigation platform that helps analysts detect suspicious transactions, identify money mule networks, and trace complex fund movements. By combining anomaly detection, graph intelligence, and an AI copilot, TrailGuard explains not just *what* is suspicious, but *why*—turning raw data into evidence-backed cases.

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

## ⚖️ Disclaimer & License

**Important:** TrailGuard is a synthetic-data prototype designed for investigation support. It uses deterministic datasets for demonstration. It does not make legal determinations or replace human investigators.

Released under the **MIT License**.
