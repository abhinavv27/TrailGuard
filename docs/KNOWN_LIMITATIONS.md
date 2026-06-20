# TrailGuard AI — Known Limitations

## 1. Demo / Synthetic Data Only

TrailGuard AI ships with synthetic transaction data generators. The platform is designed for **demonstration and evaluation purposes**. It is not pre-configured to connect to live banking systems, core banking APIs, or SWIFT/ISO 20022 data feeds.

- Real-world deployment requires custom data ingestion adapters
- Synthetic data patterns may not reflect real criminal behavior complexity

## 2. Not a Replacement for Real Financial Investigation

TrailGuard AI is an **investigative aid**, not a replacement for professional financial crime analysis. The platform:

- Does not automatically file SARs (Suspicious Activity Reports)
- Does not guarantee detection of all financial crime patterns
- Should not be the sole basis for legal or regulatory decisions
- Requires human review and judgment for all alerts

## 3. LLM Features Are Optional and Behind API Key

Any LLM-powered features (e.g., narrative report generation) are entirely optional:

- Require a valid third-party API key (OpenAI, Anthropic, etc.)
- Are not required for core detection or investigation workflows
- May incur API costs based on usage
- LLM output quality varies and should always be reviewed by a human

## 4. Deterministic Detection (Not ML-Based)

The detection engine uses **rule-based, deterministic algorithms**:

- Pattern matching against defined thresholds
- Graph-theoretic analysis (NetworkX) for relationship detection
- No machine learning models are trained or deployed

This means:
- Detection is fully explainable (every alert has traceable reason codes)
- Detection rules require manual tuning for different environments
- Novel or highly sophisticated patterns may not be caught
- False positive rates depend on threshold configuration

## 5. Single-Region Deployment by Default

The default Docker Compose configuration is designed for **single-region, single-instance deployment**:

- No built-in horizontal scaling (multiple API replicas require additional configuration)
- No cross-region replication for PostgreSQL
- No built-in load balancing
- Session persistence not configured (JWT-based auth mitigates this)

For production multi-region deployment, additional infrastructure (reverse proxy, read replicas, CDN) would be required.
