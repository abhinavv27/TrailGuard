# TrailGuard AI — Demo Script

## Flow Overview

This demo takes approximately **5–7 minutes** and walks through the complete TrailGuard AI workflow from data ingestion to case report generation.

---

### Step 1: Open TrailGuard AI Command Center

Navigate to `http://localhost:3000` and log in with the demo credentials provided in the setup. The **Command Center (Dashboard)** displays:

- System status
- Recent alert summary
- Quick actions: Load Dataset, Run Analysis, View Alerts

### Step 2: Load a Synthetic Dataset

Click **"Load Dataset"** on the dashboard. Select one of the pre-built synthetic datasets:
- `small_fraud_patterns.csv` — Quick demo with targeted patterns
- `medium_mule_network.csv` — Full network demonstration

The system validates the CSV schema and loads transactions into the database. A confirmation message shows record count and data range.

### Step 3: Run Analysis

Click **"Run Analysis"** to execute the detection engine across the loaded dataset. The analysis runs in seconds and covers:

- Structuring detection (multiple deposits under reporting threshold)
- Mule ring identification (layered transaction networks)
- Rapid movement detection (quick in-and-out patterns)
- Account risk scoring

A progress indicator shows the analysis stages. When complete, the dashboard alert counter updates.

### Step 4: Show Critical Mule Ring Alert

Navigate to **Alerts**. The list is sorted by severity. The top alert reads:

> **Critical**: Mule Ring Detected — 12 accounts, 47 transactions, ~$340,000 layered

Highlight the severity badge (Critical/High/Medium/Low) and the alert summary. Click to open details.

### Step 5: Open an Account Intelligence Profile

From the alert detail, click on the highest-risk account. The **Account Intelligence Hub** opens with:

- **Risk Score**: Numerical score with color indicator (red = high risk)
- **Transaction History**: Chronological list of all transactions
- **Network Connections**: Mini-graph showing linked accounts
- **Alert History**: All detection events involving this account

### Step 6: Explain Reason Codes

Scroll to the **Reason Codes** section on the account page. Each detection event includes:

- **Pattern Name**: e.g., "Structuring Pattern"
- **Specific Evidence**: "Account ACCT-123 received 3 deposits of $9,950 within 24 hours (threshold: $10,000)"
- **Transaction References**: Direct links to the specific transactions
- **Confidence Level**: High / Medium / Low based on pattern match strength

### Step 7: Enter Mule Money Trail Mode

Click **"Trace Money Flow"** on the account page. This opens the interactive **Money Flow Graph**:

- Accounts are nodes (sized by transaction volume, colored by risk)
- Transactions are edges (arrow direction shows money flow)
- Controls for zoom, pan, and filter by amount/date

### Step 8: Trace Victims → Mule → Exits

Use the graph to trace a complete money trail:

1. **Click a victim account** (inbound deposits from external sources)
2. **Follow edges** to intermediate mule accounts (rapid in-out pattern)
3. **Continue tracing** to exit accounts (funds consolidated and sent out of network)

Highlight the layer-jumping pattern that defines mule networks. Use the **Path Highlight** feature to automatically trace the complete flow from entry to exit.

### Step 9: Create an Investigation Case

Click **"Create Case"** from the alert or account page. The case form includes:

- **Case Title**: Auto-generated from alert type (editable)
- **Severity**: Pre-populated from alert
- **Description**: Free-text for investigator notes
- **Linked Accounts**: Auto-attached from the alert's involved accounts
- **Evidence Items**: Select specific transactions and detection events

Set status to **Draft** or **Open** and save.

### Step 10: Show Evidence Timeline

Open the created case and navigate to the **Evidence Timeline** tab. This shows:

- Chronological view of all evidence attached to the case
- Each item shows: date, type (transaction/alert/note), description
- Items are filterable by type and date range
- New evidence can be added from the timeline

### Step 11: Generate a Case Report

Click **"Generate Report"** in the case page. Select output format:

- **PDF**: Formatted document suitable for regulatory filing or law enforcement referral
- **JSON**: Machine-readable export for system integration

The report includes:
- Case summary
- Account details (all linked accounts with risk scores)
- Complete transaction list
- Detection event details with reason codes
- Evidence timeline
- Narratives generated (if LLM is configured)

Click **Download**.

### Step 12: Closing Statement

> "TrailGuard AI transforms complex financial crime investigation from a manual, fragmented process into an explainable, graph-driven workflow. What you've seen today — from data ingestion to actionable case report — represents hours of manual work compressed into minutes, with every finding backed by transparent reason codes that investigators and regulators can trust. TrailGuard AI: Making money trails visible."

---

## Demo Environment

- **URL**: http://localhost:3000
- **Demo User**: `demo@trailguard.ai` / `demo123`
- **Dataset**: `data/synthetic/medium_mule_network.csv`
