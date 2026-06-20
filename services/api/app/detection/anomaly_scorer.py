"""Statistical anomaly scorer using Isolation Forest or robust z-score."""
import logging
import math
import sys
from datetime import datetime
from statistics import median, stdev
from typing import Any, Dict, List, Optional

from app.detection.base_detector import BaseDetector

logger = logging.getLogger(__name__)

SKLEARN_AVAILABLE = False
IsolationForest = None

def _check_sklearn():
    global SKLEARN_AVAILABLE, IsolationForest
    if SKLEARN_AVAILABLE or IsolationForest is not None:
        return SKLEARN_AVAILABLE
    try:
        from sklearn.ensemble import IsolationForest as _IF
        IsolationForest = _IF
        SKLEARN_AVAILABLE = True
    except ImportError:
        logger.warning("sklearn not available; falling back to z-score only")
    return SKLEARN_AVAILABLE


class AnomalyScorer(BaseDetector):
    """
    Statistical anomaly detection:
    - Uses Isolation Forest for datasets >= 100 transactions
    - Falls back to robust z-score for smaller datasets
    """

    version = "1.3.0"

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.if_contamination = self.config.get("if_contamination", 0.1)
        self.z_score_threshold = self.config.get("z_score_threshold", 2.5)
        self.min_for_isolation_forest = self.config.get(
            "min_for_isolation_forest", 100
        )

    def analyze(
        self,
        account_id: str,
        transactions: List[Dict],
        db_session=None,
    ) -> Optional[Dict]:
        if not transactions or len(transactions) < 5:
            return None

        amounts = [tx.get("amount", 0) for tx in transactions]
        log_amounts = [
            math.log(max(a, 0.01)) for a in amounts
        ]

        sender_counts = self._count_by_key(
            transactions, "sender_account_id"
        )
        receiver_counts = self._count_by_key(
            transactions, "receiver_account_id"
        )

        sender_velocities = [
            sender_counts.get(tx.get("sender_account_id", ""), 0)
            for tx in transactions
        ]
        receiver_velocities = [
            receiver_counts.get(tx.get("receiver_account_id", ""), 0)
            for tx in transactions
        ]

        unique_counterparties = set()
        for tx in transactions:
            unique_counterparties.add(tx.get("sender_account_id", ""))
            unique_counterparties.add(tx.get("receiver_account_id", ""))
        counterparty_count = len(unique_counterparties)

        mean_amt = sum(amounts) / len(amounts)
        if mean_amt > 0:
            amount_zscores = [
                (a - mean_amt) / max(stdev(amounts), 0.01)
                for a in amounts
            ]
        else:
            amount_zscores = [0] * len(amounts)

        features = []
        for i in range(len(transactions)):
            features.append(
                [
                    log_amounts[i],
                    amount_zscores[i],
                    sender_velocities[i],
                    receiver_velocities[i],
                    counterparty_count / max(len(transactions), 1),
                ]
            )

        num_samples = len(transactions)
        use_if = (
            _check_sklearn()
            and num_samples >= self.min_for_isolation_forest
        )

        anomaly_scores = []
        if use_if:
            try:
                model = IsolationForest(
                    contamination=self.if_contamination,
                    random_state=42,
                    n_estimators=100,
                )
                predictions = model.fit_predict(features)
                anomaly_scores = [
                    1 if p == -1 else 0 for p in predictions
                ]
                confidence = "high"
            except Exception as e:
                logger.error(f"Isolation Forest failed: {e}")
                use_if = False

        if not use_if:
            anomaly_scores = [
                1 if abs(z) > self.z_score_threshold else 0
                for z in amount_zscores
            ]
            confidence = "limited" if num_samples < 100 else "moderate"

        anomaly_count = sum(anomaly_scores)
        anomaly_ratio = anomaly_count / max(len(anomaly_scores), 1)
        score = min(anomaly_ratio * 1.5, 1.0)

        multi_dim_factor = 0
        if counterparty_count > 50:
            multi_dim_factor = 0.1
        score = min(score + multi_dim_factor, 1.0)

        reason_codes = []
        source_tx_ids = []

        if anomaly_count > 0:
            anomaly_tx_ids = [
                transactions[i].get("id", "")
                for i in range(len(anomaly_scores))
                if anomaly_scores[i] == 1
            ][:10]
            source_tx_ids.extend(anomaly_tx_ids)

            method = "Isolation Forest" if use_if else "Z-score"
            reason_codes.append(
                {
                    "code": "STATISTICAL_ANOMALY",
                    "description": f"Statistical anomaly detected ({anomaly_count} anomalous transactions, confidence: {confidence}).",
                    "severity": round(score, 2),
                    "source_transaction_ids": anomaly_tx_ids,
                }
            )

        return {
            "score": round(score, 4),
            "reason_codes": reason_codes,
            "source_transaction_ids": list(set(source_tx_ids)),
            "version": self.version,
        }

    def _count_by_key(
        self, transactions: List[Dict], key: str
    ) -> Dict[str, int]:
        counts = {}
        for tx in transactions:
            val = tx.get(key, "")
            if val:
                counts[val] = counts.get(val, 0) + 1
        return counts
