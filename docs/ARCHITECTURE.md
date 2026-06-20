# TrailGuard AI — Architecture Document

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                    Next.js 14 (App Router)                              │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐ │ │
│  │  │Dashboard │ │  Alert   │ │ Account  │ │  Graph   │ │   Reports    │ │ │
│  │  │  Page    │ │  Review  │ │Intellig. │ │ Visual. │ │   Builder    │ │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────────┘ │ │
│  │                                                                         │ │
│  │  ┌────────────────────────────────────────────────────────────────────┐ │ │
│  │  │              API Client (lib/api.ts)                               │ │ │
│  │  └────────────────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────────────────────┘
                           │ HTTP / JSON
                           │
┌──────────────────────────▼──────────────────────────────────────────────────┐
│                           API LAYER                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                    FastAPI (Python 3.12)                                │ │
│  │                                                                         │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐ │ │
│  │  │  Auth    │ │ Account  │ │  Alert   │ │  Graph   │ │   Dataset    │ │ │
│  │  │ Routes   │ │ Routes   │ │ Routes   │ │ Routes   │ │   Routes     │ │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────────┘ │ │
│  │                                                                         │ │
│  │  ┌────────────────────────────────────────────────────────────────────┐ │ │
│  │  │                    Service Layer                                   │ │ │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │ │ │
│  │  │  │   Auth   │ │ Dataset  │ │  Case    │ │  Report  │           │ │ │
│  │  │  │ Service  │ │ Service  │ │ Service  │ │ Service  │           │ │ │
│  │  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │ │ │
│  │  └────────────────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼───────┐  ┌──────▼───────┐  ┌───────▼───────┐
│  Detection     │  │   Graph     │  │   Report      │
│   Engine       │  │   Analysis  │  │   Generator   │
│                │  │             │  │               │
│ • Structuring  │  │ • NetworkX  │  │ • PDF Export  │
│ • Mule Rings   │  │ • Subgraphs │  │ • JSON Export │
│ • Rapid Mov't  │  │ • Centrality│  │ • Evidence    │
│ • Reason Codes │  │ • Paths     │  │ • Timeline    │
└───────┬───────┘  └──────┬───────┘  └───────┬───────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────────────┐
│                           DATA LAYER                                        │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                    PostgreSQL 16                                        │ │
│  │                                                                         │ │
│  │  accounts │ transactions │ detection_events │ analysis_runs             │ │
│  │  investigations │ risk_assessments │ audit_events │ users │ datasets   │ │
│  │                                                                         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                    Synthetic Data Store (CSV)                           │ │
│  │                    data/synthetic/                                      │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Descriptions

### Frontend (Next.js 14)

| Component | Responsibility |
|-----------|---------------|
| Dashboard | Overview metrics, recent alerts, system status |
| AlertReview | List/detail views of detected patterns with reason codes |
| AccountIntelligence | Single-account summary with risk score, transaction history, network |
| MoneyFlowGraph | Interactive D3 force-directed graph for fund tracing |
| CaseManagement | Create/edit/view investigations with evidence attachment |
| ReportBuilder | Generate and download case reports |
| DatasetManager | Upload, validate, and select transaction datasets |

### Backend (FastAPI)

| Component | Responsibility |
|-----------|---------------|
| Auth Routes | Login, token refresh, user management |
| Account Routes | Account CRUD, intelligence data |
| Alert Routes | Detection event listing, filtering, detail |
| Graph Routes | Graph data for visualization, path tracing |
| Dataset Routes | Upload, validate, list datasets |
| Investigation Routes | Case CRUD, evidence management |
| Report Routes | Generate and download case reports |
| Detection Engine | Run detection rules, generate alerts with reason codes |
| Graph Analyzer | NetworkX-based graph analysis, mule ring detection |
| Report Generator | Assemble case data into PDF/JSON output |

## Data Flow

### Detection Pipeline

```
Transaction Data
      │
      ▼
┌─────────────────┐
│ Data Ingestion   │  CSV → Validate → Store in PostgreSQL
│ (Dataset Service)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Detection Engine │  Load transactions → Run rules → Score patterns
│                  │
│ 1. Structuring   │  Multiple deposits near threshold in time window
│ 2. Mule Ring     │  Layered transactions through interconnected accounts
│ 3. Rapid Mov't   │  Funds in-and-out within short time window
│ 4. Risk Scoring  │  Aggregate score from pattern matches
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Alert Generation │  Create detection_event records with reason codes
│ + Reason Codes   │  "ACCT-123 received 3 deposits of $9,950 within 24h"
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Graph Analysis   │  Build NetworkX graph → detect interconnected rings
│                  │  → calculate centrality → identify mule clusters
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Account Risk     │  Update risk scores based on detection events
│ Assessment      │  Store risk assessment history
└─────────────────┘
```

## Security Boundaries

```
┌─────────────────────────────────────────────────────┐
│  PUBLIC / UNAUTHENTICATED                            │
│  • Login page                                        │
│  • Health check endpoint                             │
└───────────────────────┬─────────────────────────────┘
                        │ JWT Auth Middleware
┌───────────────────────▼─────────────────────────────┐
│  AUTHENTICATED                                       │
│  • All API routes (except login, health)             │
│  • Frontend pages                                    │
│  • Report downloads                                  │
└───────────────────────┬─────────────────────────────┘
                        │ RBAC Check
┌───────────────────────▼─────────────────────────────┐
│  ROLE-BASED ACCESS                                   │
│  Analyst: View alerts, accounts, reports             │
│  Investigator: All Analyst + create cases, trace     │
│  Admin: All Investigator + manage users, config     │
└─────────────────────────────────────────────────────┘
```

## Key Design Decisions

1. **Deterministic over ML**: Rule-based detection patterns provide 100% explainability. Every alert has traceable reason codes referencing specific transactions and thresholds.

2. **In-process Graph Analysis**: NetworkX runs in the same process as FastAPI. For the scale of synthetic data (thousands of transactions), this is sufficient. A future version could add Memgraph/Neo4j for larger datasets.

3. **Monorepo with Docker Compose**: Single repository simplifies development. Docker Compose ensures consistent environment across machines.

4. **Synthetic Data First**: Built for demo and evaluation with realistic synthetic data. Real deployment would connect to actual banking data sources.

5. **Stateless API**: JWT-based auth with no server-side session storage. Simplifies scaling and deployment.
