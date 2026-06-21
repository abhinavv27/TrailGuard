"""Ground-truth calibration test for the detection engine.

Runs the full engine over the synthetic dataset (which has named, labelled
fraud scenarios) and asserts that planted fraud surfaces as alerts while the
normal high-volume background accounts do not. This locks in the calibration
fixes: dataset reference-time anchoring, whole-graph layering/cycle, the
funnel-aware mule signal, the burst-aware velocity, and the blended scoring.
"""
import csv
import os

import pytest

from app.detection.engine import RiskEngine

CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "data",
    "synthetic",
    "sample_transactions.csv",
)


def _load_transactions():
    rows = []
    with open(CSV_PATH, newline="") as f:
        for i, row in enumerate(csv.DictReader(f)):
            rows.append(
                {
                    "id": row.get("transaction_id", f"tx{i}"),
                    "amount": float(row.get("amount", 0) or 0),
                    "timestamp": row.get("timestamp", ""),
                    "sender_account_id": row.get("sender_account_id", ""),
                    "receiver_account_id": row.get("receiver_account_id", ""),
                    "currency": row.get("currency", "USD"),
                    "channel": row.get("channel", "online"),
                }
            )
    return rows


def _score_all():
    txs = _load_transactions()
    by_account = {}
    for t in txs:
        for acct in (t["sender_account_id"], t["receiver_account_id"]):
            if acct:
                by_account.setdefault(acct, [])
        s, r = t["sender_account_id"], t["receiver_account_id"]
        if s:
            by_account[s].append(t)
        if r and r != s:
            by_account[r].append(t)

    engine = RiskEngine()
    engine.prepare_dataset(txs)
    return {
        acct: engine.analyze_account(acct, acct_txs)
        for acct, acct_txs in by_account.items()
    }


@pytest.fixture(scope="module")
def scores():
    if not os.path.exists(CSV_PATH):
        pytest.skip("synthetic dataset not present")
    return _score_all()


def _alerts(scores):
    return {a for a, r in scores.items() if r.risk_level in ("HIGH", "CRITICAL")}


def test_mule_account_is_critical(scores):
    assert scores["MULE-AX7"].risk_level == "CRITICAL"


def test_cycle_accounts_alert(scores):
    for acct in ("CYCLE-A", "CYCLE-B", "CYCLE-C"):
        assert scores[acct].risk_level in ("HIGH", "CRITICAL"), acct


def test_structuring_account_alerts(scores):
    assert scores["STRUCT-01"].risk_level in ("HIGH", "CRITICAL")


def test_layering_conduits_alert(scores):
    # The pass-through conduits in the chain LAYER-A->B->C->D->EXIT-L.
    for acct in ("LAYER-B", "LAYER-C", "LAYER-D"):
        assert scores[acct].risk_level in ("HIGH", "CRITICAL"), acct


def test_no_normal_account_alerts(scores):
    # Normal high-volume background accounts (ACC-*) must not generate alerts.
    offenders = [a for a in _alerts(scores) if a.startswith("ACC")]
    assert offenders == [], f"normal accounts wrongly alerted: {offenders}"


def test_fraud_outranks_normal(scores):
    top_normal = max(
        scores[a].risk_score for a in scores if a.startswith("ACC")
    )
    planted = ["MULE-AX7", "CYCLE-A", "STRUCT-01", "LAYER-B"]
    for acct in planted:
        assert scores[acct].risk_score > top_normal, (
            f"{acct} ({scores[acct].risk_score}) should outrank top normal "
            f"account ({top_normal})"
        )
