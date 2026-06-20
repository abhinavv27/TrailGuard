# TrailGuard

### Explainable Financial Crime Intelligence Platform

> **Follow the money. Surface the truth.**

TrailGuard is an AI-powered financial crime investigation platform designed to help analysts detect suspicious transactions, identify money mule networks, trace complex fund movements, and convert raw transaction data into explainable, evidence-backed investigation cases.

It combines anomaly detection, rule-based AML pattern detection, graph intelligence, temporal analysis, and an optional AI investigation copilot to help investigators understand not only **what is suspicious**, but also **why it is suspicious and where the money moved next**.

> **Important:** TrailGuard is a synthetic-data prototype for investigation support. It does not make legal determinations, confirm fraud, or replace human investigators.

---

## Problem

Financial crime investigations often involve thousands of transactions spread across many accounts, devices, channels, and time windows.

Traditional systems usually stop at:

```text
Transaction → Risk Score → Alert
```

That is not enough for an investigator.

Investigators need to know:

* Why was an account flagged?
* Which accounts are connected?
* Where did the funds originate?
* Where did the money move next?
* Is this activity part of a mule network, layering chain, circular transfer pattern, or structuring attempt?
* What evidence supports the case?

TrailGuard turns raw transaction data into a visible and explainable investigation workflow.

---

# Core Value Proposition

```text
Upload Transaction Data
        ↓
Detect Suspicious Behaviour
        ↓
Identify Fraud and AML Patterns
        ↓
Map Money Movement Through Graph Intelligence
        ↓
Trace Source and Destination Accounts
        ↓
Create Evidence-Backed Investigation Cases
        ↓
Generate Human-Reviewable Report Drafts
```

Instead of showing a vague fraud alert, TrailGuard gives investigators a complete financial trail.

---

# Key Features

## 1. Hybrid Risk Scoring Engine

Every transaction and account receives a risk score from `0–100`.

The score is built from multiple explainable signals:

```text
30% Anomaly Score
30% Fraud Pattern Severity
25% Graph / Network Risk
15% Velocity and Temporal Behaviour
```

Risk levels:

|  Score | Risk Level |
| -----: | ---------- |
|   0–44 | Low        |
|  45–74 | Medium     |
|  75–89 | High       |
| 90–100 | Critical   |

Every score includes reason codes and evidence references.

Example:

```text
Account: ACC-7821
Risk Score: 91/100 — Critical

Why flagged:
• Received funds from 14 unrelated accounts in 2 hours
• Forwarded 88% of funds within 16 minutes
• Sent money to 6 downstream accounts
• Connected to a high-risk circular transaction cluster
```

---

## 2. Mule Money Trail Mode

Mule Money Trail Mode is TrailGuard’s primary differentiator.

It identifies accounts that appear to collect money from many unrelated sources and rapidly move it through multiple downstream accounts.

It detects:

* many incoming transfers from unrelated senders
* rapid forwarding of received funds
* fan-in activity
* fan-out activity
* unusually short holding time
* newly created accounts handling high-value transfers
* high-risk network clusters
* connected exit or cash-out accounts

Example:

```text
Victim Accounts
      ↓
  Mule Account
      ↓
Multiple Exit Accounts
```

---

## 3. Interactive Money Trail Visualization

TrailGuard converts transaction records into an interactive directed graph.

```text
Node = Account
Edge = Transaction
Direction = Fund Movement
Colour = Risk Level
```

Investigators can:

* trace money backward to source accounts
* trace money forward to destination or exit accounts
* expand one, two, or three transaction hops
* inspect account-level intelligence
* filter by date, risk level, amount, country, channel, and transaction type
* highlight suspicious paths
* isolate circular flows
* focus on suspected mule rings
* inspect transaction evidence directly from graph edges

---

## 4. Fraud and AML Pattern Detection

TrailGuard detects suspicious financial behaviour using deterministic rules, graph analytics, and temporal analysis.

### Supported Patterns

