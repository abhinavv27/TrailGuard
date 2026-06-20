# TrailGuard AI — Architecture Decision Records

> This document records key architectural decisions made during the build of TrailGuard AI. Each decision includes context, options considered, and rationale.

---

## Stack Decisions

**Decision:** FastAPI + Next.js + SQLite + NetworkX
**Context:** Spec required no-Docker setup with simple local dev. SQLite eliminates database server dependency.
**Options considered:** FastAPI vs Flask (FastAPI chosen for async, Pydantic integration, auto-docs). PostgreSQL vs SQLite (SQLite chosen per No-Docker spec). React vs Next.js (Next.js chosen for file-based routing, API proxying, SSR).
**Rationale:** FastAPI provides best-in-class Python API development with automatic OpenAPI docs. SQLite enables zero-infrastructure local development. Next.js provides clean frontend architecture with built-in API proxy in dev.

## Database Design

**Decision:** SQLite via SQLAlchemy 2.x with Alembic migrations. String(36) UUIDs for all primary keys.
**Context:** SQLite doesn't support PostgreSQL native UUID types. All IDs use Python-generated uuid4 hex strings.
**Rationale:** String(36) UUIDs ensure portability across databases. Alembic handles schema migrations. Foreign keys are enforced at the application level via SQLAlchemy relationships.
**Core tables:** users, datasets, accounts, transactions, analysis_runs, account_risk_assessments, transaction_risk_assessments, detection_events, graph_metrics, investigation_cases, case_evidence, case_notes, audit_events.

## Detection Engine Architecture

**Decision:** Modular detector system with unified RiskEngine orchestrator.
**Context:** Each AML pattern has a dedicated detector class inheriting from BaseDetector. The RiskEngine collects results from all detectors and produces composite scores.
**Weighting:** 25% mule, 15% layering, 10% cycle, 10% structuring, 10% velocity, 15% anomaly, 15% counterparty.
**Rationale:** Modular design allows independent testing of each pattern. Deterministic scoring ensures reproducibility and auditability. sklearn Isolation Forest used conditionally for anomaly detection with z-score fallback.

## Frontend Architecture

**Decision:** Next.js 15 App Router, Tailwind CSS, TanStack Query, Recharts, React Force Graph.
**Context:** Dark navy/charcoal theme with electric cyan accents. Desktop-first financial intelligence command center aesthetic.
**Component structure:** Shared UI primitives (Button, Card, Badge, Table, Modal) in components/ui/. Domain components in components/{domain}/. Pages use App Router file conventions.
**Rationale:** TanStack Query provides clean API state management. React Force Graph enables interactive network visualization. shadcn/ui design patterns ensure consistency.

## Security Approach

**Decision:** Defense-in-depth with multiple layers.
**Auth:** SHA-256 + salt password hashing (bcrypt in production), JWT with configurable expiry, RBAC (admin/analyst).
**API:** CORS from env, ORM parameterization prevents SQL injection, Pydantic input validation, no stack traces in production.
**Files:** CSV/XLSX only validation, size limits, server-side filename generation, formula injection prevention.
**LLM:** Optional and sandboxed — only structured evidence passed, never raw CSV. Deterministic fallback when LLM unavailable.
