# TrailGuard AI — Product Requirements Document

## 1. Problem Statement

Financial crime — including money laundering, mule-account networks, and layered structuring — costs the global economy an estimated 2–5% of GDP annually. Investigators at financial institutions face three core challenges:

- **Data Overload**: Thousands of daily alerts from rule-based AML systems, most false positives.
- **Fragmented Tooling**: Analysis spread across spreadsheets, SQL queries, and legacy case management systems with no unified view.
- **Explainability Gap**: Black-box ML scores that cannot be justified to regulators or used in court.

TrailGuard AI solves these problems by providing an **explainable, graph-based financial crime investigation platform** that makes money trails visible, traceable, and report-ready.

## 2. Target Users

### Financial Crime Analyst
- Reviews alerts and suspicious activity reports
- Traces transaction flows across accounts
- Needs clear evidence for regulatory filings

### Investigator
- Conducts deep-dive investigations into complex networks
- Builds cases linking multiple accounts and transactions
- Generates case reports for law enforcement referrals

### Supervisor / Admin
- Reviews case quality and completeness
- Manages team workload and case assignments
- Configures detection rules and thresholds

## 3. Core User Flow

```
Load Data → Run Analysis → Review Alerts → Investigate Accounts →
  Trace Money Flow → Build Case → Generate Report
```

1. **Load Data**: Import synthetic or real transaction datasets
2. **Run Analysis**: Execute detection engine across loaded data
3. **Review Alerts**: Examine detected patterns (structuring, mule rings, rapid movement)
4. **Investigate Accounts**: Open detailed account intelligence profiles
5. **Trace Money Flow**: Use interactive graph to follow fund movement
6. **Build Case**: Collect evidence into structured investigation
7. **Generate Report**: Export investigator-ready case report

## 4. Must-Have Features

| # | Feature | Description | Priority |
|---|---------|-------------|----------|
| 1 | Transaction Ingestion | Load transaction CSV files with schema validation | P0 |
| 2 | Anomaly Detection Engine | Determine detection of structuring, mule rings, rapid movement | P0 |
| 3 | Explainable Reason Codes | Every alert includes human-readable why explanation | P0 |
| 4 | Account Intelligence Hub | Single-page view of account risk, history, network | P0 |
| 5 | Interactive Money Flow Graph | D3/Force-directed graph for tracing fund movement | P0 |
| 6 | Mule Ring Detection | Identify interconnected accounts with layered movement | P0 |
| 7 | Case Management | Create, update, close investigations with evidence | P0 |
| 8 | Evidence Timeline | Chronological view of all evidence attached to a case | P0 |
| 9 | Case Report Generation | Downloadable PDF/JSON case report | P1 |
| 10 | Authentication & RBAC | Login with role-based access control | P1 |

## 5. Success Metrics

- **Detection Accuracy**: < 20% false positive rate on synthetic benchmarks
- **Investigation Speed**: Time from alert to case report under 5 minutes for standard patterns
- **Explainability**: 100% of alerts have at least one reason code with specific transaction references
- **Case Quality**: All generated reports include account details, transaction list, evidence timeline, and reason codes
- **User Adoption**: Demo-ready with synthetic data in under 60 seconds from first load