| Pattern                | Description                                                     |
| ---------------------- | --------------------------------------------------------------- |
| Mule Activity          | Many incoming transfers followed by rapid fund dispersal        |
| Layering               | Funds moving through several accounts to obscure origin         |
| Circular Transfers     | Funds returning to an earlier account through a cycle           |
| Structuring            | Multiple smaller transfers grouped below a configured threshold |
| Rapid Pass-Through     | Funds entering and leaving an account within a short time       |
| Fan-In                 | Many senders transferring to one account                        |
| Fan-Out                | One account distributing value to many accounts                 |
| New Account Risk       | Recently created accounts moving unusually high value           |
| Counterparty Expansion | Sudden increase in unique senders or receivers                  |
| Network Cluster Risk   | Suspicious accounts connected in a high-risk graph cluster      |

---

## 5. Explainable Alerts

TrailGuard does not create black-box alerts.

Each alert includes:

* risk score
* severity level
* triggering detector
* reason codes
* involved transactions
* connected accounts
* graph evidence
* timeline context
* suggested next investigation steps

This makes the platform useful for real analysts who need defensible evidence, not just model predictions.

---

## 6. Account Intelligence Profiles

Every account has a dedicated intelligence profile.

It includes:

* account risk score
* risk history
* incoming and outgoing transaction value
* top senders and receivers
* account age
* unique counterparties
* average fund holding time
* graph centrality score
* detected patterns
* linked alerts
* suspicious transaction timeline
* connected high-risk accounts

---

## 7. Investigation Case Builder

Alerts can be converted into structured investigation cases.

Each case includes:

* case number
* title and severity
* primary suspicious account
* linked alerts
* transaction evidence
* connected accounts
* graph findings
* evidence timeline
* analyst notes
* case status
* generated report draft

Case statuses:

```text
Open
Under Review
Escalated
Closed
```

---

## 8. AI Investigation Copilot

The AI copilot helps investigators understand complex cases.

Example questions:

```text
Why is this account high risk?
Show suspicious outgoing routes.
Which accounts are part of this mule network?
Summarize the suspicious money movement.
What evidence supports this investigation?
```

The copilot is intentionally constrained.

It:

* only receives verified structured evidence
* cannot access arbitrary files or raw uploads
* cannot execute shell commands
* cannot modify database records
* cannot make legal conclusions
* cannot invent transactions or evidence
* cites evidence IDs and transaction references where possible

If no LLM API key is configured, TrailGuard uses deterministic investigation summaries.

---

## 9. Synthetic Fraud Scenario Simulator

For live demos and testing, TrailGuard includes a synthetic scenario injector.

Available scenarios:

```text
Inject Mule Ring
Inject Layering Chain
Inject Circular Flow
Inject Structuring Activity
Inject Rapid Pass-Through Account
```

Injected scenarios are persisted, analysed, and reflected in alerts and graph visualizations.

---

## 10. Investigation Report Generator

TrailGuard generates printable and exportable investigation report drafts.

Reports include:

* case overview
* risk score
* reason codes
* involved accounts
* suspicious transaction timeline
* graph findings
* detected fraud patterns
* evidence list
* analyst notes
* AI or deterministic summary
* limitations and disclaimer

Every generated report includes:

```text
Synthetic Demonstration Only — Human Review Required
```

---

# System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                       Next.js Frontend                      │
│ Dashboard · Alerts · Graph · Cases · Reports · Copilot      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ REST API / WebSocket
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                       FastAPI Backend                        │
│ Auth · Upload · Analysis · Graph · Cases · Reports · APIs   │
└───────────────┬──────────────────────┬──────────────────────┘
                │                      │
                │                      │
┌───────────────▼────────────┐  ┌──────▼─────────────────────┐
│ PostgreSQL / SQLite         │  │ Detection & Graph Engine   │
│ Users                       │  │ Isolation Forest           │
│ Datasets                    │  │ Rule-Based AML Detection   │
│ Accounts                    │  │ NetworkX Graph Analytics   │
│ Transactions                │  │ Temporal Risk Analysis     │
│ Alerts                      │  │ Evidence Generator         │
│ Cases                       │  └────────────────────────────┘
│ Audit Events                │
└────────────────────────────┘
```

---

# Technology Stack

## Frontend

* Next.js
* TypeScript
* Tailwind CSS
* shadcn/ui
* TanStack Query
* React Hook Form
* Zod
* React Force Graph or Sigma.js
* Recharts
* Lucide Icons

## Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* Alembic
* PostgreSQL / SQLite
* Pandas or Polars
* NetworkX
* scikit-learn
* Isolation Forest
* Redis and background workers where needed

---

# Application Workflow

```text
1. User logs into TrailGuard
        ↓
