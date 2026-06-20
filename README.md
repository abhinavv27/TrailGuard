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

TrailGuard is an explainable financial-crime investigation platform that detects suspicious transactions, identifies mule-account networks, visualizes money trails, and turns alerts into evidence-backed investigation cases.

Built with synthetic data for demonstration and research. Human review is always required.

## ❓ Why TrailGuard?

Most fraud systems stop at:
`Transaction → Risk Score → Alert`

TrailGuard goes further:
`Transaction Data → Risk Analysis → Fraud Pattern Detection → Money Trail Graph → Investigation Case → Evidence-Backed Report`

It helps investigators understand why an account is suspicious, where funds came from, and where they moved next.

## 🌟 Key Features

- **Hybrid Risk Scoring** — combines anomaly detection, fraud rules, graph intelligence, and transaction velocity.
- **Mule Money Trail Mode** — detects fan-in/fan-out accounts that receive funds from many sources and rapidly forward them.
- **Interactive Money Trail Graph** — trace funds backward to sources and forward to exit accounts.
- **Fraud Pattern Detection** — detects layering, circular flows, structuring, rapid pass-through, and suspicious account clusters.
- **Explainable Alerts** — every alert includes risk score, reason codes, linked transactions, and graph evidence.
- **Investigation Workspace** — convert alerts into cases with notes, evidence timelines, and linked accounts.
- **AI Investigation Copilot** — summarizes verified evidence and helps analysts understand complex trails.
- **Case Report Export** — generates human-reviewable investigation report drafts.
- **Synthetic Fraud Simulator** — inject mule rings, layering chains, circular flows, and structuring scenarios for demos.

## 🕵️ Mule Money Trail Mode

```text
Victim Accounts
      ↓
  Mule Account
      ↓
Exit / Cash-Out Accounts
```

**Example alert:**
Risk Score: 91/100 — Critical
• 14 incoming senders in 2 hours
• 88% of received funds forwarded in 16 minutes
• 6 downstream accounts involved
• Connected to a circular transfer cluster

## 🏗️ Tech Stack

| Layer | Technologies |
| --- | --- |
| **Frontend** | Next.js, TypeScript, Tailwind CSS |
| **Backend** | FastAPI, Pydantic, SQLAlchemy |
| **Database** | SQLite (default) / PostgreSQL |
| **Detection** | Isolation Forest, rule engine, temporal analysis |
| **Graph Intelligence** | NetworkX + React Force Graph |
| **AI Layer** | Optional LLM for evidence summaries only |

## 📐 Architecture

```text
Next.js Dashboard
        ↓
FastAPI Backend
        ↓
Risk + Pattern + Graph Engine
        ↓
SQLite / PostgreSQL
```

## 🚀 Quick Start

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

**Open:**
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`

## 🎬 Demo Flow

1. Upload the synthetic transaction dataset.
2. Run analysis.
3. Open a critical mule-account alert.
4. Trace source and destination accounts in the graph.
5. Create an investigation case.
6. Generate an evidence-backed report draft.

---
Released under the **MIT License**.
