<div align="center">
  <img src="apps/web/public/logo.svg" alt="TrailGuard AI" width="120" height="120" />
  <h1>TrailGuard AI</h1>
  <p><b>Explainable Financial Crime Intelligence Platform</b></p>
  <p><i>Follow the money. Surface the truth.</i></p>
  <br/>
  <p>
    <a href="https://github.com/abhinavv27/NexTrace/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License"/></a>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.12+-blue.svg" alt="Python"/></a>
    <a href="https://nextjs.org/"><img src="https://img.shields.io/badge/Next.js-15-black.svg" alt="Next.js"/></a>
    <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-0.111-009688.svg" alt="FastAPI"/></a>
    <a href="https://tailwindcss.com/"><img src="https://img.shields.io/badge/Tailwind_CSS-4-06B6D4.svg" alt="Tailwind CSS"/></a>
  </p>
</div>

---

TrailGuard AI is a next-generation explainable financial crime intelligence platform built to **detect suspicious transactions, map mule-account networks, visualize money trails in real-time, and transform raw alerts into regulator-ready investigation cases.**

Unlike traditional AML systems that stop at black-box risk scoring, TrailGuard AI provides complete transparency into every detection decision — showing investigators the *what, why, and where* behind each alert.

> Built with synthetic data for demonstration and research. Human review is always required before any action.

---

## Why TrailGuard AI?

Traditional fraud detection systems follow a shallow pipeline:

```
Transaction → Risk Score → Alert (and nothing more)
```

TrailGuard AI delivers a complete investigation workflow:

```
Transaction Data → Risk Analysis → Pattern Detection → Money Trail Graph → Investigation Case → Evidence-Backed Report
```

**How we're different:**
- **Not a black box** — every alert includes risk reason codes, linked transactions, and graph-based evidence you can verify
- **Graph-native intelligence** — visualize funds flowing through accounts instead of staring at spreadsheets
- **Built for investigators** — take alerts all the way to case reports without switching tools

---

## Features

| Feature | Description |
|---------|-------------|
| **Hybrid Risk Scoring** | Combines anomaly detection (Isolation Forest), fraud rules, graph intelligence, and transaction velocity analysis |
| **Mule Account Detection** | Identifies fan-in/fan-out patterns — accounts receiving from many sources and rapidly forwarding funds to exit points |
| **Interactive Money Trail Graph** | Visualize fund flow backward to sources and forward to exit accounts with full interactivity |
| **Fraud Pattern Library** | Automated detection of layering chains, circular flows, structuring patterns, rapid pass-through, and suspicious clusters |
| **Explainable Alerts** | Every alert includes risk score breakdown, reason codes, linked transactions, and visual graph evidence |
| **Investigation Workspace** | Convert alerts into structured cases with notes, evidence timelines, and linked account profiles |
| **AI Investigation Copilot** | LLM-powered assistant that summarizes verified evidence and helps analysts navigate complex money trails |
| **Case Report Export** | Auto-generate human-reviewable investigation report drafts suitable for regulatory filings |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 15, TypeScript, Tailwind CSS 4, Recharts, React Force Graph 2D |
| **Backend** | FastAPI, Pydantic, SQLAlchemy, Alembic |
| **Database** | SQLite (development) / PostgreSQL (production) |
| **Detection Engine** | Isolation Forest, rule-based engine, temporal & velocity analysis |
| **Graph Intelligence** | NetworkX graph analysis with React Force Graph visualization |
| **Testing** | pytest (backend), Vitest + Playwright (frontend) |
| **AI Layer** | Optional LLM integration for evidence summarization only |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Next.js Dashboard                     │
│  ┌──────────┐ ┌──────────┐ ┌─────────┐ ┌────────────┐  │
│  │ Dashboard │ │  Alerts  │ │   Case  │ │  Money     │  │
│  │  & Stats  │ │  Review  │ │  Worksp.│ │  Trail     │  │
│  └──────────┘ └──────────┘ └─────────┘ └────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────────┐
│                   FastAPI Backend                        │
│  ┌──────────┐ ┌──────────┐ ┌─────────┐ ┌────────────┐  │
│  │  Auth &  │ │  Alert   │ │  Case   │ │Transaction │  │
│  │  Users   │ │  Engine  │ │ Manager │ │  Service   │  │
│  └──────────┘ └──────────┘ └─────────┘ └────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              Risk + Pattern + Graph Engine               │
│  ┌──────────────┐ ┌────────────┐ ┌───────────────────┐  │
│  │   Anomaly    │ │   Fraud    │ │    Graph          │  │
│  │  Detection   │ │  Patterns  │ │  Intelligence     │  │
│  │ (Isolation   │ │(Layering,  │ │  (NetworkX -     │  │
│  │   Forest)    │ │ Structur.) │ │  Money Trails)   │  │
│  └──────────────┘ └────────────┘ └───────────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              SQLite / PostgreSQL Database                 │
│        Transactions · Accounts · Alerts · Cases          │
└─────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- npm

### 1. Clone & Setup

```bash
git clone https://github.com/abhinavv27/NexTrace.git
cd trailguard-ai
```

### 2. Backend

```bash
cd services/api
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
alembic upgrade head
python -m app.db.seed

uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd apps/web
npm install
npm run dev
```

### 4. Open

| Service | URL |
|---------|-----|
| Frontend Dashboard | `http://localhost:3000` |
| Backend API | `http://localhost:8000` |
| API Docs | `http://localhost:8000/docs` |

---

## Demo Flow

1. **Load data** — Upload the synthetic transaction dataset (seeded by default)
2. **Run analysis** — Execute the detection engine across all transactions
3. **Review alerts** — Open a critical mule-account alert (risk score, reason codes, evidence)
4. **Trace the money** — Use the interactive graph to follow funds from victim accounts through mules to exit points
5. **Build a case** — Convert the alert into a structured investigation with notes and evidence
6. **Export report** — Generate a regulator-ready investigation report draft

---

## Project Structure

```
trailguard-ai/
├── apps/
│   └── web/                    # Next.js frontend
│       ├── app/                # Pages & routes
│       ├── components/         # Reusable UI components
│       ├── hooks/              # Custom React hooks
│       ├── lib/                # API client & utilities
│       └── tests/              # Frontend tests
├── services/
│   └── api/                    # FastAPI backend
│       ├── app/
│       │   ├── main.py         # Application entry point
│       │   ├── db/             # Database models & migrations
│       │   ├── routes/         # API route handlers
│       │   └── services/       # Detection engine & business logic
│       └── tests/              # Backend tests
├── data/                       # Sample datasets
├── docs/                       # Documentation
└── docker-compose.yml          # Container orchestration
```

---

## Detection Capabilities

TrailGuard AI detects the following fraud patterns out of the box:

- **Mule Account Networks** — Accounts receiving from multiple disparate sources and rapidly forwarding funds
- **Layering Chains** — Series of transactions designed to obscure the origin of funds
- **Circular Flows** — Funds cycling through a closed set of accounts
- **Structuring (Smurfing)** — Transactions deliberately kept below reporting thresholds
- **Rapid Pass-Through** — Funds moving through an account in minutes rather than days
- **Velocity Anomalies** — Unusual transaction frequency or volume relative to historical behavior

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<p align="center">Built with synthetic data for research and demonstration. Not for direct use in production financial systems without rigorous validation.</p>