2. User uploads CSV or XLSX transaction data
        ↓
3. Backend validates, normalizes, and stores records
        ↓
4. Risk engine runs anomaly detection and rule checks
        ↓
5. Graph engine maps account relationships and fund movement
        ↓
6. Alerts are generated for suspicious accounts and transactions
        ↓
7. Investigator opens a high-risk alert
        ↓
8. Investigator traces source and destination paths
        ↓
9. Investigator creates a case
        ↓
10. TrailGuard builds an evidence timeline and report draft
```

---

# Detection Architecture

## Anomaly Detection

TrailGuard uses Isolation Forest when enough data is available.

For smaller datasets, TrailGuard uses robust statistical heuristics rather than pretending a model has high confidence.

---

## Rule-Based Detection

Known suspicious patterns are detected through transparent rules.

Example mule-account logic:

```text
Mule Risk =
Incoming Sender Diversity
+ Rapid Forwarding Ratio
+ Outgoing Recipient Diversity
+ Short Holding Time
+ New Account Risk
+ Graph Centrality Risk
```

---

## Graph Intelligence

Transactions are modelled as a directed graph.

TrailGuard calculates:

* in-degree and out-degree
* weighted transaction volume
* PageRank
* betweenness centrality
* connected components
* suspicious clusters
* directed cycles
* shortest paths

These metrics help identify intermediary accounts and high-influence nodes in suspicious financial networks.

---

# API Overview

All APIs are versioned under:

```text
/api/v1/
```

Key endpoints:

```text
POST   /auth/login
POST   /auth/logout
GET    /auth/me

POST   /datasets/upload
GET    /datasets
POST   /datasets/{id}/analyze

GET    /alerts
GET    /alerts/{id}

GET    /accounts/{id}
GET    /accounts/{id}/risk
GET    /accounts/{id}/graph

GET    /graph/explore
POST   /graph/trace-source
POST   /graph/trace-destination

GET    /cases
POST   /cases
GET    /cases/{id}
PATCH  /cases/{id}

POST   /demo/inject-scenario
```

---

# Security Model

TrailGuard is built as a security-conscious prototype.

## Authentication and Access Control

* role-based access control
* analyst and admin roles
* password hashing using Argon2 or bcrypt
* protected API routes
* short-lived access tokens

## AI Safety

* AI is optional
* AI summaries use verified evidence only
* no raw user files sent directly into prompts
* schema-validated structured outputs
* no autonomous database mutation

---

# Demo Dataset

TrailGuard ships with deterministic synthetic transaction data.

Included scenarios:

| Scenario             | Purpose                                                        |
| -------------------- | -------------------------------------------------------------- |
| Mule Ring            | Multiple incoming sources followed by rapid outgoing transfers |
| Layering Chain       | Multi-hop transfers designed to obscure source                 |
| Circular Flow        | Funds loop back to an earlier account                          |
| Structuring          | Repeated smaller transfers below a configured threshold        |
| New Account Velocity | Recently created account rapidly moving high value             |
| Normal Baseline      | Regular low-risk transactions for comparison                   |

---

# Getting Started

## Prerequisites

* Node.js 18+
* Python 3.12+

---

## Run Locally Without Docker

### Backend

```bash
cd services/api
python -m venv .venv
# On Windows: .venv\Scripts\activate
# On Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd apps/web
npm install
npm run dev
```

---

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

---

# Limitations

TrailGuard is a hackathon-grade prototype.

Current limitations may include:

* synthetic data only
* no real banking integration
* no regulatory filing integration
* anomaly quality depends on data quality and volume
* risk scores are investigation indicators, not legal conclusions
* LLM summaries must always be reviewed by a human investigator

---

# Responsible Use

TrailGuard should be used only as an investigation support tool.

It must not be used to:

* automatically label individuals as criminals
* deny financial access without human review
* make legal conclusions

---

# License

MIT License

---

## TrailGuard

> **Most systems tell investigators that something looks suspicious.
> TrailGuard shows them why, where the money came from, where it went next, and what evidence supports the case.**
